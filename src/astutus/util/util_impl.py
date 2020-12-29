import logging
import os
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
    try:
        stdout = completed_process.stdout.decode('utf-8')
    except UnicodeDecodeError:
        stdout = "<<not unicode>>"
    stderr = completed_process.stderr.decode('utf-8')
    return return_code, stdout, stderr


def get_user_data_path():
    return os.path.expanduser('~/.astutus')


def create_user_data_dir_if_needed():
    # Create the user's data directory if needed
    os.makedirs(get_user_data_path(), exist_ok=True)
