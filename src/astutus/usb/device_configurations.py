import copy
import logging
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.log
import astutus.util
import astutus.util.pci


logger = logging.getLogger(__name__)


class DeviceConfiguration(dict):

    @staticmethod
    def make_pci_configuration(data, command_runner=astutus.util.run_cmd):
        # PCI configuration is determined from the lspci command, rather
        # than what is stored in the configuration file.
        # Not really sure why the /sys/device names append '0000:' before the slot.
        slot = data['dirname'][5:]
        config = {
            "color": "cyan",
            "description_template": '{Device}',
            'name': slot,
        }
        return DeviceConfiguration(config, command_runner)

    @staticmethod
    def make_generic_usb_configuration(data, command_runner=astutus.util.run_cmd):
        config = {
            'name_of_config': 'Generic USB',
            'color': 'blue',
            'description_template': None,
        }
        return DeviceConfiguration(config, command_runner)

    @staticmethod
    def make_generic_other_configuration(data, command_runner=astutus.util.run_cmd):
        config = {
            "color": "cyan",
            "description_template": None,
            'name_of_config': 'Generic Other',
        }
        return DeviceConfiguration(config, command_runner)

    def __init__(self, config, command_runner=astutus.util.run_cmd):
        self.config = config
        # Command runner is a dependency injection point to make code more testable
        self.command_runner = command_runner
        config['stylers'] = self.stylers
        super().update(config)

    def __repr__(self):
        return f"DeviceConfiguration(config={self.config})"

    def find_tty(self):
        return self.config.get('find_tty')

    @property
    def idx(self):
        return self.config['idx']

    @property
    def name(self):
        return self.config['name_of_config']

    @property
    def stylers(self):
        stylers = self.config.get('stylers')
        if stylers is None:
            # This is a simple config, where style attributes are directly expressed in the configuration.
            # So, dynamically create a single styler, with no special selection attributes,
            # and return that as a list
            styler = copy.deepcopy(self.config)
            if styler.get("name_of_config"):
                del styler["name_of_config"]  # A styler is not a config.
            if styler.get("name"):
                del styler["name"]  # A styler is not a config.
            stylers = [styler]
        # For now, apply color conversion at this point.
        for styler in stylers:
            styler['color'] = astutus.util.convert_color_for_html_input_type_color(styler.get('color'))
        return stylers

    def get_color(self, dirpath):
        """ Get color in #rrggbb format suitable for HTML input control. """
        styler = self.find_styler(dirpath)
        color = styler.get('color')
        if color is None:
            color = 'cyan'
        color = astutus.util.convert_color_for_html_input_type_color(color)
        return color

    def get_name(self):
        return self.config.get('name_of_config')

    def generate_description(self, dirpath, data):
        description_template = self.find_description_template(dirpath)
        try:
            description = description_template.format_map(data)
            return description
        except KeyError as exception:
            return f"exception: {exception}, description_template{description_template}, data{data}"

    def find_styler(self, dirpath):
        for styler in self.stylers:
            styler['color'] = astutus.util.convert_color_for_html_input_type_color(styler.get('color'))
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
