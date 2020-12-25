import logging
import os

import astutus.usb
import astutus.util
import treelib

logger = logging.getLogger(__name__)


included_files = ['manufacturer', 'product', 'idVendor', 'idProduct', 'busnum', 'devnum', 'serial']


class Directory(object):

    def __init__(self, tag):
        self.tag = tag

    @property
    def colorized(self):
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        return f"{start('cyan')}{self.tag}{end('cyan')}"

    def key(self):
        return f"10 - {self.tag}"


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
        color = self.config['color']
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        return f"{self.filename} - {start(color)}{description}{end(color)}"

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
    tree.create_node(
        tag=rootpath, identifier=rootpath, parent=None, data=Directory(rootpath))
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
                tree.create_node(tag=tag, identifier=dirpath,  parent=parent_path, data=Directory(tag))

    tree.show(data_property="colorized", key=key_for_files_first_first_alphabetic)
