import logging
import re
import subprocess

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


def find_bus_and_dev_for_sys_device(path) -> (int, int):
    abs_path = f"/sys/devices/{path}"
    return_code, stdout, stderr = run_cmd(f'cat {abs_path}/busnum')
    busnum = int(stdout.strip())
    return_code, stdout, stderr = run_cmd(f'cat {abs_path}/devnum')
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
    for path in find_paths_for_vendor_and_product('1a86', '7523'):
        if path in sym_link:
            busnum, devnum = find_bus_and_dev_for_sys_device(path)
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
        logger.debug(f"busnum_for_tty == busnum {busnum_for_tty == busnum}")
        if busnum_for_tty == busnum and devnum_for_tty == devnum:
            return tty
    raise ValueError(f"No tty USB device found for busnum: {busnum} devnum: {devnum}")
