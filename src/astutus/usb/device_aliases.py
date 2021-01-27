"""

Device aliases allow the USB device tree to identify a node with a
label associated with the physical device.


This module provides the capabilities to identify particular
nodes for visualization as well as selection of nodes as
needed for device control.

The selectors implement here are influenced by XPath.

Conceptually, the directory hierarch for sys/devices could
be mapped into an XML document.  Then XPath could be directly
applied to this.  This approach might be used in a second
implementation of this system. But for know, the initial
implementation will be driven by the needs to identify
particular USB relays plugged into the current computer.


In looking at the tree there are two distinct ilk of nodes:

    * PCI nodes identified by **vendor** and **device**
    * USB noded identified by **idVendor** and **idProduct**

The nodes are identified as:

    * pci(*{vendor}*:*{device}*)
    * usb(*{idVendor}*:*{idProduct}*)

"""
import json
import logging
import os
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.usb.node
import astutus.usb.usb_impl

logger = logging.getLogger(__name__)


def matches_as_usb_node(dirpath: str, vendor: str, product: str) -> bool:
    data = astutus.usb.usb_impl.extract_specified_data(dirpath, ['idVendor', 'idProduct'])
    if data.get('idVendor') == vendor and data.get('idProduct') == product:
        return True
    return False


def matches_as_pci_node(dirpath: str, vendor: str, device: str) -> bool:
    data = astutus.usb.usb_impl.extract_specified_data('', dirpath, ['vendor', 'device'])
    if data.get('vendor') == vendor and data.get('device') == device:
        return True
    return False


def matches_as_node(dirpath: str, ilk: str, vendor: str, device: str) -> bool:
    if ilk == "usb":
        if matches_as_usb_node(dirpath, vendor, device):
            return True
    elif ilk == "pci":
        if matches_as_pci_node(dirpath, vendor, device):
            return True
    else:
        raise NotImplementedError(ilk)
    return False


def find_all_pci_paths(value: str) -> List[str]:
    """ Find all that terminate with a node that matches the value.

    The value is something like usb(1a86:7523) or pci(0x1002:0x5a19)
    """
    logger.info(f"In find_all_pci_paths with value: {value}")
    ilk, vendor, device = astutus.usb.node.parse_value(value)
    device_paths = []
    for dirpath, dirnames, filenames in os.walk('/sys/devices/pci0000:00'):
        if ilk == "usb" and "busnum" in filenames and "devnum" in filenames:
            if matches_as_node(dirpath, ilk, vendor, device):
                device_paths.append(dirpath)
        if ilk == "pci" and "vendor" in filenames and "device" in filenames:
            if matches_as_node(dirpath, ilk, vendor, device):
                device_paths.append(dirpath)
    return device_paths


def find_node_paths(value: str) -> List[str]:
    node_paths = []
    pci_paths = find_all_pci_paths(value)
    logger.debug(f"pci_paths {pci_paths}")
    for pci_path in pci_paths:
        pci_path += '/'
        logger.debug(f"pci_path {pci_path}")
        idx = 0
        node_ids = []
        while True:
            idx = pci_path.find('/', idx + 1)
            if idx < 0:
                break
            dirpath = pci_path[:idx]
            logger.debug(f"dirpath {dirpath}")
            node_id = astutus.usb.node.node_id_for_dirpath(dirpath)
            if node_id is not None:
                node_ids.append(node_id)
        node_paths.append("/".join(node_ids))
    logger.debug(f"node_paths {node_paths}")
    return node_paths


class DeviceAliases(dict):
    """ The device aliases class provides a dictionary between selectors and aliases for a node.

    The aliases should have the following attributes:

        * "color"
        * "label"
        * "order"
        * "priority"

    Each of these attributes are string values.

    Color should be as defined using css compatible color names or #rrggbb values.

    The order and priority values should be two character values, such as "44".

    Aliases with higher priority are selected over other potential aliases
    of lesser priority for a particular node.

    Order is used in sorting the nodes in the USB tree for display.

    Here is structure of the raw aliases file:

    .. code-block:: json

        {
        "pci(0x1002:0x5a19)/pci(0x1b21:0x1042)":
            {
                "name": "Come up with good name",
                "color": "#5a1ddd",
                "description_template": "ASM1042 Alias",
                "order": "00",
                "pattern": "pci(0x1002:0x5a19)/pci(0x1b21:0x1042)",
                "priority": 50
            },
        }

    """

    @staticmethod
    def write_raw_as_json(filepath: str, raw_aliases: Dict) -> None:
        if filepath is None:
            filepath = os.path.join(astutus.util.get_user_data_path(), 'device_aliases.json')
        with open(filepath, 'w') as aliases_file:
            json.dump(raw_aliases, aliases_file, indent=4, sort_keys=True)

    @staticmethod
    def read_raw_from_json(filepath: str) -> Dict:
        if filepath is None:
            filepath = os.path.join(astutus.util.get_user_data_path(), 'device_aliases.json')
            if not os.path.isfile(filepath):
                # If the file doesn't exist in the user's data dir,
                # Create an "empty" one.
                raw_aliases = {}
                DeviceAliases.write_raw_as_json(filepath, raw_aliases)
        with open(filepath, 'r') as aliases_file:
            raw_device_aliases = json.load(aliases_file)
        return raw_device_aliases

    @staticmethod
    def parse_raw_aliases(raw_aliases: Dict) -> Dict:
        aliases = {}
        for pattern, value in raw_aliases.items():
            alias = value
            logger.debug(f"alias: {alias}")
            alias['color'] = astutus.util.convert_color_for_html_input_type_color(alias['color'])
            alias['pattern'] = pattern
            aliases[pattern] = value
        return aliases

    def __init__(self, *, filepath: str):
        self.filepath = filepath
        logger.info("Initializing DeviceAliases")
        super(DeviceAliases, self).__init__()
        raw_aliases = self.read_raw_from_json(filepath)

        self.update(self.parse_raw_aliases(raw_aliases))

    def find(self, nodepath: str) -> [Dict]:
        """ Find all aliases that partially match the nodepath.  """
        logger.debug(f"nodepath: {nodepath}")
        if nodepath is None:
            assert False
        aliases = []
        for pattern, value in super().items():
            if nodepath.endswith(pattern):
                aliases.append(value)
        logger.debug(f"aliases: {aliases}")
        return aliases

    def find_highest_priority(self, nodepath: str) -> Dict:
        """ Find the alias with the highest priority."""
        aliases = self.find(nodepath)
        highest = None
        for alias in aliases:
            if highest is None:
                highest = alias
            else:
                if alias['priority'] > highest['priority']:
                    highest = alias
        return highest

    def get(self, pattern: str) -> Dict:
        """ Get the alias that exactly matches the pattern"""
        logger.debug(f'pattern: {pattern}')
        value = super().get(pattern)
        if value is None:
            alias = None
        else:
            alias = value
            alias['pattern'] = pattern
            alias['color'] = astutus.util.convert_color_for_html_input_type_color(alias['color'])
        logger.debug(f'alias: {alias}')
        return alias

    def write(self, filepath=None) -> None:
        """ Writes the aliases to filepath

        if filepath is None, then write to original path
        """
        if filepath is None:
            filepath = self.filepath
        self.write_raw_as_json(filepath=filepath, raw_aliases=self)

    def to_javascript(self) -> str:
        """ Provides the device aliases as a Javascript object with a small set of methods. """
        chunks = []
        chunks.append("<script>")
        chunks.append("var aliases = ")
        chunks.append(json.dumps(self, indent=4, sort_keys=True))

        chunks.append('''
        aliases.find = function(nodepath) {
            const keys = Object.keys(this);
            var matchingAliases = [];
            keys.forEach((pattern, index) => {
                if (nodepath.endsWith(pattern)) {
                   matchingAliases.push(this[pattern]);
                }
            });
            return matchingAliases;
        };
        aliases.findLongest = function(nodepath) {
            var longest_length = 0;
            var best = null;
            matchingAliases = this.find(nodepath);
            for (alias of matchingAliases) {
                if (alias['pattern'].length > longest_length) {
                    best = alias;
                    longest_length = alias['pattern'].length;
                };
            }
            return best;
        };

        ''')
        # Try it out
        chunks.append("console.log('aliases.find(): ', aliases.find('pci(0x1002:0x5a19)/pci(0x1b21:0x1042)/usb(1d6b:0002)'));")  # noqa
        chunks.append("console.log('aliases.findLongest(', aliases.findLongest('pci(0x1002:0x5a19)/pci(0x1b21:0x1042)/usb(1d6b:0002)'));")  # noqa
        chunks.append("</script>")
        return "\n".join(chunks)
