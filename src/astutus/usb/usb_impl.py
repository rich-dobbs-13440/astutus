import logging
import re
import os

import astutus.util


logger = logging.getLogger(__name__)


def find_paths_for_vendor_and_product(vendor_id: str, product_id: str):
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


def find_busnum_and_devnum_for_sys_device(pci_path) -> (int, int):
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


def find_sym_link_for_tty(tty):
    return_code, stdout, stderr = astutus.util.run_cmd(f"ls -l {tty}")
    if return_code == 2:
        return None
    elif return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    logger.debug(f"stdout: {stdout}")
    major_minor_pattern = r"dialout\s+(\d+),\s+(\d+)\s"
    matches = re.search(major_minor_pattern, stdout)
    major, minor = matches.group(1), matches.group(2)
    logger.debug(f"major: {major}  minor: {minor}")
    cmd = f"ls -l /sys/dev/char/{major}:{minor}"
    logger.debug(f"cmd: {cmd}")
    return_code, stdout, stderr = astutus.util.run_cmd(cmd)
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    logger.debug(f"stdout: {stdout}")
    sym_link = stdout.strip()
    return sym_link


def find_busnum_and_devnum_for_sym_link(sym_link):
    for pci_path in find_paths_for_vendor_and_product('1a86', '7523'):
        if pci_path in sym_link:
            busnum, devnum = find_busnum_and_devnum_for_sys_device(pci_path)
            return busnum, devnum
    raise ValueError(f"No busnum, devnum found for symbolic link: {sym_link}")


def find_busnum_and_devnum_for_tty(tty):
    sym_link = find_sym_link_for_tty(tty)
    if sym_link is None:
        return -1, -1
    busnum, devnum = find_busnum_and_devnum_for_sym_link(sym_link)
    return busnum, devnum


def find_tty_for_busnum_and_devnum(busnum, devnum):
    logger.debug(f"Searching for tty for busnum: {busnum} devnum: {devnum}")
    # Issue:  The coding convention may be platform dependent
    return_code, stdout, stderr = astutus.util.run_cmd('ls /dev/tty*USB* /dev/tty*usb*')
    if return_code == 0:
        pass
    elif return_code == 2:
        pass
    else:
        raise RuntimeError(return_code, stderr, stdout)
    tty_devices = stdout.splitlines()
    for tty in tty_devices:
        busnum_for_tty, devnum_for_tty = find_busnum_and_devnum_for_tty(tty)
        logger.debug(f"tty: '{tty}' busnum_for_tty: '{busnum_for_tty}' devnum_for_tty: '{devnum_for_tty}'")
        if busnum_for_tty == busnum and devnum_for_tty == devnum:
            return tty
    raise ValueError(f"No tty USB device found for busnum: {busnum} devnum: {devnum}")


def find_vendor_info_from_busnum_and_devnum(busnum: int, devnum: int):
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


def find_tty_description_from_pci_path(pci_path):
    busnum, devnum = find_busnum_and_devnum_for_sys_device(pci_path)
    tty = find_tty_for_busnum_and_devnum(busnum, devnum)
    vendorid, productid, description = find_vendor_info_from_busnum_and_devnum(busnum, devnum)
    return tty, busnum, devnum, vendorid, productid, description


def extract_specified_data(tag, dirpath, filenames):
    data = {'tag': tag}
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        return_code, stdout, stderr = astutus.util.run_cmd(f"cat {filepath}")
        if return_code != 0:
            continue
        data[filename] = stdout.strip()
    return data


USB_KEY_ATTRIBUTES = ['manufacturer', 'product', 'idVendor', 'idProduct', 'busnum', 'devnum', 'serial']

PCI_KEY_ATTRIBUTES = ['vendor', 'device', 'class']
