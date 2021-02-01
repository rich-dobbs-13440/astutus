import logging
import re
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.util.pci
import pymemcache
import pymemcache.client.base

logger = logging.getLogger(__name__)


class DeviceClassifier(object):

    def __init__(self, *, expire_seconds):
        self.expire_seconds = expire_seconds
        # TODO: Cache socket.timeout for robustness
        self.cache = pymemcache.client.base.Client(
            'localhost', serde=pymemcache.serde.pickle_serde, connect_timeout=0.1, timeout=0.1)

        self.pci_device_info_map_key = self.make_key('pci_device_info_map')
        self.pci_device_info_map = self.cache.get(self.pci_device_info_map_key)
        if self.pci_device_info_map is None:
            self.pci_device_info_map = astutus.util.pci.get_slot_to_device_info_map_from_lspci()
            self.cache.set(self.pci_device_info_map_key, self.pci_device_info_map, expire=self.expire_seconds)

        self.aliases_key = self.make_key('astutus.usb.device_aliases.DeviceAliases')
        self.aliases = None  # lazy fetching, and necessary reading of aliases until used.

        self.map_dirpath_to_ilk_key = self.make_key('map_dirpath_to_ilk')
        self.map_dirpath_to_ilk = self.cache.get(self.map_dirpath_to_ilk_key)
        if self.map_dirpath_to_ilk is None:
            self.map_dirpath_to_ilk = {}

        self.map_dirpath_to_device_data_key = self.make_key('make_device_data_cache')
        self.map_dirpath_to_device_data = self.cache.get(self.map_dirpath_to_device_data_key)
        if self.map_dirpath_to_device_data is None:
            self.map_dirpath_to_device_data = {}

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
            else:
                raise NotImplementedError(f'No method identified for augmenting device date for field {field}')
            changed = True
        if changed:
            self.map_dirpath_to_device_data[dirpath] = device_data
            self.cache.set(
                self.map_dirpath_to_device_data_key,
                self.map_dirpath_to_device_data,
                expire=self.expire_seconds)
            logger.error("Wrote to cache")

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
                device_data['vendor'] = matches.group(1)
            elif line.startswith('idProduct'):
                matches = re.search(r'idProduct\s+\w+\s+([^\n]+)', line)
                device_data['product_text'] = matches.group(1)
            elif line.startswith('bDeviceClass '):
                matches = re.search(r'bDeviceClass\s+\w+\s+([^\n]+)', line)
                device_data['device_class'] = matches.group(1)
            elif line.startswith('bInterfaceClass '):
                matches = re.search(r'bInterfaceClass\s+\w+\s+([^\n]+)', line)
                interface_class_list.append(matches.group(1))
        device_data['interface_class_list'] = ','.join(interface_class_list)
