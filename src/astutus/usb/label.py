import copy
from typing import Dict, List, Optional, Set, Tuple  # noqa


original_rules = [
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

rules = copy.deepcopy(original_rules)


def get_rules() -> List[Dict]:
    return rules


def get_rule(idx: int) -> Dict:
    for rule in rules:
        if rule['id'] == idx:
            return rule
    return None


def update(rule_with_updated_value: Dict):
    idx = rule_with_updated_value['id']
    for item_idx, rule in enumerate(rules):
        if rule['id'] == idx:
            rules[item_idx] = rule_with_updated_value
            break
    return None


def sort(ids: List) -> str:
    """ sort the label rules in the order given by the ids.

    Returns error message or None
    """
    global rules
    if len(ids) != len(rules):
        return f"Wrong number of ids.  Expected {len(rules)}, got {len(ids)}"
    ids_as_ints = [int(idx) for idx in ids]
    rules_as_dict = {rule['id']: rule for rule in rules}
    new_rules = [rules_as_dict[idx] for idx in ids_as_ints]
    if len(new_rules) != len(rules):
        return f"Incorrect or repeated ids: {ids}"
    rules = new_rules
    return None


def new_rule() -> Dict:
    max_id = None
    for rule in rules:
        if max_id is None:
            max_id = rule['id']
        elif rule['id'] > max_id:
            max_id = rule['id']
    if max_id is None:
        max_id = 0
    idx = max_id + 1
    rule = {
        'name': f'-- name rule {idx} --',
        'id': idx,
        'checks': [{'field': 'ilk', 'operator': 'equals', 'value': 'usb'}],
        'template': '{color_for_usb} {vendor} {product_text} {end_color}'
    }
    rules.insert(0, rule)
    return rule


def rule_applies(rule, device_data: Dict[str, str]) -> bool:
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
