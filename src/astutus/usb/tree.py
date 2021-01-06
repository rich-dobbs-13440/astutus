#!/usr/bin/env python3

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

DEFAULT_BASEPATH = "/sys/devices/pci0000:00"
DEFAULT_DEVICE_ALIASES_FILEPATH = "~/.astutus/device_aliases.json"
DEFAULT_DEVICE_CONFIGURATIONS_FILEPATH = "~/.astutus/device_configurations.json"


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
            assert data.get('dirpath') is not None, data
        elif ilk == 'pci':
            data = astutus.usb.node.PciDeviceNodeData.extract_data(dirpath)
            assert data.get('dirpath') is not None, data
        else:
            _, dirname = dirpath.rsplit("/", 1)
            data = {'ilk': ilk, 'dirpath': dirpath, 'dirname': dirname}
            assert data.get('dirpath') is not None, data
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


def generate_alias_json_snippet(*, node_ids, tree_dirpaths, data_by_dirpath, device_configurations):
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


def extract_tree_data(*, basepath):
    logger.info("assemble_tree")

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

    return tree_dirpaths, data_by_dirpath, ilk_by_dirpath


def assemble_tree(
        *,
        basepath,
        tree_dirpaths,
        data_by_dirpath,
        ilk_by_dirpath,
        device_aliases,
        device_configurations):
    tree = treelib.Tree()
    rootpath, tag = basepath.rsplit('/', 1)
    for dirpath in tree_dirpaths:
        data = data_by_dirpath[dirpath]
        assert dirpath == data['dirpath']
        parent_dirpath, dirname = dirpath.rsplit('/', 1)
        ilk = ilk_by_dirpath[dirpath]
        nodepath = data.get('nodepath')
        alias = device_aliases.get(nodepath)
        device_config = device_configurations.find_configuration(data)
        if ilk == 'usb':
            node_data = astutus.usb.node.UsbDeviceNodeData(
                data=data,
                config=device_config,
                alias=alias)
        elif ilk == 'pci':
            node_data = astutus.usb.node.PciDeviceNodeData(
                data=data,
                config=device_config,
                alias=alias)
        elif ilk == 'other':
            data['node_id'] = basepath
            data['nodepath'] = data['dirname']
            assert data['nodepath'], data
            node_data = astutus.usb.node.PciDeviceNodeData(
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

    return tree


def formulate_data_as_table(data):
    lines = []
    # Data is a dictionary, but we want to display it as a table
    lines.extend(make_button(data))
    lines.append('<table class="node_attr_table_class" >')
    retained_keys = [
        'html_label',
        'manufacturer',
        'product',
        'serial',
        'tty',
        'nodepath',
        'resolved_color',
    ]
    for key in retained_keys:
        if key.startswith('terminal_colored_'):
            # Skip these attributes because they are not needed for HTML.
            continue
        value = data.get(key)
        if value is not None:
            lines.append(f'<tr><td>{key}</td><td>{value}</td></tr>')
    lines.append('</table>')
    return lines


def formulate_data_consisely(data):
    lines = []
    lines.append("<ul>")
    lines.append("<li>")
    lines.append(data['dirname'])
    lines.append("<ul>")
    lines.append("<li>")
    lines.append('<table class="node_attr_table_class">')
    lines.append(data.get('node_id'))
    lines.append(f"<tr><td>label</td><td>{data.get('label')}</td></tr>")
    lines.append("</table>")
    lines.append("</li>")
    lines.append("</ul>")
    lines.append("</li>")
    lines.append("</ul>")
    return lines


def make_button(data):
    idx = data['idx']
    dirname = data['dirname']
    data_json = json.dumps(data)
    return [
        f"<button onclick='handleTreeItemClick({data_json})' id='{idx}'>{dirname}</button>",
        data['html_label']
    ]


def traverse_element(element):
    if isinstance(element, dict):
        data = element.get("data")
        children = element.get("children")
        if children is not None:
            lines = []
            if data is not None:
                lines.extend(make_button(data))
            lines.extend(traverse_element(children))
            return lines
        if data is not None:
            return formulate_data_as_table(data)
            # return formulate_data_consisely(data)
        lines = []
        for key, value in element.items():
            lines.extend(traverse_element(value))
        return lines
    elif isinstance(element, list):
        lines = []
        lines.append("<ul>")
        for value in element:
            lines.append("<li>")
            lines.extend(traverse_element(value))
            lines.append("</li>")
        lines.append("</ul>")
        return lines
    else:
        return [f'Got to something unhandled {type(element)}']


def traverse_tree_dict_to_html(tree_dict: dict) -> str:
    lines = []
    items = tree_dict
    lines.extend(traverse_element(items))
    return "\n".join(lines)


def execute_tree_cmd(
        *,
        basepath,
        device_aliases_filepath,
        device_configurations_filepath=None,
        verbose=False,
        node_ids=[],
        show_tree=False,
        to_dict=False,
        to_html=False,
        ):

    if basepath is None:
        basepath = DEFAULT_BASEPATH

    aliases = astutus.usb.device_aliases.DeviceAliases(filepath=device_aliases_filepath)

    device_configurations = astutus.usb.device_configurations.DeviceConfigurations(
        filepath=device_configurations_filepath)

    tree_dirpaths, data_by_dirpath, ilk_by_dirpath = extract_tree_data(basepath=basepath)

    if show_tree or to_dict or to_html:
        tree = assemble_tree(
            basepath=basepath,
            tree_dirpaths=tree_dirpaths,
            data_by_dirpath=data_by_dirpath,
            ilk_by_dirpath=ilk_by_dirpath,
            device_aliases=aliases,
            device_configurations=device_configurations,
        )
        if show_tree:
            astutus.usb.node.DeviceNode.verbose = verbose
            tree.show(data_property="colorized_node_label_for_terminal", key=key_by_node_data_key)

        if to_dict:
            return tree.to_dict(with_data=True)

        if to_html:
            tree_dict = tree.to_dict(with_data=True)
            return traverse_tree_dict_to_html(tree_dict)

    if len(node_ids) > 0:
        generate_alias_json_snippet(
            node_ids=node_ids,
            tree_dirpaths=tree_dirpaths,
            data_by_dirpath=data_by_dirpath,
            device_configurations=device_configurations
        )


def parse_arguments(raw_args):
    # TODO:  Move this to astutus.util to avoid breaking DRY principle.

    parser = argparse.ArgumentParser(
        description="Output a tree of USB devices attached to computer. "
    )
    # Note:  For consistency with standard usage, help strings should be phrases
    #        that start with a lower case, and not be sentences.
    # Note:  In the help, the arguments are listed in the order given, with --help first.
    #        So it is probably best to list them in decreasing order of value to
    #        the end user for the important ones, and then alphabetically
    #        for rarely used options.
    parser.add_argument(
        "-v", "--verbose",
        default=False,
        dest="verbose",
        action="store_true",
        help="output the tree with additional information needed for specifying aliases")

    example = ', for example --node-id "usb(1a86:7523)" "pci(0x1b21:0x1042)"'
    parser.add_argument(
        "-n", "--node-id",
        nargs='+',  # Takes a list of arguments.  Does not need to be last.
        default="",
        dest="node_id_list",
        help=f'generated alias template(s) for a specified node ids{example}')

    parser.add_argument(
        "--log",
        default="WARNING",
        dest="loglevel",
        help="set the logging level - DEBUG, INFO, WARNING, ERROR")

    parser.add_argument(
        "-a", "--device-aliases",
        default=None,
        dest="device_aliases_filepath",
        help=f"specify device aliases file - defaults to {DEFAULT_DEVICE_ALIASES_FILEPATH}")

    # TODO: pull basepath from user data, so it can be configured one time.
    parser.add_argument(
        "-b", "--basepath",
        default=None,
        dest="basepath",
        help=f'set the basepath for the PCI bus - defaults to "{DEFAULT_BASEPATH}"'
    )

    parser.add_argument(
        "-c", "--device-configurations",
        default=None,
        dest="device_configurations_filepath",
        help=f"specify device configurations file - defaults to {DEFAULT_DEVICE_CONFIGURATIONS_FILEPATH}")

    args = parser.parse_args(args=raw_args)
    return args


def main(raw_args=None):
    if raw_args is None:
        raw_args = sys.argv[1:]

    args = parse_arguments(raw_args)

    loglevel = getattr(logging, args.loglevel)
    logging.basicConfig(format=astutus.log.console_format, level=loglevel)

    execute_tree_cmd(
        basepath=args.basepath,
        device_aliases_filepath=args.device_aliases_filepath,
        device_configurations_filepath=args.device_configurations_filepath,
        verbose=args.verbose,
        node_ids=args.node_id_list,
        show_tree=True,
        to_dict=False,
        )


if __name__ == '__main__':

    main(sys.argv[1:])
