from typing import Dict, List, Optional, Set, Tuple  # noqa


rules = [
    {
        'name': 'Purple SMAKN Relay',
        'id': 6,
        'checks': [
            {'field': 'ilk', 'operator': 'equals', 'value': 'usb'},
            {'field': 'node_id', 'operator': 'equals', 'value': 'usb(1a86:7523)'},
            {'field': 'nodepath', 'operator': 'contains', 'value': 'usb(05e3:0610)'},
        ],
        'extra_fields': ['tty'],
        'template': '{color_purple} Purple SMAKN Relay {tty} {end_color}'
    },
    {
        'name': 'SMAKN Relay',
        'id': 5,
        'checks': [
            {'field': 'ilk', 'operator': 'equals', 'value': 'usb'},
            {'field': 'node_id', 'operator': 'equals', 'value': 'usb(1a86:7523)'},
        ],
        'extra_fields': ['tty'],
        'template': '{color_for_usb} SMAKN Relay {tty} {end_color}'
    },
    {
        'name': 'PCI Nodes',
        'id': 4,
        'checks': [{'field': 'ilk', 'operator': 'equals', 'value': 'pci'}],
        'template': '{color_for_pci} {vendor} {product_text} {end_color}'
    },
    {
        'name': 'USB Nodes',
        'id': 3,
        'checks': [{'field': 'ilk', 'operator': 'equals', 'value': 'usb'}],
        'template': '{color_for_usb} {vendor} {product_text} {end_color}'
    },
    {
        'name': 'Other Nodes',
        'id': 2,
        'checks': [{'field': 'ilk', 'operator': 'equals', 'value': 'other'}],
        'template': '{color_for_other} {node_id} {end_color}'
    },
    {
        'name': 'Default',
        'id': 1,
        'template': '{node_id}'
    }
]


def get_rules():
    return rules


def get_rule(idx: int):
    for rule in rules:
        if rule['id'] == idx:
            return rule
    return None


def rule_applies(rule, device_data) -> bool:
    checks = rule.get('checks')
    if checks is None:
        return True
    for check in checks:
        field = check.get('field')
        data_value = device_data.get(field)
        operator = check.get('operator')
        if operator == 'equals':
            if check.get('value') != data_value:
                return False
        elif operator == 'contains':
            if check.get('value') not in data_value:
                return False
        else:
            raise NotImplementedError(f'operator: {operator}')
    return True


html_formatting_data = {
    'color_for_usb': '<span style="color:ForestGreen">',
    'color_for_pci': '<span style="color:DarkOrange">',
    'color_for_other': '<span style="color:DarkOrange">',
    'color_purple': '<span style="color:Purple">',
    'end_color': '</span>'
}


def get_formatting_data(kind: str) -> Dict[str, str]:
    assert kind == 'html'
    return html_formatting_data
