import logging

import astutus.raspi

logger = logging.getLogger(__name__)


def test_publish_wheels():
    logger.error("Just say something")
    raspi = astutus.raspi.RaspberryPi(ipv4='192.168.0.65')
    raspi.publish_wheels()
