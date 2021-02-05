#!/usr/bin/env python3

import argparse
import copy
import json
import logging
import os
import os.path
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.log
import astutus.usb
import astutus.usb.node
import astutus.util
import treelib

logger = logging.getLogger(__name__)

# TODO:  Move this to astutus.util to avoid breaking DRY principle.
# DEFAULT_BASEPATH = "/sys/devices/pci0000:00"
DEFAULT_BASEPATH = "/sys/devices"
DEFAULT_DEVICE_ALIASES_FILEPATH = "~/.astutus/device_aliases.json"
DEFAULT_DEVICE_CONFIGURATIONS_FILEPATH = "~/.astutus/device_configurations.json"


def key_by_node_data_key(node):
    return node.data.key()


def get_data_for_dirpath(ilk, dirpath, pci_device_info):
    if ilk == 'usb':
        data = astutus.usb.node.UsbDeviceNodeData.extract_data(dirpath)
        assert data.get('dirpath') is not None, data
    elif ilk == 'pci':
        data = astutus.usb.node.PciDeviceNodeData.extract_data(dirpath)
        if pci_device_info is not None:
            data.update(pci_device_info)
        assert data.get('dirpath') is not None, data
    else:
        _, dirname = dirpath.rsplit("/", 1)
        data = astutus.usb.node.OtherDeviceNodeData.extract_data(dirpath)
        logger.debug(f'ilk: {data.get("ilk")}')
        logger.debug(f'dirpath: {data.get("dirpath")}')
        logger.debug(f'dirname: {data.get("dirname")}')
    return data


def get_node_data(data, device_config, alias):
    assert data is not None
    ilk = data['ilk']
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
        node_data = astutus.usb.node.OtherDeviceNodeData(
            data=data,
            config=device_config,
            alias=alias)
    else:
        raise NotImplementedError()
    return node_data


class UsbDeviceTree(object):
    """  Provides a tree of USB devices and the PCI buses and devices that connect them.

    The representation can provide aliases that are meaningful in terms of physical USB devices
    and ports on the computer.

    The representation can be color-coded as desired by the user.

    To speed up rendering, this code implements caching of intermediate calculations
    and lazy evaluation.

    """

    def __init__(self, basepath, device_aliases_filepath, device_configurations_filepath=None):
        if basepath is None:
            basepath = DEFAULT_BASEPATH
        self.basepath = basepath
        self.device_aliases_filepath = device_aliases_filepath
        self.device_configurations_filepath = device_configurations_filepath
        # These items for lazy evaluation.
        self.slot_to_device_info_map = None
        self.treelib_tree = None
        self.device_configurations = None
        self.aliases = None
        self.tree_dirpaths = None
        self.data_by_dirpath = None
        self.ilk_by_dirpath = None
        self.usb_device_dirpaths = None
        self.tree_as_dict = None

    def get_device_info_map(self):
        if self.slot_to_device_info_map is None:
            self.slot_to_device_info_map = astutus.util.pci.get_slot_to_device_info_map_from_lspci()
        return self.slot_to_device_info_map

    @staticmethod
    def walk_basepath_for_usb(basepath):
        logger.info(f"Start walk for {basepath}")
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
        logger.info(f"End walk for {basepath}")
        return usb_device_paths, ilk_by_dirpath

    @staticmethod
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

    def find_data_for_paths(self, ilk_by_dirpath, dirpaths):
        data_by_dirpath = {}
        device_info_map = self.get_device_info_map()
        for dirpath in dirpaths:
            ilk = ilk_by_dirpath[dirpath]

            if ilk == 'pci':
                _, dirname = dirpath.rsplit('/', 1)
                slot = dirname[5:]
                device_info = device_info_map.get(slot)
            else:
                device_info = None
            data = get_data_for_dirpath(ilk, dirpath, device_info)
            data_by_dirpath[dirpath] = data
        return data_by_dirpath

    @staticmethod
    def augment_data_by_nodepath(tree_dirpaths, data_by_dirpath):
        nodepath_by_dirpath = {}
        for dirpath in tree_dirpaths:
            data = data_by_dirpath[dirpath]
            dirpath = data['dirpath']
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

    @staticmethod
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

    def get_usb_device_dirpath(self):
        if self.usb_device_dirpaths is None:
            self.usb_device_dirpaths, self.ilk_by_dirpath = self.walk_basepath_for_usb(self.basepath)
        return self.usb_device_dirpaths

    def get_ilk_by_dirpath(self):
        """ The attribute ilk is one of 'usb', 'pci', or 'other'."""
        if self.ilk_by_dirpath is None:
            self.usb_device_dirpaths, self.ilk_by_dirpath = self.walk_basepath_for_usb(self.basepath)
        return self.ilk_by_dirpath

    def get_tree_dirpaths(self) -> List[str]:
        """ Returns a list of directory paths for the tree.

        The list is sorted from the top of the tree to the bottom, so parent nodes are guaranteed
        to be listed before child nodes.
        """
        if self.tree_dirpaths is None:
            self.tree_dirpaths = self.find_tree_dirpaths(self.basepath, self.get_usb_device_dirpath())
            logger.debug(f'self.tree_dirpaths: {self.tree_dirpaths}')
        return self.tree_dirpaths

    def get_data_by_dirpath(self):
        if self.data_by_dirpath is None:
            logger.info("Start get_data_by_dirpath")
            start_time = datetime.now()

            tree_dirpaths = self.get_tree_dirpaths()
            data_by_dirpath = self.find_data_for_paths(self.get_ilk_by_dirpath(), self.get_tree_dirpaths())

            self.augment_data_by_nodepath(tree_dirpaths, data_by_dirpath)
            for dirpath in tree_dirpaths:
                logger.debug(f"dirpath: {dirpath} nodepath: {data_by_dirpath[dirpath]['nodepath']}")
            self.data_by_dirpath = data_by_dirpath

            logger.info(f"End get_data_by_dirpath duration: {(datetime.now() - start_time).total_seconds()}")
        return self.data_by_dirpath

    def assemble_bare_tree(self):
        logger.info("Start assemble_bare_tree")
        start_time = datetime.now()
        tree = treelib.Tree()
        rootpath, tag = self.basepath.rsplit('/', 1)
        for dirpath in self.get_tree_dirpaths():
            parent_dirpath, dirname = dirpath.rsplit('/', 1)
            if parent_dirpath == self.basepath:
                pass
            if parent_dirpath == rootpath:
                parent = None
            else:
                parent = parent_dirpath
            data = {
                'dirpath': dirpath,
                'dirname': dirname,
            }
            tree.create_node(
                tag=dirname,
                identifier=dirpath,
                parent=parent,
                data=data)
        logger.info(f"End assemble_bare_tree - duration: {(datetime.now() - start_time).total_seconds()}")
        return tree.to_dict(with_data=True)

    def assemble_tree(
            self,
            *,
            basepath,
            tree_dirpaths,
            data_by_dirpath,
            ilk_by_dirpath):
        logger.info("Start assemble_tree")
        start_time = datetime.now()
        tree = treelib.Tree()
        rootpath, tag = basepath.rsplit('/', 1)
        for dirpath in tree_dirpaths:
            data = data_by_dirpath[dirpath]
            assert dirpath == data['dirpath']
            parent_dirpath, dirname = dirpath.rsplit('/', 1)
            # ilk = ilk_by_dirpath[dirpath]
            # nodepath = data.get('nodepath')
            device_config = None
            alias = None
            node_data = get_node_data(data, device_config, alias)
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
        logger.info(f"End assemble_tree - duration: {(datetime.now() - start_time).total_seconds()}")
        return tree

    def formulate_data_as_table(self, data):
        lines = []
        # Data is a dictionary, but we want to display it as a table
        lines.extend(self.make_button(data))
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

    @staticmethod
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

    @staticmethod
    def sanitize_for_html(data):
        sanitized_data = copy.deepcopy(data)
        keys_to_remove = [
            'resolved_description',
            'resolved_color',
            'terminal_colored_node_label_verbose',
            'terminal_colored_node_label_concise',
            'terminal_colored_description',
        ]
        for key in keys_to_remove:
            if sanitized_data.get(key) is not None:
                del sanitized_data[key]

        return sanitized_data

    # def get_aliases(self):
    #     if self.aliases is None:
    #         self.aliases = astutus.usb.device_aliases.Device Aliases(filepath=self.device_aliases_filepath)
    #     return self.aliases

    def get_treelib_tree(self):
        if self.treelib_tree is None:
            self.treelib_tree = self.assemble_tree(
                basepath=self.basepath,
                tree_dirpaths=self.get_tree_dirpaths(),
                data_by_dirpath=self.get_data_by_dirpath(),
                ilk_by_dirpath=self.get_ilk_by_dirpath()
            )
        return self.treelib_tree

    def get_tree_as_dict(self):
        if self.tree_as_dict is None:
            tree = self.get_treelib_tree()
            self.tree_as_dict = tree.to_dict(with_data=True)
        return self.tree_as_dict

    def execute_tree_cmd(
            self,
            *,
            verbose=False,
            node_ids=[],
            show_tree=False,
            to_dict=False,
            to_tree_dirpaths=False,
            to_bare_tree=False
            ):

        if show_tree:
            astutus.usb.node.DeviceNode.verbose = verbose
            tree = self.get_treelib_tree()
            tree.show(data_property="colorized_node_label_for_terminal", key=key_by_node_data_key)

        if to_tree_dirpaths:
            return self.get_tree_dirpaths()

        if to_bare_tree:
            return self.assemble_bare_tree()

        if to_dict:
            return self.get_tree_as_dict()

        # if to_html:
        #     tree = self.get_treelib_tree()
        #     tree_dict = tree.to_dict(with_data=True)
        #     return self.traverse_tree_dict_to_html(tree_dict)

        if len(node_ids) > 0:
            self.generate_alias_json_snippet(
                node_ids=node_ids,
                tree_dirpaths=self.get_tree_dirpaths(),
                data_by_dirpath=self.get_data_by_dirpath(),
                device_configurations=self.get_device_configurations()
            )


def parse_arguments(raw_args):
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

    tree = UsbDeviceTree(
        basepath=args.basepath,
        device_aliases_filepath=args.device_aliases_filepath,
        device_configurations_filepath=args.device_configurations_filepath
    )

    tree.execute_tree_cmd(verbose=args.verbose, node_ids=args.node_id_list, show_tree=True, to_dict=False)


if __name__ == '__main__':

    main(sys.argv[1:])
