import json
import logging
import os
import re

import astutus.usb
import astutus.util
import treelib

logger = logging.getLogger(__name__)


class AliasPaths:

    hardcoded_aliases = {
        'pci(0x1002:0x5a19)': {
            'order': '10', 'label': 'wendy:front', 'color': 'cyan'},
        'pci(0x1002:0x5a1b)': {
            'order': '20', 'label': 'wendy:back:row2', 'color': 'blue'},
        '05e3:0610[child==0bda:8153]': {
            'priority': 50, 'order': '30', 'label': 'TECKNET USB 2.0', 'color': 'orange'},
        '05e3:0612[child==0bda:8153]': {
            'priority': 50, 'order': '40', 'label': 'TECKNET USB 3.0', 'color': 'orange'},
        '[ancestor==05e3:0612]1a86:7523[sibling==0bda:8153]': {
            'priority': 99, 'order': '40', 'label': 'SMAKIN Relay into TECKNET USB 3.0', 'color': 'fushia'},
        '[ancestor==05e3:0610]1a86:7523[sibling==0bda:8153]': {
            'priority': 98, 'order': '40', 'label': 'SMAKIN Relay into TECKNET USB 2.0', 'color': 'fushia'},
        '1a86:7523[sibling==05e3:0610]': {
            'priority': 98, 'order': '40', 'label': 'SMAKIN Relay into ONN', 'color': 'fushia'},
    }

    def __init__(self):
        logger.info("Initializing AliasPaths")

        child_pattern = r'\[child(==|!=)([^\]]+)]'
        ancestor_pattern = r'\[ancestor(==|!=)([^\]]+)]'
        sibling_pattern = r'\[sibling(==|!=)([^\]]+)]'

        # Parse the key into ancestor, current, and child axes:
        self.aliases = {}
        for key in self.hardcoded_aliases.keys():
            logger.debug(f"key: {key}")
            check_str = key
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
            self.aliases[(ancestor_check, current_check, child_check, sibling_check)] = self.hardcoded_aliases[key]

    @staticmethod
    def matches_as_usb_node(dirpath, value):
        if value.startswith('pci('):
            return False
        data = UsbDeviceNodeData.extract_data('', dirpath, ['idVendor', 'idProduct'])
        vendor = data.get('idVendor')
        product = data.get('idProduct')
        if vendor is not None and product is not None:
            id = f"{vendor}:{product}"
            if id == value:
                return True
        return False

    @staticmethod
    def matches_as_pci_node(dirpath, value):
        if not value.startswith('pci('):
            return False
        data = PciDeviceNodeData.extract_data('', dirpath, ['vendor', 'device'])
        vendor = data.get('vendor')
        device = data.get('device')
        if vendor is not None and device is not None:
            id = f"pci({vendor}:{device})"
            if id == value:
                return True
        return False

    def sibling_passes(self, check, dirpath):
        if check is None:
            return True
        operator, value = check
        # Only implementing equality operator now.
        assert operator == "=="
        parent_dirpath, current = dirpath.rsplit('/', 1)
        if self.has_usb_child(parent_dirpath, value):
            return True
        if value.startswith('pci('):
            raise NotImplementedError()
        return False

    def ancestor_passes(self, check, dirpath):
        if check is None:
            return True
        operator, value = check
        # Only implementing equality operator now.
        assert operator == "=="
        logger.debug(f"dirpath: {dirpath}")
        a_dirpath, current = dirpath.rsplit('/', 1)
        while a_dirpath != '/sys/devices':
            if self.matches_as_usb_node(a_dirpath, value):
                return True
            if self.matches_as_pci_node(a_dirpath, value):
                return True
            a_dirpath, current = a_dirpath.rsplit('/', 1)
        return False

    def usb_child_passes(self, check, dirpath):
        if check is None:
            return True
        operator, value = check
        # Only implementing equality operator now.
        assert operator == "=="
        if self.has_usb_child(dirpath, value):
            return True
        return False

    def get(self, id, dirpath):
        filtered_aliases = []
        # Filter on current check first of all, with an exact match required.
        for checks in self.aliases.keys():
            logger.debug(f"checks: {checks}")
            if id == checks[1][1]:
                # Only equality supported for current access
                assert checks[1][0] == '=='
                filtered_aliases.append((checks, self.aliases[checks]))

        if len(filtered_aliases) > 0:
            logger.debug(f"id: {id}")
            logger.debug(f"tests: {len(filtered_aliases)}")
            # Sort by priority, so that first passed test is the most desirable one.

            def by_priority_key(item):
                return item[1].get('priority', '00')

            # TODO:  Should just sort them initially, rather than redoing each time.
            prioritized_aliases = sorted(filtered_aliases, key=by_priority_key, reverse=True)

            for alias in prioritized_aliases:
                checks, alias_value = alias
                logger.debug(f"checks: {checks}")
                logger.debug(f"alias_value: {alias_value}")
                # Parent test already been applied, no need to retest now.
                ancestor_check, _, child_check, sibling_check = checks
                if not self.ancestor_passes(ancestor_check, dirpath):
                    continue
                if not self.usb_child_passes(child_check, dirpath):
                    continue
                if not self.sibling_passes(sibling_check, dirpath):
                    continue
                return alias_value
        return None

    def label(self, name):
        for checks in self.aliases.keys():
            ancestor_check, current_check, child_check = checks
            current_check_value = current_check[1]
            if ancestor_check is None and current_check_value == name and child_check is None:
                alias = self.aliases[checks]
                return alias['label']
        return None

    def has_usb_child(self, dirpath, child_id):
        root, dirs, _ = next(os.walk(dirpath))
        logger.debug(f"dirs: {dirs}")
        for dir in dirs:
            subdirpath = os.path.join(root, dir)
            data = UsbDeviceNodeData.extract_data('', subdirpath, ['idVendor', 'idProduct'])
            id = f"{data.get('idVendor', '')}:{data.get('idProduct', '')}"
            if id == child_id:
                return True
        return False


alias_paths = AliasPaths()


class DeviceNode(object):

    @staticmethod
    def extract_specified_data(tag, dirpath, filenames, included_files):
        data = {'tag': tag}
        for filename in filenames:
            if filename not in included_files:
                continue
            filepath = os.path.join(dirpath, filename)
            return_code, stdout, stderr = astutus.util.run_cmd(f"cat {filepath}")
            if return_code != 0:
                continue
            data[filename] = stdout.strip()
        return data

    def __init__(self, tag, dirpath, data, config, alias, cls_order):
        self.tag = tag
        self.dirpath = dirpath
        self.data = data
        self.config = config
        self.alias = alias
        if self.alias is None:
            self.order = '50'
        else:
            self.order = self.alias['order']
        self.cls_order = cls_order

    def key(self):
        key_value = f"{self.cls_order} - {self.order} - {self.tag}"
        logger.debug(f"key_value: {key_value}")
        return key_value

    def get_description(self):
        description_template = self.find_description_template()
        return description_template.format_map(self.data)

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
        return f"{self.tag} - {start(color)}{label}{end(color)}"


class PciDeviceNodeData(DeviceNode):

    included_files = ['vendor', 'device']
    cls_order = "10"

    @classmethod
    def extract_data(cls, tag, dirpath, filenames):
        return DeviceNode.extract_specified_data(tag, dirpath, filenames, cls.included_files)

    def __init__(self, *, tag, dirpath, data, config):
        id = f"pci({data.get('vendor', '-')}:{data.get('device', '-')})"
        logger.debug(f'id: {id}')
        # TODO:  "Use lspci to get description"
        data["description"] = id
        alias = alias_paths.get(id, dirpath)
        logger.debug(f'alias: {alias}')
        super(PciDeviceNodeData, self).__init__(tag, dirpath, data, config, alias, self.cls_order)
        logger.info(f'PCI node created id:{id} tag: {tag}')


class UsbDeviceNodeData(DeviceNode):

    included_files = ['manufacturer', 'product', 'idVendor', 'idProduct', 'busnum', 'devnum', 'serial']
    cls_order = "00"

    @classmethod
    def extract_data(cls, tag, dirpath, filenames):
        return DeviceNode.extract_specified_data(tag, dirpath, filenames, cls.included_files)

    def __init__(self, *, tag, dirpath, data, config):
        busnum = int(data['busnum'])
        devnum = int(data['devnum'])
        _, _, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
        data["description"] = description
        if config.get('find_tty'):
            tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
            data['tty'] = tty
        # For now, just find the alias based on the vendorId:productId value
        id = f"{data['idVendor']}:{data['idProduct']}"
        alias = alias_paths.get(id, dirpath)
        super(UsbDeviceNodeData, self).__init__(tag, dirpath, data, config, alias, self.cls_order)
        logger.info(f'USB node created id:{id} tag: {tag}')


def key_by_node_data_key(node):
    return node.data.key()


class DeviceConfigurations(object):

    device_map = {
        '0e6f:0232': {
            'name_of_config': 'PDPGaming LVL50 Wireless Headset',
            'color': 'magenta',
            'description_template': "{product}",
        },
        '05e3:0610': {
            'name_of_config': 'Genesys Logic, Inc. 4-port hub',
            'color': 'yellow',
            'description_template': None,
        },
        '04e8:6860': {
            'name_of_config': 'Samsung Electronics Co., Ltd Galaxy series, misc. (MTP mode)',
            'color': 'blue',
            'description_template': None,
        },
        '046d:082c': {
            'name_of_config': 'Logitech HD Webcam C615',
            'color': 'magenta',
            'description_template': "Logitech {product}",
        },
        '0bda:8153': {
            'name_of_config': 'Realtek USB 10/100/1000 LAN',
            'color': 'green',
            'description_template': "{manufacturer} {product}",
        },
        '1d6b:0001': {
            'name_of_config': 'Linux Foundation 1.1 root hub',
            'color': 'yellow',
            'description_template': None,
        },
        '1d6b:0002': {
            'name_of_config': 'Linux Foundation 2.0 root hub',
            'color': 'yellow',
            'description_template': None,
        },
        '1d6b:0003': {
            'name_of_config': 'Linux Foundation 3.0 root hub',
            'color': 'yellow',
            'description_template': None,
        },
        '046d:c52f': {
            'name_of_config': 'Logitech, Inc. Unifying Receiver',
            'color': 'magenta',
            'description_template': [
                {
                    'cmd': 'grep -r . -e "mouse" 2>/dev/null',
                    'test': 'value_in_stdout',
                    'value': 'mouse',
                    'description_template': "{manufacturer} {product} mouse",
                },
                {
                    'cmd': 'grep -r . -e "numlock" 2>/dev/null',
                    'test': 'value_in_stdout',
                    'value': 'numlock',
                    'description_template': "{manufacturer} {product} keyboard",
                },
            ],
        },
        '046d:c52b': {
            'name_of_config': 'Logitech, Inc. Unifying Receiver',
            'color': 'magenta',
            'description_template': [
                {
                    'cmd': 'grep -r . -e "mouse" 2>/dev/null',
                    'test': 'value_in_stdout',
                    'value': 'mouse',
                    'description_template': "{manufacturer} {product} mouse",
                },
                {
                    'cmd': 'grep -r . -e "numlock" 2>/dev/null',
                    'test': 'value_in_stdout',
                    'value': 'numlock',
                    'description_template': "{manufacturer} {product} keyboard",
                },
            ],
        },
        '1a86:7523': {
            'name_of_config': 'QinHeng Electronics HL-340 USB-Serial adapter',
            'color': 'green',
            'description_template': "{description} - {tty}",
            'find_tty': True
        },
    }

    def find_usb_configuration(self, data):
        if data.get('idVendor') is None:
            return None
        key = f"{data['idVendor']}:{data['idProduct']}"
        characteristics = self.device_map.get(key)
        if characteristics is None:
            if data.get('busnum') and data.get('devnum'):
                characteristics = {
                    'name_of_config': 'Generic',
                    'color': 'blue',
                    'description_template': None,
                }
        return characteristics

    def write_as_json(self, filepath):
        with open(filepath, 'w') as config_file:
            json.dump(self.device_map, config_file, indent=4, sort_keys=True)


def print_tree():
    logger.info("Start print_tree")
    basepath = '/sys/devices/pci0000:00'
    device_paths = []

    for dirpath, dirnames, filenames in os.walk(basepath):
        if "busnum" in filenames and "devnum" in filenames:
            device_paths.append(dirpath + "/")

    logger.info(f"Number of USB devices found: {len(device_paths)}")
    for device_path in device_paths:
        logger.debug(device_path)

    nodes_to_create = []
    for device_path in device_paths:
        idx = len(basepath)
        while idx > 0:
            node = device_path[:idx]
            if node not in nodes_to_create:
                nodes_to_create.append(node)
            idx = device_path.find("/", idx + 1)

    logger.info(f"Number of nodes to create: {len(nodes_to_create)}")
    for node in nodes_to_create:
        logger.debug(node)

    device_configurations = DeviceConfigurations()

    rootpath, tag = basepath.rsplit('/', 1)
    logger.debug(f"rootpath: {rootpath}")
    logger.debug(f"tag: {tag}")
    tree = treelib.Tree()
    for dirpath, dirnames, filenames in os.walk(basepath):
        if dirpath in nodes_to_create:
            if dirpath == rootpath:
                continue
            parent_path, tag = dirpath.rsplit("/", 1)
            if parent_path == rootpath:
                parent = None
            else:
                parent = parent_path
            data = UsbDeviceNodeData.extract_data(tag, dirpath, filenames)
            device_config = device_configurations.find_usb_configuration(data)
            if device_config is not None:
                node_data = UsbDeviceNodeData(tag=tag, dirpath=dirpath, data=data, config=device_config)
            else:
                pci_data = PciDeviceNodeData.extract_data(tag, dirpath, filenames)
                pci_config = {'color': 'cyan'}
                node_data = PciDeviceNodeData(tag=tag, dirpath=dirpath, data=pci_data, config=pci_config)
            tree.create_node(
                tag=tag,
                identifier=dirpath,
                parent=parent,
                data=node_data)

    tree.show(data_property="colorized", key=key_by_node_data_key)
