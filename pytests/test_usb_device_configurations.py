import logging
import json

from astutus.usb import DeviceConfigurations
import astutus.util
import pytest

logger = logging.getLogger(__name__)


def test_instantiation():
    device_configurations = DeviceConfigurations()
    logger.info(f"device_configurations: {device_configurations}")


@pytest.mark.skip(reason="")
def test_to_generate_command_runner_data():
    # This is a work in progress.  Really need use with relevant data.
    command_results = {}

    def recording_command_runner(cmd, cwd=None):
        if cwd is None:
            return_code, stdout, stderr = astutus.util.run_cmd(cmd)
        else:
            return_code, stdout, stderr = astutus.util.run_cmd(cmd, cwd=cwd)
        key = (cmd, cwd)
        value = {
           "return_code": return_code,
           "stdout": stdout,
           "stderr": stderr,
        }
        command_results[key] = value
        return return_code, stdout, stderr

    device_configurations = DeviceConfigurations(filepath=None, command_runner=recording_command_runner)

    data = {
        'idVendor': '046d',
        'idProduct': 'c52b',

    }
    device_configuration = device_configurations.find_usb_configuration(data)

    dirpath = "needs to be determined."
    device_configuration.find_description_template(dirpath)

    with open('device_configurations_command_record.json', 'w') as config_file:
        json.dump(command_results, config_file, indent=4, sort_keys=True)
