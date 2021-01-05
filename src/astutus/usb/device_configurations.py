import copy
import json
import logging
import os
import shutil

import astutus.log
import astutus.util
import webcolors

logger = logging.getLogger(__name__)


def convert_color_for_html_input_type_color(color):
    # Need to interpret named color into hexidecimal format
    if not color.startswith("#"):
        color = webcolors.name_to_hex(color)
    assert color.startswith("#")
    return color


class DeviceConfiguration(object):

    def __init__(self, config, command_runner=astutus.util.run_cmd):
        self.config = config
        # Command runner is a dependency injection point to make code more testable
        self.command_runner = command_runner

    def find_tty(self):
        return self.config.get('find_tty')

    def get_stylers(self):
        stylers = self.config.get('stylers')
        if stylers is None:
            # This is a simple config, where style attributes are directly expressed in the configuration.
            # So, dynamically create a single styler, with no special selection attributes,
            # and return that as a list
            styler = copy.deepcopy(self.config)
            del styler["name_of_config"]  # A styler is not a config.
            stylers = [styler]
        # For now, apply color conversion at this point.
        for styler in stylers:
            styler['color'] = convert_color_for_html_input_type_color(styler.get('color'))
        return stylers

    def get_color(self, dirpath):
        """ Get color in #rrggbb format suitable for HTML input control. """
        styler = self.find_styler(dirpath)
        color = styler.get('color')
        if color is None:
            color = 'cyan'
        color = convert_color_for_html_input_type_color(color)
        return color

    def get_name(self):
        return self.config.get('name_of_config')

    def generate_description(self, dirpath, data):
        description_template = self.find_description_template(dirpath)
        description = description_template.format_map(data)
        return description

    def find_styler(self, dirpath):
        for styler in self.get_stylers():
            styler['color'] = convert_color_for_html_input_type_color(styler.get('color'))
            if styler.get('test') is None:
                return styler
            elif styler.get('test') == 'value_in_stdout':
                cmd = styler.get('cmd')
                if cmd is None:
                    raise ValueError('cmd must be given for test value_in_stdout')
                _, stdout, stderr = self.command_runner(cmd, cwd=dirpath)
                if styler.get('value') in stdout:
                    return styler
        return None

    def find_description_template(self, dirpath):
        styler = self.find_styler(dirpath)
        if styler is None:
            description_template = "{description}"
        else:
            description_template = styler.get('description_template')
            if description_template is None:
                description_template = "{description}"
        return description_template


class DeviceConfigurations(object):

    def __init__(self, filepath=None, command_runner=astutus.util.run_cmd):
        logger.info("Initializing device configurations")
        self.device_map = None
        self.read_from_json(filepath)
        self.command_runner = command_runner
        logger.info("Done initializing device configurations")

    def find_configuration(self, data):
        if data['ilk'] == 'usb':
            return self.find_usb_configuration(data)
        elif data['ilk'] == 'pci':
            config = {
                "color": "cyan",
                "description_template": None,
                'name_of_config': 'Generic PCI',
            }
            return DeviceConfiguration(config, self.command_runner)
        else:
            config = {
                "color": "cyan",
                "description_template": None,
                'name_of_config': 'Generic Other',
            }
            return DeviceConfiguration(config, self.command_runner)

    def find_usb_configuration(self, data):
        if data.get('idVendor') is None:
            return None
        key = f"{data['idVendor']}:{data['idProduct']}"
        config = self.device_map.get(key)
        if config is None:
            if data.get('busnum') and data.get('devnum'):
                config = {
                    'name_of_config': 'Generic USB',
                    'color': 'blue',
                    'description_template': None,
                }
        return DeviceConfiguration(config, self.command_runner)

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
                source_path = os.path.join(astutus.usb.__path__[0], 'device_configurations.json')
                shutil.copyfile(source_path, filepath)
        with open(filepath, 'r') as config_file:
            device_map = json.load(config_file)
        self.device_map = device_map

    def get_item(self, key):
        config = self.device_map[key]
        device_config = DeviceConfiguration(config)
        item = {
            'id': key,
            'name': device_config.get_name(),
            'stylers': device_config.get_stylers()
        }
        return item

    def items(self):
        item_list = []
        sorted_keys = sorted([key for key in self.device_map.keys()])
        for key in sorted_keys:
            item_list.append(self.get_item(key))
        return item_list
