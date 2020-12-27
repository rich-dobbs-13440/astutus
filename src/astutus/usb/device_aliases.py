import json
import logging
import os
import pathlib
import re

import astutus.usb.usb_impl

logger = logging.getLogger(__name__)


class DeviceAliases:

    def __init__(self, filepath):
        logger.info("Initializing AliasPaths")
        raw_aliases = self.read_raw_from_json(filepath)
        self.aliases = self.parse_raw_aliases(raw_aliases)
        # DevCode: self.aliases = self.parse_raw_aliases(self.sample_hardcoded_aliases)

    @staticmethod
    def write_raw_as_json(filepath, raw_aliases):
        with open(filepath, 'w') as config_file:
            json.dump(raw_aliases, config_file, indent=4, sort_keys=True)

    @staticmethod
    def read_raw_from_json(filepath=None):
        if filepath is None:
            filepath = pathlib.Path(__file__).resolve().parent / "device_aliases.json"
        with open(filepath, 'r') as config_file:
            raw_device_aliases = json.load(config_file)
        return raw_device_aliases

    @staticmethod
    def parse_raw_aliases(raw_aliases):
        # Parse the key into ancestor, current, and child axes:
        child_pattern = r'\[child(==|!=)([^\]]+)]'
        ancestor_pattern = r'\[ancestor(==|!=)([^\]]+)]'
        sibling_pattern = r'\[sibling(==|!=)([^\]]+)]'

        aliases = {}
        for key in raw_aliases.keys():
            logger.debug(f"key: {key}")
            check_str = key
            child_check = None
            if "[child" in check_str:
                logger.debug(f"child_pattern: {child_pattern}")
                matches = re.search(child_pattern, check_str)
                child_check = (matches.group(1), matches.group(2))
                # Remove the child axes from the check string
                check_str = re.sub(child_pattern, '', check_str, 0, re.MULTILINE)
            ancestor_check = None
            if "[ancestor" in check_str:
                matches = re.search(ancestor_pattern, check_str)
                ancestor_check = (matches.group(1), matches.group(2))
                # Remove the ancestor axes from the key
                check_str = re.sub(ancestor_pattern, '', check_str, 0, re.MULTILINE)
            sibling_check = None
            if "[sibling" in check_str:
                matches = re.search(sibling_pattern, check_str)
                sibling_check = (matches.group(1), matches.group(2))
                # Remove the ancestor axes from the key
                check_str = re.sub(sibling_pattern, '', check_str, 0, re.MULTILINE)
            # After removing the other axes, will be just left with the current key, which
            # implicitly has the equality operator.
            current_check = ('==', check_str)
            aliases[(ancestor_check, current_check, child_check, sibling_check)] = raw_aliases[key]
        return aliases

    @staticmethod
    def matches_as_usb_node(dirpath, value):
        if value.startswith('pci('):
            return False
        data = astutus.usb.usb_impl.extract_specified_data('', dirpath, ['idVendor', 'idProduct'])
        vendor = data.get('idVendor')
        product = data.get('idProduct')
        if vendor is not None and product is not None:
            id = f"{vendor}:{product}"
            if id == value:
                return True
        return False

    @staticmethod
    def matches_as_pci_node(dirpath, value):
        if not value.startswith('pci('):
            return False
        data = astutus.usb.usb_impl.extract_specified_data('', dirpath, ['vendor', 'device'])
        vendor = data.get('vendor')
        device = data.get('device')
        if vendor is not None and device is not None:
            id = f"pci({vendor}:{device})"
            if id == value:
                return True
        return False

    def sibling_passes(self, check, dirpath):
        if check is None:
            return True
        operator, value = check
        # Only implementing equality operator now.
        assert operator == "=="
        parent_dirpath, current = dirpath.rsplit('/', 1)
        if self.has_usb_child(parent_dirpath, value):
            return True
        if value.startswith('pci('):
            raise NotImplementedError()
        return False

    def ancestor_passes(self, check, dirpath):
        if check is None:
            return True
        operator, value = check
        # Only implementing equality operator now.
        assert operator == "=="
        logger.debug(f"dirpath: {dirpath}")
        a_dirpath, current = dirpath.rsplit('/', 1)
        while a_dirpath != '/sys/devices':
            if self.matches_as_usb_node(a_dirpath, value):
                return True
            if self.matches_as_pci_node(a_dirpath, value):
                return True
            a_dirpath, current = a_dirpath.rsplit('/', 1)
        return False

    def usb_child_passes(self, check, dirpath):
        if check is None:
            return True
        operator, value = check
        # Only implementing equality operator now.
        assert operator == "=="
        if self.has_usb_child(dirpath, value):
            return True
        return False

    def get(self, id, dirpath):
        filtered_aliases = []
        # Filter on current check first of all, with an exact match required.
        for checks in self.aliases.keys():
            logger.debug(f"checks: {checks}")
            if id == checks[1][1]:
                # Only equality supported for current access
                assert checks[1][0] == '=='
                filtered_aliases.append((checks, self.aliases[checks]))

        if len(filtered_aliases) > 0:
            logger.debug(f"id: {id}")
            logger.debug(f"tests: {len(filtered_aliases)}")
            # Sort by priority, so that first passed test is the most desirable one.

            def by_priority_key(item):
                return item[1].get('priority', '00')

            # TODO:  Should just sort them initially, rather than redoing each time.
            prioritized_aliases = sorted(filtered_aliases, key=by_priority_key, reverse=True)

            for alias in prioritized_aliases:
                checks, alias_value = alias
                logger.debug(f"checks: {checks}")
                logger.debug(f"alias_value: {alias_value}")
                # Parent test already been applied, no need to retest now.
                ancestor_check, _, child_check, sibling_check = checks
                if not self.ancestor_passes(ancestor_check, dirpath):
                    continue
                if not self.usb_child_passes(child_check, dirpath):
                    continue
                if not self.sibling_passes(sibling_check, dirpath):
                    continue
                return alias_value
        return None

    def label(self, name):
        for checks in self.aliases.keys():
            ancestor_check, current_check, child_check = checks
            current_check_value = current_check[1]
            if ancestor_check is None and current_check_value == name and child_check is None:
                alias = self.aliases[checks]
                return alias['label']
        return None

    def has_usb_child(self, dirpath, child_id):
        root, dirs, _ = next(os.walk(dirpath))
        logger.debug(f"dirs: {dirs}")
        for dir in dirs:
            subdirpath = os.path.join(root, dir)
            data = astutus.usb.usb_impl.extract_specified_data('', subdirpath, ['idVendor', 'idProduct'])
            id = f"{data.get('idVendor', '')}:{data.get('idProduct', '')}"
            if id == child_id:
                return True
        return False
