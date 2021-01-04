import json
import logging
import os
import os.path
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


def get_settings_filepath():
    return os.path.join(get_user_data_path(), 'settings.json')


def get_settings_categories():
    try:
        with open(get_settings_filepath(), 'r') as settings_file:
            categories = json.load(settings_file)
        return categories
    except IOError:
        return {}


def get_setting(category_as_url, attribute, default_value):
    categories = get_settings_categories()
    category = categories.get(category_as_url, {})
    return category.get(attribute, default_value)


def persist_setting(category_as_url, attribute, value):
    create_user_data_dir_if_needed()
    categories = get_settings_categories()
    category = categories.get(category_as_url, {})
    category[attribute] = value
    categories[category_as_url] = category
    with open(get_settings_filepath(), 'w') as settings_file:
        json.dump(categories, settings_file, indent=4, sort_keys=True)
