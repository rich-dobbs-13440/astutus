import json
import logging

import astutus.usb
import astutus.usb.device_aliases
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


@pytest.mark.skip(reason="Obsolete Maybe?")
def test_execute_tree_cmd():
    usb_tree = astutus.usb.UsbDeviceTree(
        basepath=None,
        device_configurations_filepath=None)

    tree_html = usb_tree.execute_tree_cmd(verbose=True, to_html=True)
    print("Start Tree")
    print(tree_html)
    print("End Tree")
