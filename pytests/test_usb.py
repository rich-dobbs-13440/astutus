import logging
import time

import astutus.usb


logger = logging.getLogger(__name__)


def test_find_dev_tty_for_each_relay():
    # return_code, stdout, stderr = run_cmd('lsusb -d 1a86:7523')
    # if return_code != 0:
    #     raise RuntimeError(return_code, stderr, stdout)
    # # Bus 010 Device 022: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    # # Bus 010 Device 021: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    tty = '/dev/ttyUSB0'
    busnum, devnum = astutus.usb.find_busnum_and_devnum_for_tty(tty)
    logger.debug(f"tty: {tty}  busnum: {busnum}  devnum:{devnum}")
    tty = '/dev/ttyUSB1'
    busnum, devnum = astutus.usb.find_busnum_and_devnum_for_tty(tty)
    logger.debug(f"tty: {tty}  busnum: {busnum}  devnum:{devnum}")


def test_find_tty_from_busnum_and_devnum():
    busnum, devnum = 10, 21
    tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
    logger.info(f"busnum: {busnum} devnum: {devnum} tty: {tty}")


def test_usb_relay():
    pci_path = 'pci0000:00/0000:00:07.0/0000:05:00.0/usb10/10-1/10-1.2/10-1.2.2'
    tty, _, _, vendorid, productid, _ = astutus.usb.find_tty_description_from_pci_path(pci_path)
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


def test_find_characteristics_from_pci_path():
    pci_path = 'pci0000:00/0000:00:07.0/0000:05:00.0/usb10/10-1/10-1.2/10-1.2.2'
    tty, busnum, devnum, vendorid, productid, description = astutus.usb.find_tty_description_from_pci_path(pci_path)
    logger.info(f"busnum: {busnum}")
    logger.info(f"devnum: {devnum}")
    logger.info(f"tty: {tty}")
    logger.info(f"vendorid: {vendorid}")
    logger.info(f"productid: {productid}")
    logger.info(f"description: {description}")
    assert tty is not None
    assert description == 'QinHeng Electronics HL-340 USB-Serial adapter'
    assert vendorid == '1a86'
    assert productid == '7523'


def test_print_tree():
    astutus.usb.print_tree()
