import os
import re

import astutus.usb
import astutus.util
import treelib


included_files = ['manufacturer', 'product', 'idVendor', 'idProduct', 'busnum', 'devnum']


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
        data=FileNode(id, augmented_description, color='yellow'))
    node.expanded = False


excluded_directories = [r'^power$', r'^msi_irqs$', r'^ep_\d\d$']


def excluded(tag):
    for pattern in excluded_directories:
        if re.match(pattern, tag):
            return True
    return False


collapsed_directories = [
    r'^power$',
    r'^msi_irqs$',
    r'^ep_\d\d$',
    r'^widgets$',
    r'^ata\d$',
    r'^card\d$',
    r'^i2c-\d+$'
]


def collapse(tag):
    for pattern in collapsed_directories:
        if re.match(pattern, tag):
            return True
    return False


def default_node_handler(tree, tag, dirpath, parent_path, filenames, data):
    if excluded(tag):
        return
    node = tree.create_node(tag=tag, identifier=dirpath,  parent=parent_path, data=Directory(tag))
    if collapse(tag):
        node.expanded = False
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        if filename in included_files:
            return_code, stdout, stderr = astutus.util.run_cmd(f"cat {filepath}")
            if return_code != 0:
                raise RuntimeError(return_code, stderr, stdout)
            data = stdout.strip()
        else:
            data = None
        # print(f"filename: {filename} data: {data}")
        if data is not None:
            tree.create_node(tag=filename, identifier=filepath,  parent=dirpath, data=FileNode(filename, data))


def get_node_handler(data):
    if data.get('idVendor') == '1a86' and data.get('idProduct') == '7523':
        return lcus_1_usb_relay_node_handler
    return default_node_handler


def print_tree():
    basepath = '/sys/devices/pci0000:00'
    rootpath, tag = basepath.rsplit('/', 1)
    tree = treelib.Tree()
    tree.create_node(
        tag=rootpath, identifier=rootpath, parent=None, data=Directory(rootpath))

    for dirpath, dirnames, filenames in os.walk(basepath):
        parent_path, tag = dirpath.rsplit("/", 1)
        data = {}
        for filename in filenames:
            if filename not in included_files:
                continue
            filepath = os.path.join(dirpath, filename)
            return_code, stdout, stderr = astutus.util.run_cmd(f"cat {filepath}")
            if return_code != 0:
                # raise RuntimeError(return_code, stderr, stdout)
                continue
            data[filename] = stdout.strip()
        handle = get_node_handler(data)
        handle(tree, tag, dirpath, parent_path, filenames, data)

    tree.show(data_property="colorized", key=key_for_files_first_first_alphabetic)