import logging
import time
import pathlib

import astutus.usb
import pytest


logger = logging.getLogger(__name__)


def test_find_dev_tty_for_each_relay():
    tty = '/dev/ttyUSB0'
    busnum, devnum = astutus.usb.find_busnum_and_devnum_for_tty(tty)
    logger.info(f"tty: {tty}  busnum: {busnum}  devnum:{devnum}")
    if busnum < 0:
        logger.warning(f"No tty {tty} found in system at this time")
    tty = '/dev/ttyUSB1'
    busnum, devnum = astutus.usb.find_busnum_and_devnum_for_tty(tty)
    logger.info(f"tty: {tty}  busnum: {busnum}  devnum:{devnum}")
    if busnum < 0:
        logger.warning(f"No tty {tty} found in system at this time")


def test_find_tty_from_busnum_and_devnum():
    tty_original = '/dev/ttyUSB0'
    busnum, devnum = astutus.usb.find_busnum_and_devnum_for_tty(tty_original)
    if busnum < 0:
        msg = f"No tty {tty_original} found in system at this time"
        logger.warning(msg)
        pytest.skip(msg)
    tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
    logger.info(f"busnum: {busnum} devnum: {devnum} tty: {tty}")
    assert tty == tty_original


def test_current_selector():
    selector = 'usb(1a86:7523)'
    pci_paths = astutus.usb.find_pci_paths(selector)
    assert len(pci_paths) == 2


def logger_info_pci_paths(pci_paths):
    if len(pci_paths) == 1 or len(pci_paths) == 0:
        logger.info(f"pci_paths: {pci_paths}")
        return
    indent = '\n                               '
    lines = indent.join(pci_paths)
    logger.info(f"pci_paths: {indent}{lines}")


def test_sibling_selector():
    selector = 'usb(1a86:7523)[sibling==usb(0bda:8153)]'
    pci_paths = astutus.usb.find_pci_paths(selector)
    logger_info_pci_paths(pci_paths)
    assert len(pci_paths) == 1


def test_ancestor_selector():
    selector = '[ancestor==usb(05e3:0610)]usb(1a86:7523)'
    pci_paths = astutus.usb.find_pci_paths(selector)
    if len(pci_paths) == 0:
        msg = "No relays plugged into Genesys Logic, Inc. 4-port hubs found in system at this time"
        logger.warning(msg)
        logger.info("These hubs are used in various products such as ONN hubs and TECKNET USB Ethernet adapters.")
        pytest.skip(msg)
    logger_info_pci_paths(pci_paths)


def test_ancestor_sibling_selector():
    smakin_relay_in_tecknet_selector = '[ancestor==usb(05e3:0610)]usb(1a86:7523)[sibling==usb(0bda:8153)]'
    pci_paths = astutus.usb.find_pci_paths(smakin_relay_in_tecknet_selector)
    assert len(pci_paths) == 1
    logger_info_pci_paths(pci_paths)


def test_usb_relay():
    smakin_relay_in_tecknet_selector = '[ancestor==usb(05e3:0610)]usb(1a86:7523)[sibling==usb(0bda:8153)]'
    pci_paths = astutus.usb.find_pci_paths(smakin_relay_in_tecknet_selector)
    logger_info_pci_paths(pci_paths)
    assert len(pci_paths) == 1
    tty, _, _, vendorid, productid, _ = astutus.usb.find_tty_description_from_pci_path(pci_paths[0])
    assert vendorid == '1a86'
    assert productid == '7523'
    with astutus.usb.UsbRelayLcus1(tty) as relay:
        relay.turn_on()
        time.sleep(3)
        relay.turn_off()
        time.sleep(3)
        relay.turn_on()
        time.sleep(3)
        relay.turn_off()


# def test_find_characteristics_from_pci_path():
#     pci_path = 'pci0000:00/0000:00:07.0/0000:05:00.0/usb10/10-1/10-1.2/10-1.2.2'
#     tty, busnum, devnum, vendorid, productid, description = astutus.usb.find_tty_description_from_pci_path(pci_path)
#     logger.info(f"busnum: {busnum}")
#     logger.info(f"devnum: {devnum}")
#     logger.info(f"tty: {tty}")
#     logger.info(f"vendorid: {vendorid}")
#     logger.info(f"productid: {productid}")
#     logger.info(f"description: {description}")
#     assert tty is not None
#     assert description == 'QinHeng Electronics HL-340 USB-Serial adapter'
#     assert vendorid == '1a86'
#     assert productid == '7523'


def test_print_tree():
    device_aliases_filepath = pathlib.Path(__file__).resolve().parent / "test_data/device_aliases.json"
    astutus.usb.print_tree(device_aliases_filepath)


def test_device_configuration_write_to_file():
    device_configurations = astutus.usb.DeviceConfigurations()
    device_configurations.write_as_json("device_configurations.json")


def test_device_configuration_read_from_file():
    device_configurations = astutus.usb.DeviceConfigurations()
    device_configurations.read_from_json()


def test_device_aliases_write_raw_as_json():
    sample_hardcoded_aliases = {
        'pci(0x1002:0x5a19)': {
            'order': '10', 'label': 'wendy:front', 'color': 'cyan'},
        'pci(0x1002:0x5a1b)': {
            'order': '20', 'label': 'wendy:back:row2', 'color': 'blue'},
        '05e3:0610[child==0bda:8153]': {
            'priority': 50, 'order': '30', 'label': 'TECKNET USB 2.0', 'color': 'orange'},
        '05e3:0612[child==0bda:8153]': {
            'priority': 50, 'order': '40', 'label': 'TECKNET USB 3.0', 'color': 'orange'},
        '[ancestor==05e3:0612]1a86:7523[sibling==0bda:8153]': {
            'priority': 99, 'order': '40', 'label': 'SMAKIN Relay into TECKNET USB 3.0', 'color': 'fushia'},
        '[ancestor==05e3:0610]1a86:7523[sibling==0bda:8153]': {
            'priority': 98, 'order': '40', 'label': 'SMAKIN Relay into TECKNET USB 2.0', 'color': 'fushia'},
        '1a86:7523[sibling==05e3:0610]': {
            'priority': 98, 'order': '40', 'label': 'SMAKIN Relay into ONN', 'color': 'fushia'},
    }
    # TODO: Write this to temporary directory
    astutus.usb.DeviceAliases.write_raw_as_json('device_aliases.json', sample_hardcoded_aliases)
