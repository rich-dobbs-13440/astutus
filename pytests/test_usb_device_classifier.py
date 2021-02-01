import json
import logging

import pytest
from astutus.usb import DeviceClassifier

logger = logging.getLogger(__name__)


def test_instantiation():

    deviceClassifier = DeviceClassifier(expire_seconds=5)
    assert deviceClassifier is not None


@pytest.mark.skip(reason="Need faking technique")
def test_get_ilk():
    for i in range(1000):
        deviceClassifier = DeviceClassifier(expire_seconds=10)
        smakn_path = '/sys/devices/pci0000:00/0000:00:07.0/0000:08:00.0/usb10/10-2/10-2.3/10-2.3.2'
        ilk = deviceClassifier.get_ilk(smakn_path)
        assert ilk == 'usb'


@pytest.mark.skip(reason="Need faking technique")
def test_get_device_data_ilk_usb():
    for i in range(1000):
        deviceClassifier = DeviceClassifier(expire_seconds=10)
        smakn_path = '/sys/devices/pci0000:00/0000:00:07.0/0000:08:00.0/usb10/10-2/10-2.3/10-2.3.2'
        device_data = deviceClassifier.get_device_data(smakn_path)
        assert device_data['ilk'] == 'usb', device_data

    logger.error(json.dumps(device_data, indent=2, sort_keys=True))


@pytest.mark.skip(reason="Need faking technique")
def test_get_device_data_ilk_pci():
    for i in range(1000):
        deviceClassifier = DeviceClassifier(expire_seconds=10)
        pci_path = '/sys/devices/pci0000:00/0000:00:07.0'
        device_data = deviceClassifier.get_device_data(pci_path)
        assert device_data['ilk'] == 'pci', device_data
    # logger.error(json.dumps(device_data, indent=2, sort_keys=True))


@pytest.mark.skip(reason="Need faking technique")
def test_get_device_data_ilk_other():
    for i in range(1000):
        deviceClassifier = DeviceClassifier(expire_seconds=10)
        other_path = '/sys/devices/pci0000:00'
        device_data = deviceClassifier.get_device_data(other_path)
        assert device_data['ilk'] == 'other', device_data
    # logger.error(json.dumps(device_data, indent=2, sort_keys=True))


@pytest.mark.skip(reason="Need faking technique")
def test_get_device_data_ilk_other_sys():
    for i in range(1000):
        deviceClassifier = DeviceClassifier(expire_seconds=10)
        other_path = '/sys/devices'
        device_data = deviceClassifier.get_device_data(other_path)
        assert device_data['ilk'] == 'other', device_data
    # logger.error(json.dumps(device_data, indent=2, sort_keys=True))


@pytest.mark.skip(reason="Need faking technique")
def test_get_device_data_ilk_other_sys_nodepath():
    for i in range(1000):
        deviceClassifier = DeviceClassifier(expire_seconds=10)
        other_path = '/sys/devices'
        device_data = deviceClassifier.get_device_data(other_path, ['nodepath'])
        assert device_data['ilk'] == 'other', device_data
    # logger.error(json.dumps(device_data, indent=2, sort_keys=True))


@pytest.mark.skip(reason="Need faking technique")
def test_get_device_data_ilk_usb_augment():
    for i in range(1000):
        deviceClassifier = DeviceClassifier(expire_seconds=30)
        smakn_path = '/sys/devices/pci0000:00/0000:00:07.0/0000:08:00.0/usb10/10-2/10-2.3/10-2.3.2'
        extra_fields = [
            'vendor', 'product_text', 'device_class', 'tty', 'nodepath'
        ]
        device_data = deviceClassifier.get_device_data(smakn_path, extra_fields)
        assert device_data['ilk'] == 'usb', device_data
    # logger.error(json.dumps(device_data, indent=2, sort_keys=True))
