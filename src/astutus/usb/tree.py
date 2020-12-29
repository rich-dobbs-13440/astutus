import argparse
import json
import logging
import os
import os.path
import shutil
import sys


import astutus.usb
import astutus.util
import treelib

logger = logging.getLogger(__name__)


class DeviceNode(object):

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

    cls_order = "10"

    @classmethod
    def extract_data(cls, tag, dirpath, filenames):
        return astutus.usb.usb_impl.extract_specified_data(tag, dirpath, astutus.usb.usb_impl.PCI_KEY_ATTRIBUTES)

    def __init__(self, *, tag, dirpath, data, config, alias_paths):
        id = f"pci({data.get('vendor', '-')}:{data.get('device', '-')})"
        logger.debug(f'id: {id}')
        # TODO:  "Use lspci to get description"
        data["description"] = id
        alias = alias_paths.get(id, dirpath)
        logger.debug(f'alias: {alias}')
        super(PciDeviceNodeData, self).__init__(tag, dirpath, data, config, alias, self.cls_order)
        logger.info(f'PCI node created id:{id} tag: {tag}')


class UsbDeviceNodeData(DeviceNode):

    cls_order = "00"

    @classmethod
    def extract_data(cls, tag, dirpath, filenames):
        return astutus.usb.usb_impl.extract_specified_data(tag, dirpath, astutus.usb.usb_impl.USB_KEY_ATTRIBUTES)

    def __init__(self, *, tag, dirpath, data, config, alias_paths):
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

    def __init__(self, filepath=None):
        logger.info("Initializing device configurations")
        self.device_map = None
        self.read_from_json(filepath)
        logger.info("Done initializing device configurations")

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


def print_tree(*, device_aliases_filepath, device_configurations_filepath):
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

    alias_paths = astutus.usb.device_aliases.DeviceAliases(filepath=device_aliases_filepath)
    device_configurations = DeviceConfigurations(filepath=device_configurations_filepath)

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
                node_data = UsbDeviceNodeData(
                    tag=tag, dirpath=dirpath, data=data, config=device_config, alias_paths=alias_paths)
            else:
                pci_data = PciDeviceNodeData.extract_data(tag, dirpath, filenames)
                pci_config = {'color': 'cyan'}
                node_data = PciDeviceNodeData(
                    tag=tag, dirpath=dirpath, data=pci_data, config=pci_config, alias_paths=alias_paths)
            tree.create_node(
                tag=tag,
                identifier=dirpath,
                parent=parent,
                data=node_data)

    tree.show(data_property="colorized", key=key_by_node_data_key)


def parse_args(raw_args):
    # TODO:  Move this to astutus.util to avoid breaking DRY principle.
    default_device_aliases_filepath = "~/.astutus/device_aliases.json"
    default_device_configurations_filepath = "~/.astutus/device_configurations.json"
    parser = argparse.ArgumentParser(
        raw_args,
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

    args = parser.parse_args()
    return args


def main():
    args = parse_args(sys.argv[1:])
    astutus.usb.tree.print_tree(
        device_aliases_filepath=args.device_aliases_filepath,
        device_configurations_filepath=args.default_device_configurations_filepath
    )


if __name__ == '__main__':
    main()
