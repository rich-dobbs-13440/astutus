import logging
import re
import copy
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.util
import astutus.usb

logger = logging.getLogger(__name__)


extra_fields_for_ilk = {
    'usb': ['nodepath', 'vendor', 'product_text', 'device_class'],
    'pci': ['nodepath'],
}


def robust_format_map(template, data):
    data = copy.deepcopy(data)
    max_count = template.count('{')
    count = 0
    while True:
        try:
            value = template.format_map(data)
            return value
        except KeyError as exception:
            logger.error(f'exception: {exception}')
            data[exception.args[0]] = f"--{exception.args[0]} missing--"
            count += 1
            if count > max_count:
                # Just a double check to prevent infinite loop in case of coding error'
                return f'robust_format_map error. template: {template} - data: {data}'


class DeviceNode(dict):
    """ Base class for particular device nodes """

    verbose = False

    def __init__(
            self,
            data: Dict,
            cls_order: str):  # Should probably migrate cls order to be an int.
        dirpath = data['dirpath']
        assert dirpath is not None, data

        self.cls_order = cls_order
        device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)

        device_data = device_classifier.get_device_data(dirpath)
        extra_fields = extra_fields_for_ilk.get(device_data['ilk'])
        if extra_fields is not None:
            device_data = device_classifier.get_device_data(dirpath, extra_fields)
        label = device_classifier.get_label(
            dirpath, astutus.usb.LabelRules().get_rules(), astutus.usb.label.get_formatting_data('ansi_terminal'))
        color = data.get('resolved_color', 'pink')
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        # colored_description = f"{start(color)}{label}{end(color)}"
        data['terminal_colored_description'] = label
        data['terminal_colored_node_label_concise'] = f"{data['dirname']} - {label}"
        colored_node_id = f"{start(color)}{data['node_id']}{end(color)}"
        data['terminal_colored_node_label_verbose'] = f"{data['dirname']} - {colored_node_id} - {label}"

        self.data = data
        # Inititialize super to support JSON serialization.
        super(DeviceNode, self).__init__(data)

    def key(self) -> str:
        key_value = f"{self.cls_order} - {self.data['dirname']}"
        logger.debug(f"key_value: {key_value}")
        return key_value

    @property
    def colorized_node_label_for_terminal(self) -> str:
        if self.verbose:
            return self.data['terminal_colored_node_label_verbose']
        return self.data['terminal_colored_node_label_concise']


class OtherDeviceNodeData(DeviceNode):

    cls_order = "05"

    @staticmethod
    def node_id_from_data(data: Dict) -> str:
        return f'other({data.get("dirname", "???")})'

    @classmethod
    def extract_data(cls, dirpath: str) -> Dict:
        data = astutus.usb.usb_impl.extract_specified_data(dirpath, astutus.usb.usb_impl.PCI_KEY_ATTRIBUTES)
        data['node_id'] = cls.node_id_from_data(data)
        data['ilk'] = 'other'
        return data

    def __init__(self, *, data: Dict):
        data = copy.deepcopy(data)
        assert data.get('dirpath') is not None, data
        data["description"] = data['dirpath']
        super(OtherDeviceNodeData, self).__init__(data, self.cls_order)


class PciDeviceNodeData(DeviceNode):

    cls_order = "10"

    @staticmethod
    def node_id_from_data(data: Dict) -> str:
        return f"pci({data.get('vendor', '-')}:{data.get('device', '-')})"

    @classmethod
    def extract_data(cls, dirpath: str) -> Dict:
        data = astutus.usb.usb_impl.extract_specified_data(dirpath, astutus.usb.usb_impl.PCI_KEY_ATTRIBUTES)
        data['node_id'] = cls.node_id_from_data(data)
        data['ilk'] = 'pci'
        return data

    def __init__(self, *, data: Dict):
        data = copy.deepcopy(data)
        assert data.get('dirpath') is not None, data
        data["description"] = "{Device}"  # f"data: {data}"
        super(PciDeviceNodeData, self).__init__(data, self.cls_order)


class UsbDeviceNodeData(DeviceNode):

    cls_order = "00"

    @staticmethod
    def node_id_from_data(data: Dict) -> str:
        return f"usb({data['idVendor']}:{data['idProduct']})"

    @classmethod
    def extract_data(cls, dirpath):
        data = astutus.usb.usb_impl.extract_specified_data(dirpath, astutus.usb.usb_impl.USB_KEY_ATTRIBUTES)
        data['node_id'] = cls.node_id_from_data(data)
        data['ilk'] = 'usb'
        return data

    def __init__(self, *, data: Dict):
        data = copy.deepcopy(data)
        busnum = int(data['busnum'])
        devnum = int(data['devnum'])
        _, _, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
        data["description"] = description
        # if config is not None and config.find_tty():
        #     tty = astutus.usb.find_tty_from_pci_path(data['dirpath'])
        #     data['tty'] = tty
        super(UsbDeviceNodeData, self).__init__(data, self.cls_order)


def node_id_for_dirpath(dirpath: str) -> str:
    data = UsbDeviceNodeData.extract_data(dirpath)
    if data.get("busnum") is not None:
        return UsbDeviceNodeData.node_id_from_data(data)
    data = PciDeviceNodeData.extract_data('', dirpath)
    if data.get("device") is not None:
        return PciDeviceNodeData.node_id_from_data(data)
    return None


def parse_value(value: str) -> Tuple[str, str, str]:
    """ Given a value break it down by the ilk of node (usb or pci), the vendor, and the device or product."""
    value_pattern = r'^(usb|pci)\(([^:]{4}):([^:]{4})\)$'
    matches = re.match(value_pattern, value)
    assert matches, value
    ilk, vendor, device = matches.group(1), matches.group(2), matches.group(3)
    return ilk, vendor, device
