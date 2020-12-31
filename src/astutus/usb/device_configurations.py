import json
import logging
import os
import shutil

import astutus.log

logger = logging.getLogger(__name__)


class DeviceConfiguration(object):

    def __init__(self, config):
        self.config = config

    def find_tty(self):
        return self.config.get('find_tty')

    def get_template_thing(self):
        return self.config.get('description_template')

    def get_color(self):
        return self.config['color']

    def get_name(self):
        return self.config.get('name_of_config')

    def generate_description(self, dirpath, data):
        description_template = self.find_description_template(dirpath)
        description = description_template.format_map(data)
        return description

    def find_description_template(self, dirpath):
        # The config may directly have a simple template, or something that
        # can select or generate a template.
        template_thing = self.get_template_thing()
        if isinstance([], type(template_thing)):
            # If it is a list, then currently it contain selectors.
            for item in template_thing:
                if item.get('test') == 'value_in_stdout':
                    cmd = item.get('cmd')
                    if cmd is None:
                        raise ValueError('cmd must be given for test value_in_stdout')
                    _, stdout, stderr = astutus.util.run_cmd(cmd, cwd=dirpath)
                    if item.get('value') in stdout:
                        description_template = item.get('description_template')
                        break
        else:
            # If none of the above, the template thing is just a template.
            description_template = template_thing
        if description_template is None:
            description_template = "{description}"
        return description_template


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
            return DeviceConfiguration({
                "color": "cyan",
                "description_template": None,
                'name_of_config': 'Generic PCI',
            })
        else:
            return DeviceConfiguration({
                "color": "cyan",
                "description_template": None,
                'name_of_config': 'Generic Other',
            })

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
        return DeviceConfiguration(characteristics)

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
