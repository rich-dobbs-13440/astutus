import logging
import re
import os
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.util


logger = logging.getLogger(__name__)

DEFAULT_BASEPATH = "/sys/devices"


def find_paths_for_vendor_and_product(vendor_id: str, product_id: str) -> List[str]:
    return_code, stdout, stderr = astutus.util.run_cmd(f'grep -r . -e "{vendor_id}" 2>/dev/null', cwd="/sys/devices")
    paths = []
    for line in stdout.splitlines():
        if "idVendor" in line:
            logger.debug(f"line: {line}")
            path_pattern = r'\.\/(.+)/idVendor:'
            matches = re.search(path_pattern, line)
            if not matches:
                assert False
            path = matches.group(1)
            logger.debug(f"path: {path}")
            paths.append(path)
    return paths


def find_busnum_and_devnum_for_sys_device(pci_path: str) -> Tuple[int, int]:
    if pci_path.startswith("/sys/devices"):
        abs_path = pci_path
    else:
        abs_path = f"/sys/devices/{pci_path}"
    return_code, stdout, stderr = astutus.util.run_cmd(f'cat {abs_path}/busnum')
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    busnum = int(stdout.strip())
    return_code, stdout, stderr = astutus.util.run_cmd(f'cat {abs_path}/devnum')
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    devnum = int(stdout.strip())
    return busnum, devnum


def find_vendor_info_from_busnum_and_devnum(busnum: int, devnum: int) -> Tuple[str, str, str]:
    """
    returns vendorid, productid, description
    """
    cmd = f"lsusb -s {busnum}:{devnum}"
    logger.debug(f"cmd: {cmd}")
    return_code, stdout, stderr = astutus.util.run_cmd(cmd)
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    vendor_info_pattern = r'([0-9,a-f]{4}):([0-9,a-f]{4}) (.*)'
    matches = re.search(vendor_info_pattern, stdout, re.IGNORECASE)
    if not matches:
        assert False, f"Parsing failed with line: {stdout} and vendor_info_pattern: {vendor_info_pattern}"
    vendorid = matches.group(1)
    productid = matches.group(2)
    description = matches.group(3)
    return vendorid, productid, description


def find_tty_from_pci_path(pci_path):
    cmd = 'find . -name tty*'
    return_code, stdout, stderr = astutus.util.run_cmd(cmd, cwd=pci_path)
    assert return_code == 0, stderr
    pattern = r'/(tty[\w]+)'
    matches = re.search(pattern, stdout)
    assert matches, stdout
    tty = matches.group(1)
    return tty


def find_tty_description_from_pci_path(pci_path: str) -> Tuple[str, str, str, str, str, str]:
    """ returns tty, busnum, devnum, vendorid, productid, description  """
    busnum, devnum = find_busnum_and_devnum_for_sys_device(pci_path)
    tty = find_tty_from_pci_path(pci_path)
    vendorid, productid, description = find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    return tty, busnum, devnum, vendorid, productid, description


def extract_specified_data(dirpath: str, filenames: List[str]) -> Dict:
    parent_dirpath, dirname = dirpath.rsplit('/', 1)
    data = {
        'dirpath': dirpath,
        'parent_dirpath': parent_dirpath,
        'dirname': dirname,
    }
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        return_code, stdout, stderr = astutus.util.run_cmd(f"cat {filepath}")
        if return_code != 0:
            continue
        data[filename] = stdout.strip()
    return data


def find_ilk_for_dirpath(dirpath):
    _, dirnames, filenames = next(os.walk(dirpath))
    if "busnum" in filenames and "devnum" in filenames:
        return "usb"
    elif "vendor" in filenames and "device" in filenames:
        return "pci"
    else:
        return "other"


USB_KEY_ATTRIBUTES = ['manufacturer', 'product', 'idVendor', 'idProduct', 'busnum', 'devnum', 'serial']

PCI_KEY_ATTRIBUTES = ['vendor', 'device', 'class']


def walk_basepath_for_ilk(basepath=None):
    if basepath is None:
        basepath = astutus.usb.usb_impl.DEFAULT_BASEPATH
    logger.info(f"Start walk for {basepath}")
    ilk_by_dirpath = {}
    usb_device_paths = []
    pci_device_paths = []
    other_device_paths = []
    for dirpath, dirnames, filenames in os.walk(basepath):
        if "busnum" in filenames and "devnum" in filenames:
            usb_device_paths.append(dirpath)
            ilk_by_dirpath[dirpath] = "usb"
        elif "vendor" in filenames and "device" in filenames:
            pci_device_paths.append(dirpath)
            ilk_by_dirpath[dirpath] = "pci"
        else:
            other_device_paths.append(dirpath)
            ilk_by_dirpath[dirpath] = "other"
    logger.info(f"End walk for {basepath}")
    return ilk_by_dirpath, usb_device_paths, pci_device_paths, other_device_paths
