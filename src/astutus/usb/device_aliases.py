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

To do this, four axes are considered:

    * Current node axis
    * Ancestor axis
    * Child axis
    * Sibling axis

In looking at the tree there are two distinct ilk of nodes:

    * PCI nodes identified by **vendor** and **device**
    * USB noded identified by **idVendor** and **idProduct**

The nodes are identified as:

    * pci(*{vendor}*:*{device}*)
    * usb(*{idVendor}*:*{idProduct}*)

The axis checks are implemented using this pattern:

    [ *{axis}* *{operator}* *{node}* ]

A bare node is implicitly the current node axis and operator is implicitly
equality.

For ancestor, the equality operator means that some ancestor matches the equality
operator and specified node value.

For sibling or child, the equality operator means that some sibling or child
matches the equality operator and node value.

Here are some examples of validly formated selectors:

    * usb(1a86:7523)
    * [ancestor==usb(05e3:0610)]usb(1a86:7523)[sibling==usb(0bda:8153)]
    * [ancestor==pci(0x1002:0x5a19)]usb(1a86:7523)[child=usb(0bda:8153)]
    * [ancestor==pci(0x1002:0x5a19)]usb(1a86:7523)

This module contains two key public features:

    * The **find_pci_paths(selector)** function for use in automation.
    * The **DeviceAliases** class used by the **astutus-usb-tree** command.


"""
import json
import logging
import os
import re

import astutus.usb.usb_impl
import astutus.usb.node

logger = logging.getLogger(__name__)


def parse_selector(selector):
    """ Parse the selector into ancestor, current, sibling and child axes."""
    child_pattern = r'\[child(==|!=)([^\]]+)]'
    ancestor_pattern = r'\[ancestor(==|!=)([^\]]+)]'
    sibling_pattern = r'\[sibling(==|!=)([^\]]+)]'

    check_str = selector
    child_check = None
    if "[child" in check_str:
        logger.debug(f"child_pattern: {child_pattern}")
        matches = re.search(child_pattern, check_str)
        child_check = (matches.group(1), matches.group(2))
        # Remove the child axes from the check string
        check_str = re.sub(child_pattern, '', check_str, 0, re.MULTILINE)
    ancestor_check = None
    if "[ancestor" in check_str:
        matches = re.search(ancestor_pattern, check_str)
        ancestor_check = (matches.group(1), matches.group(2))
        # Remove the ancestor axes from the key
        check_str = re.sub(ancestor_pattern, '', check_str, 0, re.MULTILINE)
    sibling_check = None
    if "[sibling" in check_str:
        matches = re.search(sibling_pattern, check_str)
        sibling_check = (matches.group(1), matches.group(2))
        # Remove the ancestor axes from the key
        check_str = re.sub(sibling_pattern, '', check_str, 0, re.MULTILINE)
    # After removing the other axes, will be just left with the current key, which
    # implicitly has the equality operator.
    current_check = ('==', check_str)
    result = ancestor_check, current_check, child_check, sibling_check
    logger.info(f"Parsed selector to : {result}")
    return result


def matches_as_usb_node(dirpath, vendor, product):
    data = astutus.usb.usb_impl.extract_specified_data(dirpath, ['idVendor', 'idProduct'])
    if data.get('idVendor') == vendor and data.get('idProduct') == product:
        return True
    return False


def matches_as_pci_node(dirpath, vendor, device):
    data = astutus.usb.usb_impl.extract_specified_data('', dirpath, ['vendor', 'device'])
    if data.get('vendor') == vendor and data.get('device') == device:
        return True
    return False


def matches_as_node(dirpath, ilk, vendor, device):
    if ilk == "usb":
        if matches_as_usb_node(dirpath, vendor, device):
            return True
    elif ilk == "pci":
        if matches_as_pci_node(dirpath, vendor, device):
            return True
    else:
        raise NotImplementedError(ilk)
    return False


def find_all_pci_paths(value):
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


def find_node_paths(value):
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


def ancestor_passes(check, dirpath):
    """ Checks if any ancestor of a node matches the specified check. """
    logger.info(f"In ancestor_passes, with dirpath: {dirpath} and check {check}")
    if check is None:
        return True
    operator, value = check
    # Only implementing equality operator now.
    assert operator == "=="
    ilk, vendor, device = astutus.usb.node.parse_value(value)
    logger.debug(f"dirpath: {dirpath}")
    a_dirpath, current = dirpath.rsplit('/', 1)
    while a_dirpath != '/sys/devices':
        if matches_as_node(a_dirpath, ilk, vendor, device):
            logger.info(f"Match for ancestor: {a_dirpath}")
            return True
        a_dirpath, current = a_dirpath.rsplit('/', 1)
    logger.info(f"No match for any ancestor of: {dirpath}")
    return False


def child_passes(check, dirpath, skip_dirpaths=[]):
    """ Checks if any immediate child of a node matches the specified check. """
    # skip_dirpaths is for sibling checks, to avoid having current
    # being considered a sibling of itself
    logger.info(f"In child_passes, with dirpath: {dirpath} and check {check}")
    if check is None:
        return True
    operator, value = check
    # Only implementing equality operator now.
    assert operator == "=="
    ilk, vendor, device = astutus.usb.node.parse_value(value)
    root, dirs, _ = next(os.walk(dirpath))
    for dir in dirs:
        subdirpath = os.path.join(root, dir)
        if subdirpath in skip_dirpaths:
            logger.info(f"Skipping subdirpath: {subdirpath}")
            continue
        if matches_as_node(subdirpath, ilk, vendor, device):
            logger.info(f"Match for: {subdirpath}")
            return True
        logger.info(f"No match for: {subdirpath}")
    return False


def sibling_passes(check, dirpath):
    """ Checks if any immediate sibling of a node matches the specified check. """
    logger.info(f"In sibling_passes, with dirpath: {dirpath} and check {check}")
    if check is None:
        return True
    operator, value = check
    # Only implementing equality operator now.
    assert operator == "=="
    ilk, vendor, device = astutus.usb.node.parse_value(value)
    parent_dirpath, current = dirpath.rsplit('/', 1)
    logger.debug(f"parent_dirpath: {parent_dirpath}")
    if child_passes(check, parent_dirpath, skip_dirpaths=[dirpath]):
        logger.info(f"Passed check: {check}")
        return True
    logger.info(f"Didn't passed with check: {check}")
    return False


def find_pci_paths(selector):
    """ Find all paths in the sys/devices tree that matches a selector. """
    logger.info(f"In find_pci_paths with selector: {selector}")
    ancestor_check, current_check, child_check, sibling_check = parse_selector(selector)
    operator, value = current_check
    assert operator == "=="
    all_paths = find_all_pci_paths(value)
    filtered_paths = []
    for dirpath in all_paths:
        if not ancestor_passes(ancestor_check, dirpath):
            continue
        if not child_passes(child_check, dirpath):
            continue
        if not sibling_passes(sibling_check, dirpath):
            continue
        filtered_paths.append(dirpath)
    return filtered_paths


class DeviceAliases:
    """ The device aliases class provides a dictionary between selectors and aliases for a node.

    The aliases should have the following attributes:

        * "color"
        * "label"
        * "order"
        * "priority"

    Each of these attributes are string values.

    Color should be as defined in astutus.util.term_color.py.

    The order and priority values should be two character values, such as "44".

    Aliases with higher priority are selected over other potential aliases
    of lesser priority for a particular node.

    Order is used in sorting the nodes in the USB tree for display.

    Here is structure of the **old** raw aliases file:

    .. code-block:: json

        {
            "[ancestor==usb(05e3:0610)]usb(1a86:7523)[sibling==usb(0bda:8153)]": {
                "color": "fushia",
                "label": "SMAKIN Relay into TECKNET USB 2.0",
                "order": "40",
                "priority": 98
            },
        }

    """

    def __init__(self, *, filepath):
        logger.info("Initializing AliasPaths")
        raw_aliases = self.read_raw_from_json(filepath)
        self.aliases = self.parse_raw_aliases(raw_aliases)

    @staticmethod
    def write_raw_as_json(filepath, raw_aliases):
        with open(filepath, 'w') as aliases_file:
            json.dump(raw_aliases, aliases_file, indent=4, sort_keys=True)

    @staticmethod
    def read_raw_from_json(filepath):
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
    def parse_raw_aliases(raw_aliases):
        aliases = raw_aliases
        return aliases

    def get(self, nodepath):
        """ Get the alias of highest priority that matches the specified node.

        Note:  id is probably not needed, since dirpath should uniquely specify the
        node.  Opportunity for refactoring???
        """
        logger.debug(self.aliases.keys())
        value = self.aliases.get(nodepath)
        if value is None:
            return None
        else:
            # TODO:  Prioritize based on value. Or is this no longer needed
            return value[0]

    def label(self, name):
        """ Returns a simple label for the specified name.  Only checks the current axis for equality."""
        for checks in self.aliases.keys():
            ancestor_check, current_check, child_check = checks
            current_check_value = current_check[1]
            if ancestor_check is None and current_check_value == name and child_check is None:
                alias = self.aliases[checks]
                return alias['label']
        return None
