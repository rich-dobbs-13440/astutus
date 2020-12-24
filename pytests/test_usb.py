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
    busnum, devnum = 10, 8
    tty = astutus.usb.find_tty_for_busnum_and_devnum(busnum, devnum)
    with astutus.usb.UsbRelayLcus1(tty) as relay:
        relay.turn_on()
        time.sleep(3)
        relay.turn_off()
        time.sleep(3)
        relay.turn_on()
        time.sleep(3)
        relay.turn_off()
