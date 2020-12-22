import subprocess
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
                results.append(section)
                break
    return results
