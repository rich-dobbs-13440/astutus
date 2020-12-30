import argparse
import json
import logging
import os
import os.path
import shutil
import sys

import astutus.log
import astutus.usb

import astutus.usb.node
import astutus.util
import treelib

logging.basicConfig(format=astutus.log.standard_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def key_by_node_data_key(node):
    return node.data.key()


class DeviceConfigurations(object):

    def __init__(self, filepath=None):
        logger.info("Initializing device configurations")
        self.device_map = None
        self.read_from_json(filepath)
        logger.info("Done initializing device configurations")

    def find_configuration(self, data):
        if data['ilk'] == 'usb':
            return self.find_usb_configuration(data)
        elif data['ilk'] == 'pci':
            return {
                "color": "cyan",
                "description_template": None,
                'name_of_config': 'Generic PCI',
            }
        else:
            return {
                "color": "cyan",
                "description_template": None,
                'name_of_config': 'Generic Other',
            }

    def find_usb_configuration(self, data):
        if data.get('idVendor') is None:
            return None
        key = f"{data['idVendor']}:{data['idProduct']}"
        characteristics = self.device_map.get(key)
        if characteristics is None:
            if data.get('busnum') and data.get('devnum'):
                characteristics = {
                    'name_of_config': 'Generic USB',
                    'color': 'blue',
                    'description_template': None,
                }
        return characteristics

    def find_usb_configuration_for_node(self, node):
        ilk, vendor, device = astutus.usb.node.parse_value(node)
        assert ilk == "usb"
        data = {
            'idVendor': vendor,
            'idProduct': device
        }
        return self.find_usb_configuration(data)

    def write_as_json(self, filepath):
        with open(filepath, 'w') as config_file:
            json.dump(self.device_map, config_file, indent=4, sort_keys=True)

    def read_from_json(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(astutus.util.get_user_data_path(), 'device_configurations.json')
            if not os.path.isfile(filepath):
                # If the file doesn't exist in the user's data dir, copy the one default
                # one from this directory into the user's data dir.  This will allow the
                # user to customize it if necessary.
                astutus.util.create_user_data_dir_if_needed()
                logger.error(f"astutus.usb.__path__[0]: {astutus.usb.__path__[0]}")
                source_path = os.path.join(astutus.usb.__path__[0], 'device_configurations.json')
                shutil.copyfile(source_path, filepath)
        with open(filepath, 'r') as config_file:
            device_map = json.load(config_file)
        self.device_map = device_map


def walk_basepath_for_usb(basepath):
    ilk_by_dirpath = {}
    usb_device_paths = []
    for dirpath, dirnames, filenames in os.walk(basepath):
        if "busnum" in filenames and "devnum" in filenames:
            usb_device_paths.append(dirpath)
            ilk_by_dirpath[dirpath] = "usb"
        elif "vendor" in filenames and "device" in filenames:
            ilk_by_dirpath[dirpath] = "pci"
        else:
            ilk_by_dirpath[dirpath] = "other"
    return usb_device_paths, ilk_by_dirpath


def find_tree_dirpaths(basepath, device_paths):
    tree_dirpaths = []
    dirpath_set = set()
    for device_path in device_paths:
        idx = len(basepath)
        while idx > 0:
            dirpath = device_path[:idx]
            if dirpath not in dirpath_set:
                tree_dirpaths.append(dirpath)
                dirpath_set.add(dirpath)
            idx = device_path.find("/", idx + 1)
    return tree_dirpaths


def find_data_for_paths(ilk_by_dirpath, dirpaths):
    data_by_dirpath = {}
    for dirpath in dirpaths:
        ilk = ilk_by_dirpath[dirpath]
        if ilk == 'usb':
            data = astutus.usb.node.UsbDeviceNodeData.extract_data(dirpath)
        elif ilk == 'pci':
            data = astutus.usb.node.PciDeviceNodeData.extract_data(dirpath)
        else:
            data = {}
        data_by_dirpath[dirpath] = data
    return data_by_dirpath


def augment_data_by_nodepath(tree_dirpaths, data_by_dirpath):
    nodepath_by_dirpath = {}
    for dirpath in tree_dirpaths:
        data = data_by_dirpath[dirpath]
        node_id = data.get('node_id')
        parent_dirpath, dirname = dirpath.rsplit("/", 1)
        parent_nodepath = nodepath_by_dirpath.get(parent_dirpath)
        if node_id is None:
            nodepath = node_id
        elif parent_nodepath is None:
            nodepath = node_id
        else:
            nodepath = parent_nodepath + "/" + node_id
        nodepath_by_dirpath[dirpath] = nodepath
        data['nodepath'] = nodepath


def print_tree(
        *,
        device_aliases_filepath,
        device_configurations_filepath,
        generate_aliases_for_node_id=None,
        verbose=False):
    logger.info("Start print_tree")
    basepath = '/sys/devices/pci0000:00'

    usb_device_dirpaths, ilk_by_dirpath = walk_basepath_for_usb(basepath)
    logger.info(f"Number of USB devices found: {len(usb_device_dirpaths)}")
    for device_dirpath in usb_device_dirpaths:
        logger.debug(device_dirpath)
    for dirpath in usb_device_dirpaths:
        logger.debug(f"dirpath: {dirpath} ilk: {ilk_by_dirpath[dirpath]}")

    tree_dirpaths = find_tree_dirpaths(basepath, usb_device_dirpaths)
    logger.info(f"Unique dirpaths: {len(tree_dirpaths)}")
    for dirpath in tree_dirpaths:
        logger.debug(f"dirpath: {dirpath} ilk: {ilk_by_dirpath[dirpath]}")

    data_by_dirpath = find_data_for_paths(ilk_by_dirpath, tree_dirpaths)
    for dirpath in tree_dirpaths:
        logger.debug(f"dirpath: {dirpath} data: {data_by_dirpath[dirpath]}")

    augment_data_by_nodepath(tree_dirpaths, data_by_dirpath)
    for dirpath in tree_dirpaths:
        logger.debug(f"dirpath: {dirpath} nodepath: {data_by_dirpath[dirpath]['nodepath']}")

    aliases = astutus.usb.device_aliases.DeviceAliases(filepath=device_aliases_filepath)
    device_configurations = DeviceConfigurations(filepath=device_configurations_filepath)
    tree = treelib.Tree()
    rootpath, tag = basepath.rsplit('/', 1)
    for dirpath in tree_dirpaths:
        data = data_by_dirpath[dirpath]
        parent_dirpath, dirname = dirpath.rsplit('/', 1)
        ilk = ilk_by_dirpath[dirpath]
        nodepath = data.get('nodepath')
        alias = aliases.get(nodepath)
        alias = None
        if ilk == 'usb':
            device_config = device_configurations.find_usb_configuration(data)
            node_data = astutus.usb.node.UsbDeviceNodeData(
                dirpath=dirpath,
                data=data,
                config=device_config,
                alias=alias,
                verbose=verbose)
        elif ilk == 'pci':
            device_config = {'color': 'cyan'}
            node_data = astutus.usb.node.PciDeviceNodeData(
                dirpath=dirpath,
                data=data,
                config=device_config,
                alias=alias,
                verbose=verbose)
        else:
            device_config = {'color': 'cyan'}
            data['node_id'] = basepath
            data['dirname'] = dirname
            data['ilk'] = 'other'
            node_data = astutus.usb.node.PciDeviceNodeData(
                dirpath=dirpath,
                data=data,
                config=device_config,
                alias=alias,
                verbose=verbose)
        if parent_dirpath == basepath:
            pass
        if parent_dirpath == rootpath:
            parent = None
        else:
            parent = parent_dirpath
        tree.create_node(
            tag=dirname,
            identifier=dirpath,
            parent=parent,
            data=node_data)

    tree.show(data_property="colorized", key=key_by_node_data_key)

    alias_map = {}
    for dirpath in tree_dirpaths:
        data = data_by_dirpath[dirpath]
        config = device_configurations.find_configuration(data)
        nodepath = data.get('nodepath')
        if nodepath is not None:
            value = alias_map.get(nodepath)
            if value is None:
                dirpaths = [dirpath]
            else:
                dirpaths = value['dirpaths']
                dirpaths.append(dirpath)
            alias_map[nodepath] = {
                "color": config["color"],
                "label": "label",
                "description_template": config["description_template"],
                "name_of_config": config["name_of_config"],
                "order": "00",
                "priority": 50,
                "dirpaths": dirpaths,
            }
    print(json.dumps(alias_map, indent=4, sort_keys=True))

    if generate_aliases_for_node_id is not None:
        node_id = generate_aliases_for_node_id
        config = device_configurations.find_usb_configuration_for_node(node_id)
        node_paths = astutus.usb.device_aliases.find_node_paths(node_id)

        for node_path in node_paths:
            alias_map[node_path] = {
                "color": config["color"],
                "label": config["name_of_config"],
                "order": "00",
                "priority": 50,
            }

        print(json.dumps(alias_map, indent=4, sort_keys=True))


def parse_args(raw_args):
    # TODO:  Move this to astutus.util to avoid breaking DRY principle.
    default_device_aliases_filepath = "~/.astutus/device_aliases.json"
    default_device_configurations_filepath = "~/.astutus/device_configurations.json"
    parser = argparse.ArgumentParser(
        description="Print out a tree of USB devices attached to computer. "
    )
    # Note:  For consistency with standard usage, help strings should be phrases
    #        that start with a lower case, and not be sentences.
    parser.add_argument(
        "-a", "--device-aliases",
        default=None,
        dest="device_aliases_filepath",
        help=f"specify device aliases file - defaults to {default_device_aliases_filepath}")

    parser.add_argument(
        "-c", "--device-configurations",
        default=None,
        dest="default_device_configurations_filepath",
        help=f"specify device configurations file - defaults to {default_device_configurations_filepath}")

    parser.add_argument(
        "-g", "--generate-alias",
        default=None,
        dest="node_id",
        help="generated alias template(s) for a specified node id, for example usb(1a86:7523)")

    parser.add_argument(
        "-v", "--verbose",
        default=False,
        dest="verbose",
        action="store_true",
        help="output the tree with additional information")

    args = parser.parse_args(args=raw_args)
    return args


def main(raw_args=None):
    if raw_args is None:
        raw_args = sys.argv[1:]
    args = parse_args(raw_args)
    astutus.usb.tree.print_tree(
        device_aliases_filepath=args.device_aliases_filepath,
        device_configurations_filepath=args.default_device_configurations_filepath,
        generate_aliases_for_node_id=args.node_id,
        verbose=args.verbose,
    )


if __name__ == '__main__':

    main(sys.argv[1:])
