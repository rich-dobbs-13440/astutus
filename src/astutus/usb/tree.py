import argparse
import json
import logging
import os
import os.path
import sys

import astutus.log
import astutus.usb

import astutus.usb.node
import astutus.util
import treelib

logger = logging.getLogger(__name__)


def key_by_node_data_key(node):
    return node.data.key()


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
        slashed_device_path = device_path + "/"
        idx = len(basepath)
        while idx > 0:
            dirpath = slashed_device_path[:idx]
            if dirpath not in dirpath_set:
                tree_dirpaths.append(dirpath)
                dirpath_set.add(dirpath)
            idx = slashed_device_path.find("/", idx + 1)
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
            _, dirname = dirpath.rsplit("/", 1)
            data = {'ilk': ilk, 'dirpath': dirpath, 'dirname': dirname}
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


def generate_alias_json_snippet(node_ids, tree_dirpaths, data_by_dirpath, device_configurations):
    alias_map = {}
    for dirpath in tree_dirpaths:
        data = data_by_dirpath[dirpath]
        config = device_configurations.find_configuration(data)
        node_id = data.get('node_id')
        if node_id in node_ids:
            nodepath = data.get('nodepath')
            logger.debug(data)
            if nodepath is not None:
                values = alias_map.get(nodepath)
                if values is None:
                    values = []
                values.append({
                    "color": config.get_color(),
                    "description_template": config.find_description_template(dirpath),
                    "name_of_config": config.get_name(),
                    "order": "00",
                    "priority": 50,
                    "dirpath": dirpath,
                })
                alias_map[nodepath] = values

    print(json.dumps(alias_map, indent=4, sort_keys=True))


def assemble_tree(
        *,
        device_aliases,
        device_configurations):
    logger.info("assemble_tree")
    basepath = '/sys/devices/pci0000:00'

    usb_device_dirpaths, ilk_by_dirpath = walk_basepath_for_usb(basepath)
    logger.info(f"Number of USB devices found: {len(usb_device_dirpaths)}")
    for device_dirpath in usb_device_dirpaths:
        logger.debug(device_dirpath)
    for dirpath in usb_device_dirpaths:
        logger.debug(f"dirpath: {dirpath} ilk: {ilk_by_dirpath[dirpath]}")

    tree_dirpaths = find_tree_dirpaths(basepath, usb_device_dirpaths)
    logger.info(f"treepaths count: {len(tree_dirpaths)}")
    logger.debug("show ilks for all tree path:")
    for dirpath in tree_dirpaths:
        logger.debug(f"dirpath: {dirpath} ilk: {ilk_by_dirpath[dirpath]}")

    logger.debug("show data for all tree path:")
    data_by_dirpath = find_data_for_paths(ilk_by_dirpath, tree_dirpaths)
    for dirpath in tree_dirpaths:
        logger.debug(f"dirpath: {dirpath} data: {data_by_dirpath[dirpath]}")

    augment_data_by_nodepath(tree_dirpaths, data_by_dirpath)
    for dirpath in tree_dirpaths:
        logger.debug(f"dirpath: {dirpath} nodepath: {data_by_dirpath[dirpath]['nodepath']}")

    tree = treelib.Tree()
    rootpath, tag = basepath.rsplit('/', 1)
    for dirpath in tree_dirpaths:
        data = data_by_dirpath[dirpath]
        parent_dirpath, dirname = dirpath.rsplit('/', 1)
        ilk = ilk_by_dirpath[dirpath]
        nodepath = data.get('nodepath')
        alias = device_aliases.get(nodepath)
        device_config = device_configurations.find_configuration(data)
        if ilk == 'usb':
            node_data = astutus.usb.node.UsbDeviceNodeData(
                dirpath=dirpath,
                data=data,
                config=device_config,
                alias=alias)
        elif ilk == 'pci':
            node_data = astutus.usb.node.PciDeviceNodeData(
                dirpath=dirpath,
                data=data,
                config=device_config,
                alias=alias)
        elif ilk == 'other':
            data['node_id'] = basepath
            node_data = astutus.usb.node.PciDeviceNodeData(
                dirpath=dirpath,
                data=data,
                config=device_config,
                alias=alias)
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

    return tree, tree_dirpaths, data_by_dirpath


def parse_args(raw_args):
    # TODO:  Move this to astutus.util to avoid breaking DRY principle.
    default_device_aliases_filepath = "~/.astutus/device_aliases.json"
    default_device_configurations_filepath = "~/.astutus/device_configurations.json"
    parser = argparse.ArgumentParser(
        description="Output a tree of USB devices attached to computer. "
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
        "-n", "--node-ids",
        default="",
        dest="node_ids_str",
        help='generated alias template(s) for a specified node ids, for example "usb(1a86:7523), pci(0x1b21:0x1042)"')

    parser.add_argument(
        "-v", "--verbose",
        default=False,
        dest="verbose",
        action="store_true",
        help="output the tree with additional information")

    parser.add_argument(
        "--log",
        default="WARNING",
        dest="loglevel",
        help="set the logging level")

    args = parser.parse_args(args=raw_args)
    return args


def main(raw_args=None):
    if raw_args is None:
        raw_args = sys.argv[1:]
    args = parse_args(raw_args)
    loglevel = getattr(logging, args.loglevel)
    logging.basicConfig(format=astutus.log.console_format, level=loglevel)
    # Parse node_id_list into list.  Handle spaces or commas
    comma_separated_node_ids = args.node_ids_str.replace(" ", ",").replace(",,", ",")
    node_ids = comma_separated_node_ids.split(",")

    aliases = astutus.usb.device_aliases.DeviceAliases(filepath=args.device_aliases_filepath)
    device_configurations = astutus.usb.device_configurations.DeviceConfigurations(
        filepath=args.default_device_configurations_filepath)
    tree, tree_dirpaths, data_by_dirpath, = assemble_tree(
        device_aliases=aliases,
        device_configurations=device_configurations,
    )
    astutus.usb.node.DeviceNode.verbose = args.verbose
    tree.show(data_property="colorized", key=key_by_node_data_key)
    if node_ids is not None:
        generate_alias_json_snippet(node_ids, tree_dirpaths, data_by_dirpath, device_configurations)


if __name__ == '__main__':

    main(sys.argv[1:])
