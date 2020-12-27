import json
import logging
import re
import subprocess
import pathlib

logger = logging.getLogger(__name__)
# Which is better?
logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)


class RaspberryPiRuntimeError(RuntimeError):
    pass


class RaspberryPi():

    def __init__(self, *, db_data=None, ipv4=None):
        if db_data is not None:
            self.id = db_data.id
            self.ipv4 = db_data.ipv4
        elif ipv4 is not None:
            self.id = 35567
            self.ipv4 = ipv4
        else:
            raise ValueError("Must somehow provide ipv4")

    def parse_ifconfig_section_to_kvs(self, section):
        logger.debug(f"section: \n{section}")
        interface_pattern = r"(\w+): flags="
        matches = re.search(interface_pattern, section)
        interface = matches.group(1)
        logger.debug(f"interface: {interface}")
        parsed_section = {
            "content": f"{section}",
        }
        flags_pattern = r'flags=\d+<(.*)>'
        matches = re.search(flags_pattern, section, re.MULTILINE)
        if matches:
            flags_str = matches.group(1)
            parsed_section['flags'] = flags_str.split(',')
        mtu_pattern = r'mtu\s+(\d+)'
        matches = re.search(mtu_pattern, section, re.MULTILINE)
        if matches:
            mtu = int(matches.group(1))
            parsed_section['mtu'] = mtu
        inet_pattern = r"inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        matches = re.search(inet_pattern, section, re.MULTILINE)
        logger.debug(f"matches: {matches}")
        if matches:
            inet = matches.group(1)
            parsed_section['inet'] = inet
        return interface, parsed_section

    def get_ifconfig(self):
        cmd = f"ssh pi@{self.ipv4} /usr/sbin/ifconfig"
        logger.debug(f"cmd: {cmd}")
        output = subprocess.getoutput(cmd)
        sections = [section for section in output.split("\n\n")]
        results = {}
        for section in sections:
            key, value = self.parse_ifconfig_section_to_kvs(section)
            results[key] = value
        return json.dumps(results)

    def publish_wheels(self):
        working_dir = (pathlib.Path(__file__).parent.parent / 'wheels').absolute()
        logger.debug(f"working_dir: {working_dir}")
        cmd = f'/usr/bin/rsync --human-readable --verbose --progress * pi@{self.ipv4}:wheels'
        logger.debug(f"cmd: {cmd}")
        completed_process = subprocess.run(
            args=cmd,
            cwd=working_dir,
            shell=True,
            capture_output=True
        )
        logger.debug(f"type(completed_process.stdout): {type(completed_process.stdout)}")
        stdout = completed_process.stdout.decode("utf-8")
        logger.debug(f"stdout: \n{stdout}")
        if completed_process.returncode != 0:
            raise RaspberryPiRuntimeError(completed_process)
