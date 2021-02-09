import logging
import re
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.util.pci
import pymemcache
import pymemcache.client.base

logger = logging.getLogger(__name__)


class Check(object):

    def __init__(self, field: str, operator: str, value: str):
        self.field = field
        self.operator = operator
        self.value = value

    def as_dict(self) -> str:
        return {
            'field': self.field,
            'operator': self.operator,
            'value': self.value,
        }


class Rule(object):
    """ Base class for rule """

    def __init__(self, checks: List[Check]):
        self.checks = []

    def applies(self, device_data: Dict[str, str]) -> bool:
        if self.checks is None:
            return True
        for check in self.checks:
            data_value = device_data.get(check.field)
            if check.operator == 'equals':
                if check.value != data_value:
                    return False
            elif check.operator == 'contains':
                if data_value is None:
                    return False
                if check.value not in data_value:
                    return False
            else:
                raise NotImplementedError(f'operator: {check.operator}')
        return True


extra_fields_for_ilk = {
    'usb': ['nodepath', 'vendor', 'product_text', 'device_class'],
    'pci': ['nodepath'],
}


# Make this a plain function, to support eventual registration process
# for custom field searchers
def get_logitech_unifying_receiver_input_type(dirpath: str, device_data: Dict[str, str]):
    tests = [
        {
            'cmd': 'grep -r . -e "mouse" 2>/dev/null',
            'value': 'mouse',
        },
        {
            'cmd': 'grep -r . -e "kbd-numlock" 2>/dev/null',
            'value': 'kbd-numlock',
            'type': 'keyboard'
        }
    ]
    input_types = []
    for test in tests:
        cmd = test.get('cmd')
        _, stdout, stderr = astutus.util.run_cmd(cmd, cwd=dirpath)
        if test.get('value') in stdout:
            input_types.append(test.get('type'))
    return ','.join(input_types)


class DeviceClassifierException(Exception):
    pass


class DeviceClassifier(object):

    def __init__(self, *, expire_seconds):

        saved_exception = None
        try:
            self.expire_seconds = expire_seconds
            # TODO: Cache socket.timeout for robustness
            # self.cache = pymemcache.client.base.Client(
            #     'localhost', serde=pymemcache.serde.pickle_serde, connect_timeout=0.1, timeout=0.1)
            self.cache = pymemcache.client.base.Client(
                '127.0.0.1', serde=pymemcache.serde.pickle_serde, connect_timeout=1., timeout=1.)

            self.pci_device_info_map_key = self.make_key('pci_device_info_map')
            self.pci_device_info_map = self.cache.get(self.pci_device_info_map_key)
            if self.pci_device_info_map is None:
                self.pci_device_info_map = astutus.util.pci.get_slot_to_device_info_map_from_lspci()
                self.cache.set(self.pci_device_info_map_key, self.pci_device_info_map, expire=self.expire_seconds)

            self.map_dirpath_to_ilk_key = self.make_key('map_dirpath_to_ilk')
            self.map_dirpath_to_ilk = self.cache.get(self.map_dirpath_to_ilk_key)
            if self.map_dirpath_to_ilk is None:
                self.map_dirpath_to_ilk = {}

            self.map_dirpath_to_device_data_key = self.make_key('make_device_data_cache')
            self.map_dirpath_to_device_data = self.cache.get(self.map_dirpath_to_device_data_key)
            if self.map_dirpath_to_device_data is None:
                self.map_dirpath_to_device_data = {}
        except ConnectionRefusedError as exception:
            logger.error(exception)
            saved_exception = DeviceClassifierException(f'Need to install memcached! {exception}')
        if saved_exception is not None:
            raise saved_exception

    def make_key(self, short_key):
        key = f'{type(self)}-{short_key}'.replace(' ', '=')
        return key

    def get_ilk(self, dirpath: str) -> str:
        ilk = self.map_dirpath_to_ilk.get(dirpath)
        if ilk is None:
            ilk = astutus.usb.usb_impl.find_ilk_for_dirpath(dirpath)
            self.map_dirpath_to_ilk[dirpath] = ilk
            self.cache.set(
                self.map_dirpath_to_ilk_key,
                self.map_dirpath_to_ilk,
                expire=self.expire_seconds)
        return ilk

    def get_pci_device_info(self, dirpath: str) -> Dict[str, str]:
        parent_dirpath, dirname = dirpath.rsplit('/', 1)
        ilk = self.get_ilk(dirpath)
        if ilk == 'pci':
            pci_device_info = astutus.util.pci.get_device_info_from_dirname(self.pci_device_info_map, dirname)
        else:
            pci_device_info = None
        return pci_device_info

    def get_device_data(self, dirpath: str, extra_fields: List[str] = []) -> Dict[str, str]:
        device_data = self.map_dirpath_to_device_data.get(dirpath)
        if device_data is None:
            ilk = self.get_ilk(dirpath)
            device_data = astutus.usb.tree.get_data_for_dirpath(
                ilk,
                dirpath,
                self.get_pci_device_info(dirpath))
            if ilk == 'pci':
                # Fix up pci keys to be more consistent with USB fields
                key_changes = [
                    ('Class', 'device_class'),
                    ('Slot', 'slot'),
                    ('Vendor', 'vendor'),
                    ('Device', 'product_text'),
                    ('SVendor', 'subsystem_vendor'),
                    ('SDevice', 'subsystem_device'),
                    ('NUMANode', 'numa_node'),
                    ('ProgIf', 'programming_interface_register')
                ]
            elif ilk == 'usb':
                self.augument_from_lsusb(device_data)
                key_changes = [
                    ('product', 'product_text'),
                ]
            else:
                key_changes = []
            for old_key, new_key in key_changes:
                value = device_data.get(old_key)
                if value is None:
                    continue
                device_data[new_key] = value
                device_data.pop(old_key, None)
            self.augment_device_data(dirpath, device_data, extra_fields)
            self.map_dirpath_to_device_data[dirpath] = device_data
            self.cache.set(
                self.map_dirpath_to_device_data_key,
                self.map_dirpath_to_device_data,
                expire=self.expire_seconds)
        self.augment_device_data(dirpath, device_data, extra_fields)
        return device_data

    def augment_device_data(self, dirpath: str, device_data: Dict[str, str], extra_fields: List[str]):
        changed = False
        for field in extra_fields:
            if device_data.get(field) is not None:
                continue
            if field == 'tty':
                device_data['tty'] = astutus.usb.find_tty_from_pci_path(dirpath)
            elif field == 'vendor':
                self.augument_from_lsusb(device_data)
            elif field == 'product_text':
                self.augument_from_lsusb(device_data)
            elif field == 'device_class':
                self.augument_from_lsusb(device_data)
            elif field == 'nodepath':
                parent_dirpath = device_data['parent_dirpath']
                if parent_dirpath == '/sys':
                    device_data['nodepath'] = device_data['node_id']
                else:
                    parent_device_data = self.get_device_data(device_data['parent_dirpath'], ['nodepath'])
                    device_data['nodepath'] = parent_device_data['nodepath'] + '/' + device_data['node_id']
            elif field == 'logitech_unifying_receiver_input_type':
                device_data['logitech_unifying_receiver_input_type'] = get_logitech_unifying_receiver_input_type(
                    dirpath, device_data)
            else:
                raise NotImplementedError(f'No method identified for augmenting device date for field {field}')
            changed = True
        if changed:
            self.map_dirpath_to_device_data[dirpath] = device_data
            self.cache.set(
                self.map_dirpath_to_device_data_key,
                self.map_dirpath_to_device_data,
                expire=self.expire_seconds)
            logger.debug('Wrote to cache')

    def augument_from_lsusb(self, device_data: Dict[str, str]) -> None:
        cmd = f"lsusb -s {device_data['busnum']}:{device_data['devnum']} --verbose"
        return_code, stdout, stderr = astutus.util.run_cmd(cmd)
        if return_code != 0:
            raise RuntimeError(return_code, stderr, stdout)
        interface_class_list = []
        for line in stdout.splitlines():
            line = line.strip()
            if line.startswith('idVendor'):
                matches = re.search(r'idVendor\s+\w+\s+([^\n]+)', line)
                if matches:
                    device_data['vendor'] = matches.group(1)
                else:
                    assert False, line
            elif line.startswith('idProduct'):
                matches = re.search(r'idProduct\s+\w+\s+([^\n]+)', line)
                if matches:
                    device_data['product_text'] = matches.group(1)
                else:
                    # Fall back to parsing the line like this:
                    #  Bus 011 Device 002: ID 05e3:0626 Genesys Logic, Inc. USB3.1 Hub
                    matches = re.search(r'Bus\s+\d+\s+Device\s+\d+:\s+ID\s\w+:\w+\s([^\n]+)', stdout)
                    if matches:
                        vendor_and_product = matches.group(1)
                        device_data['product_text'] = vendor_and_product.replace(device_data['vendor'], '')
                    else:
                        # If this fails just fall back to the hex number.
                        device_data['product_text'] = line.replace('idProduct', '').strip()
            elif line.startswith('bDeviceClass '):
                matches = re.search(r'bDeviceClass\s+\w+\s+([^\n]+)', line)
                if matches:
                    device_data['device_class'] = matches.group(1)
                else:
                    _, device_data['device_class'] = line.rsplit(' ', 1)
            elif line.startswith('bInterfaceClass '):
                matches = re.search(r'bInterfaceClass\s+\w+\s+([^\n]+)', line)
                if matches:
                    interface_class_list.append(matches.group(1))
                else:
                    assert False, line
        device_data['interface_class_list'] = ','.join(interface_class_list)

    def get_rule(self, device_path: str, rules: List[Rule]) -> Rule:
        """ Return the idx and rule that will be used for this device path.

        This will be used to select the rule to be edited for a particular node
        on the device tree.

        """
        device_data = self.get_device_data(device_path)
        for rule in rules:
            if rule.applies(device_data):
                return rule
        return None

    def filter_device_paths_for_rule(self, rule: Rule, rules: List[Rule], input_device_paths: List[str]) -> List[str]:
        """ Find all dirpaths for which the provided rule would be used for node.

        Note: The rule must be a member of the rules list.  If it is not, the behavior is undefined.
        """
        filtered_device_paths = []
        for device_path in input_device_paths:
            rule_for_path = self.get_rule(device_path, rules)
            if rule_for_path.id == rule.id:
                filtered_device_paths.append(device_path)
        return filtered_device_paths
