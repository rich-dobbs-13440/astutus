import logging
import os

import astutus.usb
import astutus.util
import treelib
import re

logger = logging.getLogger(__name__)


class AliasPaths:

    vp_pattern = r'([0-9,a-f]{4}:[0-9,af]{4})'
    vp_child_pattern = r'\[child::' + vp_pattern + r'\]'
    ancestor_pattern = r'\[ancestor::([\w,:\.]+)\]'
    current_child_pattern = vp_pattern + vp_child_pattern
    current_pattern = vp_pattern
    ancestor_current_child_pattern = ancestor_pattern + vp_pattern + vp_child_pattern

    hardcoded_aliases = {
        '0000:00:05.0': {'order': '01', 'label': 'wendy:front', 'color': 'cyan'},
        '0000:00:12.2': {'order': '10', 'label': 'wendy:back:row1', 'color': 'cyan'},
        '0000:00:07.0': {'order': '20', 'label': 'wendy:back:row2', 'color': 'blue'},
        '0000:00:12.0': {'order': '30', 'label': 'wendy:back:row3', 'color': 'red'},
        '0000:00:13.2': {'order': '40', 'label': 'wendy:back:row4,5', 'color': 'green'},
        '[ancestor::wendy:back:row1]05e3:0610[child::0bda:8153]':
            {'priority': 100, 'order': '40', 'label': 'TECKNET: orange mouse and keyboard by nickname',
             'color': 'orange'},
        '[ancestor::0000:00:12.2]05e3:0610[child::0bda:8153]':
            {'priority': 90, 'order': '40', 'label': 'TECKNET: orange mouse and keyboard', 'color': 'orange'},
        '05e3:0610':
            {'priority': 10, 'order': '40', 'label': 'TECKNET or ONN Hub', 'color': 'orange'},
        '05e3:0610[child::0bda:8153]':
            {'priority': 50, 'order': '40', 'label': 'TECKNET', 'color': 'orange'},
    }

    def __init__(self):
        # Parse the key into ancestor, current, and child axes:
        self.aliases = {}
        for key in self.hardcoded_aliases.keys():
            logger.error(f"key: {key}")
            cc_matches = re.match(self.current_child_pattern, key)
            c_matches = re.match(self.current_pattern, key)
            acc_matches = re.match(self.ancestor_current_child_pattern, key)
            if acc_matches:
                ancestor_key = acc_matches.group(1)
                current_key = acc_matches.group(2)
                child_key = acc_matches.group(3)
            elif cc_matches:
                ancestor_key = ''
                current_key = cc_matches.group(1)
                child_key = cc_matches.group(2)
            elif c_matches:
                ancestor_key = ''
                current_key = c_matches.group(1)
                child_key = ''
            else:
                ancestor_key = ''
                current_key = key
                child_key = ''
            self.aliases[(ancestor_key, current_key, child_key)] = self.hardcoded_aliases[key]

    def get(self, id, dirpath):
        # Filter on current first of all, with an exact match required.
        items = []
        for key in self.aliases.keys():
            logger.info(f"key: {key}")
            if id == key[1]:
                items.append((key, self.aliases[key]))

        if len(items) > 0:
            logger.info(f"id: {id}")
            logger.info(f"tests: {len(items)}")
            # Sort by priority, so that first passed test is the most desirable one.

            def by_priority_key(item):
                return item[1].get('priority', '00')

            items = sorted(items, key=by_priority_key, reverse=True)
            for item in items:
                test, alias = item
                logger.debug(f"test: {test}")
                logger.debug(f"alias: {alias}")
                # Parent test already applied, no need to retest now.
                a_test, _, c_test = test
                if a_test != '':
                    logger.info(f"a_test: {a_test}")
                    logger.info(f"dirpath: {dirpath}")
                    ancestors = dirpath.split('/')[:-1]
                    logger.info(f"ancestors: {ancestors}")
                    found = False
                    for ancestor in ancestors:
                        if ancestor == a_test or self.label(ancestor) == a_test:
                            found = True
                            break
                    if not found:
                        continue
                if c_test != '':
                    logger.info(f"c_test: {c_test}")
                    if not self.has_child(dirpath, c_test):
                        continue
                return alias
        return None

    def label(self, name):
        for key in self.aliases.keys():
            a_test, current_test, c_test = key
            if a_test == '' and current_test == name and c_test == '':
                alias = self.aliases[key]
                return alias['label']
        return None

    def has_child(self, dirpath, child_id):
        root, dirs, _ = next(os.walk(dirpath))
        logger.info(f"dirs: {dirs}")
        for dir in dirs:
            subdirpath = os.path.join(root, dir)
            data = extract_data('', subdirpath, ['idVendor', 'idProduct'])
            id = f"{data.get('idVendor', '')}:{data.get('idProduct', '')}"
            if id == child_id:
                return True
        return False


alias_paths = AliasPaths()


included_files = ['manufacturer', 'product', 'idVendor', 'idProduct', 'busnum', 'devnum', 'serial']


class Directory(object):

    def __init__(self, tag, dirpath):
        self.tag = tag
        self.alias = alias_paths.get(self.tag, dirpath)
        if self.alias is None:
            self.order = '00'
        else:
            self.order = self.alias['order']

    @property
    def colorized(self):
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        if self.alias is None:
            label = self.tag
            color = 'cyan'
        else:
            label = self.alias['label']
            color = self.alias['color']
        return f"{start(color)}{label}{end(color)}"

    def key(self):
        return f"10 - {self.order} - {self.tag}"


class UsbDeviceNodeData(object):

    def __init__(self, *, filename, dirpath, data, config):
        self.filename = filename
        self.dirpath = dirpath
        self.data = data
        self.config = config
        busnum = int(self.data['busnum'])
        devnum = int(self.data['devnum'])
        _, _, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
        self.data["description"] = description
        if config.get('find_tty'):
            tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
            data['tty'] = tty
        # For now, just find the alias based on the vendorId:productId value
        id = f"{data['idVendor']}:{data['idProduct']}"
        self.alias = alias_paths.get(id, self.dirpath)

    @property
    def colorized(self):
        if callable(self.config['description_template']):
            template_generator = self.config['description_template']
            description_template = template_generator(self.dirpath, self.data)
        elif isinstance([], type(self.config['description_template'])):
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
            description_template = self.config['description_template']
        if description_template is None:
            description_template = "{description}"
        description = description_template.format_map(self.data)
        if self.alias is None:
            label = description
            color = self.config['color']
        else:
            label = self.alias['label']
            color = self.alias['color']
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        return f"{self.filename} - {start(color)}{label}{end(color)}"

    def key(self):
        return f"00 - {self.filename}"


def key_for_files_first_first_alphabetic(node):
    return node.data.key()


def find_device_config(data):
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
    if data.get('idVendor') is None:
        return None
    key = f"{data['idVendor']}:{data['idProduct']}"
    characteristics = device_map.get(key)
    if characteristics is None:
        if data.get('busnum') and data.get('devnum'):
            characteristics = {
                'name_of_config': 'Generic',
                'color': 'blue',
                'description_template': None,
            }
    return characteristics


def extract_data(tag, dirpath, filenames):
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


def print_tree():
    basepath = '/sys/devices/pci0000:00'
    device_paths = []

    for dirpath, dirnames, filenames in os.walk(basepath):
        if "busnum" in filenames and "devnum" in filenames:
            device_paths.append(dirpath + "/")

    logger.info("device_paths: {len(device_paths}")
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

    logger.info("nodes to create")
    for node in nodes_to_create:
        logger.debug(node)

    rootpath, tag = basepath.rsplit('/', 1)
    tree = treelib.Tree()
    # Not sure what this should be!
    dirpath = ''
    tree.create_node(
        tag=rootpath, identifier=rootpath, parent=None, data=Directory(rootpath, dirpath))
    for dirpath, dirnames, filenames in os.walk(basepath):
        if dirpath in nodes_to_create:
            if dirpath == rootpath:
                continue
            parent_path, tag = dirpath.rsplit("/", 1)
            data = extract_data(tag, dirpath, filenames)
            device_config = find_device_config(data)
            if device_config is not None:
                tree.create_node(
                    tag=tag,
                    identifier=dirpath,
                    parent=parent_path,
                    data=UsbDeviceNodeData(
                        filename=tag,
                        dirpath=dirpath,
                        data=data,
                        config=device_config))
            else:
                tree.create_node(tag=tag, identifier=dirpath, parent=parent_path, data=Directory(tag, dirpath=dirpath))

    tree.show(data_property="colorized", key=key_for_files_first_first_alphabetic)
