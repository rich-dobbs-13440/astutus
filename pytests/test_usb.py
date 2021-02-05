import json
import logging

import astutus.usb
import pytest

logger = logging.getLogger(__name__)


def test_parse_args():
    raw_args = ['--verbose']
    args = astutus.usb.tree.parse_arguments(raw_args)
    assert args.verbose is True


@pytest.mark.skip(reason="Need robust test strategy here.")
def test_usb_device_node_data_json_serializable():
    # TODO:  Come up with a non-fragile way to test this.
    node = astutus.usb.node.UsbDeviceNodeData(
        data={"idVendor": "Joe", "busnum": "04", "devnum": "02", "dirpath": "asfdfsda"},
        config=None,
        alias=None)
    json.dumps(node)
