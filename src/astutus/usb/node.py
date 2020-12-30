import logging
import re

import astutus.util

logger = logging.getLogger(__name__)


class DeviceNode(object):

    def __init__(self, dirpath, data, config, alias, cls_order, verbose):
        self.dirpath = dirpath
        self.data = data
        self.node_color = 'pink'
        self.config = config
        self.alias = alias
        if self.alias is None:
            self.order = '50'
        else:
            self.order = self.alias['order']
        self.cls_order = cls_order
        self.verbose = verbose

    def key(self):
        key_value = f"{self.cls_order} - {self.order} - {self.data['dirname']}"
        logger.debug(f"key_value: {key_value}")
        return key_value

    def get_description(self):
        description_template = self.find_description_template()
        description = description_template.format_map(self.data)
        if description == "<built-in function id>":
            logger.error(description_template)
            logger.error(self.data)
            raise AssertionError()
        return description

    def find_description_template(self):
        # The config may directly have a simple template, or something that
        # can select or generate a template.
        template_thing = self.config.get('description_template')
        if callable(template_thing):
            template_generator = template_thing
            description_template = template_generator(self.dirpath, self.data)
        elif isinstance([], type(template_thing)):
            # If it is a list, then currently it contain selectors.
            for item in self.config['description_template']:
                if item.get('test') == 'value_in_stdout':
                    cmd = item.get('cmd')
                    if cmd is None:
                        raise ValueError('cmd must be given for test value_in_stdout')
                    _, stdout, stderr = astutus.util.run_cmd(cmd, cwd=self.dirpath)
                    if item.get('value') in stdout:
                        description_template = item.get('description_template')
                        break
        else:
            # If none of the above, the template thing is just a template.
            description_template = template_thing
        if description_template is None:
            description_template = "{description}"
        return description_template

    @property
    def colorized(self):
        if self.alias is None:
            label = self.get_description()
            color = self.config['color']
        else:
            label = self.alias['label']
            color = self.alias['color']
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        colored_label = f"{start(color)}{label}{end(color)}"
        if self.verbose:
            node_label = f"{start(self.node_color)}{self.data['node_id']}{end(self.node_color)}"
            return f"{self.data['dirname']}  - {node_label} - {colored_label}"
        return f"{self.data['dirname']} - {colored_label}"


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

    def __init__(self, *, dirpath, data, config, alias, verbose):
        # TODO:  "Use lspci to get description"
        data["description"] = data['node_id']
        # logger.debug(f'alias: {alias}')
        super(PciDeviceNodeData, self).__init__(dirpath, data, config, alias, self.cls_order, verbose)


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
        logger
        return data

    def __init__(self, *, dirpath, data, config, alias, verbose):
        busnum = int(data['busnum'])
        devnum = int(data['devnum'])
        _, _, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
        data["description"] = description
        if config.get('find_tty'):
            tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
            data['tty'] = tty
        super(UsbDeviceNodeData, self).__init__(dirpath, data, config, alias, self.cls_order, verbose)


def node_id_for_dirpath(dirpath):
    data = UsbDeviceNodeData.extract_data('', dirpath)
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
