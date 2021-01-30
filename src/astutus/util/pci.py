import astutus.util.util_impl


def get_device_info_from_dirname(device_info_map, dirname):
    slot = dirname[5:]
    return device_info_map.get(slot)


def get_slot_to_device_info_map_from_lspci(*, command_runner=None) -> dict:
    """ Find PCI information by running the lspci command and parsing the output.

    Produces a dictionary keyed by slot, with the value being a
    dictionary of attributes.
    """
    if command_runner is None:
        command_runner = astutus.util.util_impl.run_cmd
    # For lspci
    # -mm             Produce machine-readable output
    return_code, stdout, stderr = command_runner('lspci -mm -v')
    # Sample Output with blank lines between devices:
    #
    # Slot:   04:00.0
    # Class:  SATA controller
    # Vendor: ASMedia Technology Inc.
    # Device: ASM1062 Serial ATA Controller
    # SVendor:        ASUSTeK Computer Inc.
    # SDevice:        ASM1062 Serial ATA Controller
    # Rev:    01
    # ProgIf: 01
    # NUMANode:
    assert return_code == 0
    assert len(stderr) == 0, stderr
    slot_to_device_info_map = {}
    device_info = {}
    for line in stdout.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            value = value.strip()
            device_info[key] = value
        else:
            slot_to_device_info_map[device_info['Slot']] = device_info
            device_info = {}
    if device_info.get('Slot') is not None:
        # Add the last item to the map
        slot_to_device_info_map[device_info['Slot']] = device_info
        device_info = {}
    return slot_to_device_info_map
