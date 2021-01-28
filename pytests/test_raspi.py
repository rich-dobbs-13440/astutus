import logging

import astutus.raspi
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.skip(reason="requires a RaspberryPi")
def test_publish_wheels():
    raspi = astutus.raspi.RaspberryPi(ipv4='192.168.0.65')
    raspi.publish_wheels()
