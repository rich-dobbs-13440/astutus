import logging
import re

import astutus.util

logger = logging.getLogger(__name__)


class DeviceNode(dict):
    """ Base class for particular device nodes """

    verbose = False

    def __init__(self, data, config, alias, cls_order):
        dirpath = data['dirpath']
        # Sanitize dirpath to an acceptable CSS selector:
        idx = dirpath.replace(':', '_C_')
        idx = idx.replace('.', '_P_')
        idx = idx.replace('/', '_S_')
        idx = idx.replace('-', '_D_')
        data['idx'] = idx
        assert dirpath is not None, data
        data['config_description'] = config.generate_description(dirpath, data)
        data['config_color'] = config.get_color()
        if alias is not None:
            data['alias_description_template'] = alias['description_template']
            data['alias_description'] = data['alias_description_template'].format_map(data)
            data['alias_color'] = alias['color']
            data['resolved_description'] = data['alias_description']
            data['resolved_color'] = data['alias_color']
        else:
            data['alias_description_template'] = ''
            data['alias_description'] = ''
            data['alias_color'] = ''
            data['resolved_description'] = data['config_description']
            data['resolved_color'] = data['config_color']

        self.node_color = 'pink'
        if alias is None:
            self.order = '50'
        else:
            self.order = alias['order']
        self.cls_order = cls_order

        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        color = data['resolved_color']
        colored_description = f"{start(color)}{data['resolved_description'] }{end(color)}"
        data['terminal_colored_description'] = colored_description
        data['terminal_colored_node_label_concise'] = f"{data['dirname']} - {colored_description}"
        colored_node_id = f"{start(self.node_color)}{data['node_id']}{end(self.node_color)}"
        data['terminal_colored_node_label_verbose'] = f"{data['dirname']} - {colored_node_id} - {colored_description}"
        dirname_span = f'<span class="dirname_class">{data["dirname"]}</span>'
        node_id_span = f'<span class="node_id_class">{data["node_id"]}</span>'
        description_span = f'<span style="color:{color}">{data["resolved_description"]}</span>'
        data['html_label_concise'] = f'{data["dirname"]} - {data["resolved_description"]}'
        data['html_label_verbose'] = f'{dirname_span} {node_id_span} {description_span}'

        self.data = data
        # Inititialize super to support JSON serialization.
        super(DeviceNode, self).__init__(data)

    def key(self):
        key_value = f"{self.cls_order} - {self.order} - {self.data['dirname']}"
        logger.debug(f"key_value: {key_value}")
        return key_value

    @property
    def colorized_node_label_for_terminal(self):
        if self.verbose:
            return self.data['terminal_colored_node_label_verbose']
        return self.data['terminal_colored_node_label_concise']


class PciDeviceNodeData(DeviceNode):

    cls_order = "10"

    @staticmethod
    def node_id_from_data(data):
        return f"pci({data.get('vendor', '-')}:{data.get('device', '-')})"

    @classmethod
    def extract_data(cls, dirpath):
        data = astutus.usb.usb_impl.extract_specified_data(dirpath, astutus.usb.usb_impl.PCI_KEY_ATTRIBUTES)
        data['node_id'] = cls.node_id_from_data(data)
        data['ilk'] = 'pci'
        return data

    def __init__(self, *, data, config, alias):
        # TODO:  "Use lspci to get description"
        assert data.get('dirpath') is not None, data
        data["description"] = 'use lspci'  # data['node_id']
        # logger.debug(f'alias: {alias}')
        super(PciDeviceNodeData, self).__init__(data, config, alias, self.cls_order)


class UsbDeviceNodeData(DeviceNode):

    cls_order = "00"

    @staticmethod
    def node_id_from_data(data):
        return f"usb({data['idVendor']}:{data['idProduct']})"

    @classmethod
    def extract_data(cls, dirpath):
        data = astutus.usb.usb_impl.extract_specified_data(dirpath, astutus.usb.usb_impl.USB_KEY_ATTRIBUTES)
        data['node_id'] = cls.node_id_from_data(data)
        data['ilk'] = 'usb'
        return data

    def __init__(self, *, data, config, alias):
        busnum = int(data['busnum'])
        devnum = int(data['devnum'])
        _, _, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
        data["description"] = description
        if config is not None and config.find_tty():
            tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
            data['tty'] = tty
        super(UsbDeviceNodeData, self).__init__(data, config, alias, self.cls_order)


def node_id_for_dirpath(dirpath):
    data = UsbDeviceNodeData.extract_data(dirpath)
    if data.get("busnum") is not None:
        return UsbDeviceNodeData.node_id_from_data(data)
    data = PciDeviceNodeData.extract_data('', dirpath)
    if data.get("device") is not None:
        return PciDeviceNodeData.node_id_from_data(data)
    return None


def parse_value(value):
    """ Given a value break it down by the ilk of node (usb or pci), the vendor, and the device or product."""
    value_pattern = r'^(usb|pci)\(([^:]{4}):([^:]{4})\)$'
    matches = re.match(value_pattern, value)
    assert matches, value
    ilk, vendor, device = matches.group(1), matches.group(2), matches.group(3)
    return ilk, vendor, device
