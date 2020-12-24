import logging
import re
import subprocess
import treelib
import os
import astutus.util

logger = logging.getLogger(__name__)


def run_cmd(cmd: str, *, cwd: str = None) -> (int, str, str):
    completed_process = subprocess.run(
            args=cmd,
            cwd=cwd,
            shell=True,
            capture_output=True
        )
    return_code = completed_process.returncode
    stdout = completed_process.stdout.decode('utf-8')
    stderr = completed_process.stderr.decode('utf-8')
    return return_code, stdout, stderr


def find_paths_for_vendor_and_product(vendor_id: str, product_id: str):
    return_code, stdout, stderr = run_cmd(f'grep -r . -e "{vendor_id}" 2>/dev/null', cwd="/sys/devices")
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
    abs_path = f"/sys/devices/{pci_path}"
    return_code, stdout, stderr = run_cmd(f'cat {abs_path}/busnum')
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    busnum = int(stdout.strip())
    return_code, stdout, stderr = run_cmd(f'cat {abs_path}/devnum')
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    devnum = int(stdout.strip())
    return busnum, devnum


def find_sym_link_for_tty(tty):
    return_code, stdout, stderr = run_cmd(f"ls -l {tty}")
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    logger.debug(f"stdout: {stdout}")
    major_minor_pattern = r"dialout\s+(\d+),\s+(\d+)\s"
    matches = re.search(major_minor_pattern, stdout)
    major, minor = matches.group(1), matches.group(2)
    logger.debug(f"major: {major}  minor: {minor}")
    cmd = f"ls -l /sys/dev/char/{major}:{minor}"
    logger.debug(f"cmd: {cmd}")
    return_code, stdout, stderr = run_cmd(cmd)
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
    busnum, devnum = find_busnum_and_devnum_for_sym_link(sym_link)
    return busnum, devnum


def find_tty_for_busnum_and_devnum(busnum, devnum):
    logger.info(f"Searching for tty for busnum: {busnum} devnum: {devnum}")
    # Issue:  The coding convention may be platform dependent
    return_code, stdout, stderr = run_cmd('ls /dev/tty*USB* /dev/tty*usb*')
    if return_code == 0:
        pass
    elif return_code == 2:
        pass
    else:
        raise RuntimeError(return_code, stderr, stdout)
    tty_devices = stdout.splitlines()
    for tty in tty_devices:
        busnum_for_tty, devnum_for_tty = find_busnum_and_devnum_for_tty(tty)
        logger.info(f"tty: '{tty}' busnum_for_tty: '{busnum_for_tty}' devnum_for_tty: '{devnum_for_tty}'")
        if busnum_for_tty == busnum and devnum_for_tty == devnum:
            return tty
    raise ValueError(f"No tty USB device found for busnum: {busnum} devnum: {devnum}")


def find_vendor_info_from_busnum_and_devnum(busnum: int, devnum: int):
    return_code, stdout, stderr = run_cmd(f"lsusb -s {busnum}:{devnum}")
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    vendor_info_pattern = r'([0-9,a-e]{4}):([0-9,a-e]{4}) (.*)'
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


excluded_directories = [r'^power$', r'^msi_irqs$', r'^ep_\d\d$']


def exclude_directory(tag):

    for pattern in excluded_directories:
        if re.match(pattern, tag):
            return True
    return False


included_files = ['manufacturer', 'product']


class Directory(object):
    def __init__(self, tag, color="yellow"):
        self.tag = tag
        self.color = color

    @property
    def colorized(self):
        return self.tag


class Terminal(object):

    def __init__(self, filename, data, color="blue"):
        self.filename = filename
        self.data = data
        self.color = color

    @property
    def colorized(self):
        ansi = astutus.util.AnsiSequenceStack()
        start = ansi.push
        end = ansi.end
        return f"{self.filename} - {start(self.color)}{self.data}{end(self.color)}"


def print_tree():
    basepath = '/sys/devices/pci0000:00/0000:00:07.0/0000:05:00.0'
    tree = treelib.Tree()
    tag = "0000:00:07.0"
    tree.create_node(
        tag=tag, identifier="/sys/devices/pci0000:00/0000:00:07.0", parent=None, data=Directory(tag))

    # parent_id = "top"
    for dirpath, dirnames, filenames in os.walk(basepath):
        # print(dirpath)
        parent_path, tag = dirpath.rsplit("/", 1)
        if exclude_directory(tag):
            continue
        tree.create_node(tag=tag, identifier=dirpath,  parent=parent_path, data=Directory(tag))
        for filename in filenames:
            if filename in included_files:
                filepath = os.path.join(dirpath, filename)
                return_code, stdout, stderr = run_cmd(f"cat {filepath}")
                if return_code != 0:
                    raise RuntimeError(return_code, stderr, stdout)
                data = stdout.strip()
                print(f"filename: {filename} data: {data}")
                tree.create_node(tag=filename, identifier=filepath,  parent=dirpath, data=Terminal(filename, data))

    tree.show(data_property="colorized")
