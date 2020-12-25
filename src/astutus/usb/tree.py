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

    def __init__(self, *, filename, description_template=None, data=None, color="blue"):
        self.filename = filename
        if description_template is None:
            description_template = "{description}"
        self.description_template = description_template
        self.data = data
        self.color = color
        self.find_description()

    def find_description(self):
        busnum = int(self.data['busnum'])
        devnum = int(self.data['devnum'])
        _, _, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
        # data["fvi_vendorid"] = vendorid
        # data["fvi_productid"] = productid
        self.data["description"] = description

    @property
    def colorized(self):
        description = self.description_template.format_map(self.data)
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        return f"{self.filename} - {start(self.color)}{description}{end(self.color)}"

    def key(self):
        return f"00 - {self.filename}"


def key_for_files_first_first_alphabetic(node):
    return node.data.key()


def lcus_1_usb_relay_node_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
    data['tty'] = tty
    description_template = "{description} - {tty}"
    node = tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=UsbDeviceNodeData(filename=tag, description_template=description_template, data=data, color='green'))
    node.expanded = False


def logitech_usb_receiver_handler(tree, tag, dirpath, parent_path, filenames, data):
    # Might be a keyboard or a mouse or a touchpad or more than one!
    # Will just handle my cases for now.
    description_template = None
    _, stdout, stderr = astutus.util.run_cmd('grep -r . -e "mouse" 2>/dev/null', cwd=dirpath)
    if 'mouse' in stdout:
        description_template = "{manufacturer} {product} mouse"
    if description_template is None:
        _, stdout, stderr = astutus.util.run_cmd('grep -r . -e "numlock" 2>/dev/null', cwd=dirpath)
        if 'numlock' in stdout:
            description_template = "{manufacturer} {product} keyboard"
    if description_template is None:
        description_template = "{manufacturer} {product} unknown transmitter type"
    tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=UsbDeviceNodeData(filename=tag, description_template=description_template, data=data, color='magenta'))


def default_node_handler(tree, tag, dirpath, parent_path, filenames, data):
    if data.get('busnum') and data.get('devnum'):
        tree.create_node(
            tag=tag,
            identifier=dirpath,
            parent=parent_path,
            data=UsbDeviceNodeData(filename=tag, data=data, color='blue'))
    else:
        tree.create_node(tag=tag, identifier=dirpath,  parent=parent_path, data=Directory(tag))


def find_device_characteristics(data):
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
    }
    if data.get('idVendor') is None:
        return None
    key = f"{data['idVendor']}:{data['idProduct']}"
    characteristics = device_map.get(key)
    return characteristics


def get_node_handler(data):
    if data.get('idVendor') == '1a86' and data.get('idProduct') == '7523':
        return lcus_1_usb_relay_node_handler
    if data.get('idVendor') == '046d' and data.get('idProduct') == 'c52f':
        return logitech_usb_receiver_handler
    if data.get('idVendor') == '046d' and data.get('idProduct') == 'c52b':
        return logitech_usb_receiver_handler
    return default_node_handler


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

    logger.debug("device_paths: {len(device_paths}")
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

    logger.debug("nodes to create")
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
            device_characteristics = find_device_characteristics(data)
            if device_characteristics is not None:
                tree.create_node(
                    tag=tag,
                    identifier=dirpath,
                    parent=parent_path,
                    data=UsbDeviceNodeData(
                        filename=tag,
                        description_template=device_characteristics['description_template'],
                        data=data,
                        color=device_characteristics['color']))
            else:
                handle = get_node_handler(data)
                handle(tree, tag, dirpath, parent_path, filenames, data)

    tree.show(data_property="colorized", key=key_for_files_first_first_alphabetic)
