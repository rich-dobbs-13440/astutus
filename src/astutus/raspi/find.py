import subprocess
import logging
import re


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def parse_section_to_dictionary(section: str) -> {}:
    # Nmap scan report for 192.168.0.65
    # Host is up (0.00022s latency).
    # Not shown: 998 closed ports
    # PORT     STATE SERVICE
    # 22/tcp   open  ssh
    # 5900/tcp open  vnc
    # MAC Address: DC:A6:32:C5:94:AD (Raspberry Pi Trading)
    pattern = r'((\d{1,3}\.){3}\d{1,3})'
    matches = re.search(pattern, section)
    ipv4 = matches.group(0)
    logger.debug(f"ipv4: {ipv4}")
    parsed_section = {
        'ipv4': ipv4,
        'content': section,
    }
    return parsed_section


def search_using_nmap(ipv4: str, mask: int, filter: [str]):
    logger.debug(f"ipv4: {ipv4}")
    logger.debug(f"mask: {mask}")
    logger.debug(f"filter: {filter}")
    cmd = f"sudo nmap {ipv4}/{mask}"
    logger.debug(f"cmd: {cmd}")
    output = subprocess.getoutput(cmd)
    sections = [section for section in output.split("\n\n")]
    results = []
    for section in sections:
        for item in filter:
            if item in section:
                results.append(parse_section_to_dictionary(section))
                break
    return results
