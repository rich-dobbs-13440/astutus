import subprocess
import re


def run_cmd(cmd: str, *, cwd: str = None) -> (int, str, str):
    completed_process = subprocess.run(
            args=cmd,
            cwd=cwd,
            shell=True,
            capture_output=True
        )
    return completed_process.returncode, completed_process.stdout.decode('utf-8'), completed_process.stderr.decode('utf-8')


def find_paths_for_vendor_and_product(vendor_id: str, product_id: str):
    return_code, stdout, stderr = run_cmd(f'grep -r . -e "{vendor_id}" 2>/dev/null', cwd="/sys/devices")
    print()
    paths = []
    for line in stdout.splitlines():
        if "idVendor" in line:
            print(f"line: {line}")
            path_pattern = r'\.\/(.+)/idVendor:'
            matches = re.search(path_pattern, line)
            if not matches:
                assert False
            path = matches.group(1)
            print(f"path: {path}")
            paths.append(path)
    return paths


def find_bus_and_dev_for_sys_device(path):
    abs_path = f"/sys/devices/{path}"
    return_code, stdout, stderr = run_cmd(f'cat {abs_path}/busnum')
    busnum = stdout.strip()
    return_code, stdout, stderr = run_cmd(f'cat {abs_path}/devnum')
    devnum = stdout.strip()
    return busnum, devnum


def find_sym_link_for_tty(tty):
    return_code, stdout, stderr = run_cmd(f"ls -l {tty}")
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    print(f"stdout: {stdout}")
    major_minor_pattern = r"dialout\s+(\d+),\s+(\d+)\s"
    matches = re.search(major_minor_pattern, stdout)
    major, minor = matches.group(1), matches.group(2)
    print(f"major: {major}  minor: {minor}")
    cmd = f"ls -l /sys/dev/char/{major}:{minor}"
    print(f"cmd: {cmd}")
    return_code, stdout, stderr = run_cmd(cmd)
    if return_code != 0:
        raise RuntimeError(return_code, stderr, stdout)
    print(f"stdout: {stdout}")
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


def test_find_dev_tty_for_each_relay():
    return_code, stdout, stderr = run_cmd('lsusb -d 1a86:7523')
    # Bus 010 Device 022: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    # Bus 010 Device 021: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    tty = '/dev/ttyUSB0'
    busnum, devnum = find_busnum_and_devnum_for_tty(tty)
    print(f"tty: {tty}  busnum: {busnum}  devnum:{devnum}")
    tty = '/dev/ttyUSB1'
    busnum, devnum = find_busnum_and_devnum_for_tty(tty)
    print(f"tty: {tty}  busnum: {busnum}  devnum:{devnum}")


def test_find_usb_devices():
    cmd = 'ls /dev/*USB*'
    completed_process = subprocess.run(
        args=cmd,
        shell=True,
        capture_output=True
    )
    if completed_process.returncode != 0:
        raise RuntimeError('Should hit this')
    print(f"stdout: \n{completed_process.stdout.decode('utf-8')}")
    devices = completed_process.stdout.decode('utf-8').splitlines()
    for device in devices:
        cmd = f"ls -l {device}"
        completed_process = subprocess.run(
            args=cmd,
            shell=True,
            capture_output=True
        )
        if completed_process.returncode != 0:
            raise RuntimeError('Should not hit this')
        stdout = completed_process.stdout.decode('utf-8')
        print(f"stdout: \n{stdout}")
        major_minor_pattern = r"dialout\s+(\d+),\s+(\d+)\s"
        matches = re.search(major_minor_pattern, stdout)
        major, minor = matches.group(1), matches.group(2)
        print(f"major: {major}  minor: {minor}")
        cmd = f"ls -l /sys/dev/char/{major}:{minor}"
        print(f"cmd: {cmd}")
        completed_process = subprocess.run(
            args=cmd,
            shell=True,
            capture_output=True
        )
        if completed_process.returncode != 0:
            raise RuntimeError('Should not hit this')
        stdout = completed_process.stdout.decode('utf-8')
        print(f"stdout: \n{stdout}")
        devices_pattern = r"/(devices/.*/)usb"
        matches = re.search(devices_pattern, stdout)
        devices_path = matches.group(1)
        print(f"devices_path: \n{devices_path}")
        # cmd = f"cat /sys/{devices_path}/busnum"
        # print(f"cmd: {cmd}")
        # completed_process = subprocess.run(
        #     args=cmd,
        #     shell=True,
        #     capture_output=True
        # )
        # if completed_process.returncode != 0:
        #     raise RuntimeError(completed_process.stderr.decode('utf8'))
        # busnum = completed_process.stdout.decode('utf-8')
        # print(f"busnum: \n{busnum}")
        # cmd = f"cat /sys/{devices_path}/devnum"
        # print(f"cmd: {cmd}")
        # completed_process = subprocess.run(
        #     args=cmd,
        #     shell=True,
        #     capture_output=True
        # )
        # if completed_process.returncode != 0:
        #     raise RuntimeError(completed_process.stderr.decode('utf8'))
        # devnum = completed_process.stdout.decode('utf-8')
        # print(f"devnum: \n{devnum}")