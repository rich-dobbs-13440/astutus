import json
import logging
import pathlib

import astutus.usb
import astutus.usb.device_aliases
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.skip(reason="test data needs updating.")
def test_print_tree():
    device_aliases_filepath = pathlib.Path(__file__).resolve().parent / "test_data/device_aliases.json"

    usb_tree = astutus.usb.UsbDeviceTree(
        basepath=None,
        device_aliases_filepath=device_aliases_filepath,
        device_configurations_filepath=None)

    usb_tree.execute_tree_cmd(verbose=True)


@pytest.mark.skip(reason="Investigate")
def test_find_node_paths():
    node_paths = astutus.usb.device_aliases.find_node_paths('usb(1a86:7523)')
    logger.info(f"node_paths: {node_paths}")


def test_parse_args():
    raw_args = ['-a', 'Joe']
    args = astutus.usb.tree.parse_arguments(raw_args)
    assert args.device_aliases_filepath == "Joe"

    raw_args = ['--verbose']
    args = astutus.usb.tree.parse_arguments(raw_args)
    assert args.verbose is True


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
        device_aliases_filepath=None,
        device_configurations_filepath=None)

    tree_html = usb_tree.execute_tree_cmd(verbose=True, to_html=True)
    print("Start Tree")
    print(tree_html)
    print("End Tree")
