import logging
import os
import re

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


class FileNode(object):

    def __init__(self, filename, data, color="blue"):
        self.filename = filename
        self.data = data
        self.color = color

    @property
    def colorized(self):
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        return f"{self.filename} - {start(self.color)}{self.data}{end(self.color)}"

    def key(self):
        return f"00 - {self.filename}"


def key_for_files_first_first_alphabetic(node):
    return node.data.key()


def tree_filter(node):
    parent_node = node.parent
    if parent_node is None:
        # Must show top of tree!
        return True
    if parent_node.data.show_children:
        return True
    return False


def lcus_1_usb_relay_node_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    augmented_description = f"{tty} - {description}"
    node = tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, augmented_description, color='green'))
    node.expanded = False


def pdpgaming_lvl50_wireless_headset_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    augmented_description = f"{data['product']}"
    node = tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, augmented_description, color='magenta'))
    node.expanded = False


def realtek_usb_lan_adapter_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    augmented_description = f"{data['manufacturer']} {data['product']} (sn: {data['serial']})"
    tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, augmented_description, color='green'))


def logitech_usb_receiver_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    # Might be a keyboard or a mouse or a touchpad or more than one!
    # Will just handle my cases for now.
    augmented_description = None
    _, stdout, stderr = astutus.util.run_cmd('grep -r . -e "mouse" 2>/dev/null', cwd=dirpath)
    if 'mouse' in stdout:
        augmented_description = f"{data['manufacturer']} {data['product']} mouse"
    if augmented_description is None:
        _, stdout, stderr = astutus.util.run_cmd('grep -r . -e "numlock" 2>/dev/null', cwd=dirpath)
        if 'numlock' in stdout:
            augmented_description = f"{data['manufacturer']} {data['product']} keyboard"
    if augmented_description is None:
        augmented_description = f"{data['manufacturer']} {data['product']} unknown transmitter type"
    tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, augmented_description, color='magenta'))


def logitech_hd_webcam_c615_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    augmented_description = f"Logitech {data['product']} (sn: {data['serial']})"
    tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, augmented_description, color='magenta'))


def samsung_galaxy_phone_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    augmented_description = f"{description} (sn: {data['serial']})"
    tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, augmented_description, color='magenta'))


def genesys_logic_inc_4_port_hub_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, description, color='yellow'))


def generic_host_controller_handler(tree, tag, dirpath, parent_path, filenames, data):
    busnum = int(data['busnum'])
    devnum = int(data['devnum'])
    vendorid, productid, description = astutus.usb.find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    id = f"{vendorid}:{productid}"
    tree.create_node(
        tag=tag,
        identifier=dirpath,
        parent=parent_path,
        data=FileNode(id, description, color='yellow'))


def default_node_handler(tree, tag, dirpath, parent_path, filenames, data):
    tree.create_node(tag=tag, identifier=dirpath,  parent=parent_path, data=Directory(tag))
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        if filename in included_files:
            return_code, stdout, stderr = astutus.util.run_cmd(f"cat {filepath}")
            if return_code != 0:
                raise RuntimeError(return_code, stderr, stdout)
            data = stdout.strip()
        else:
            data = None
        if data is not None:
            tree.create_node(tag=filename, identifier=filepath,  parent=dirpath, data=FileNode(filename, data))


def get_node_handler(data):
    if data.get('idVendor') == '1a86' and data.get('idProduct') == '7523':
        return lcus_1_usb_relay_node_handler
    if data.get('idVendor') == '05e3' and data.get('idProduct') == '0610':
        return genesys_logic_inc_4_port_hub_handler
    if data.get('idVendor') == '0e6f' and data.get('idProduct') == '0232':
        return pdpgaming_lvl50_wireless_headset_handler
    if data.get('idVendor') == '0bda' and data.get('idProduct') == '8153':
        return realtek_usb_lan_adapter_handler
    if data.get('idVendor') == '046d' and data.get('idProduct') == 'c52f':
        return logitech_usb_receiver_handler
    if data.get('idVendor') == '046d' and data.get('idProduct') == 'c52b':
        return logitech_usb_receiver_handler
    if data.get('idVendor') == '046d' and data.get('idProduct') == '082c':
        return logitech_hd_webcam_c615_handler
    if data.get('idVendor') == '04e8' and data.get('idProduct') == '6860':
        return samsung_galaxy_phone_handler
    if data.get('idVendor') == '1d6b':
        return generic_host_controller_handler
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
            handle = get_node_handler(data)
            handle(tree, tag, dirpath, parent_path, filenames, data)

    tree.show(data_property="colorized", key=key_for_files_first_first_alphabetic)
