import copy
import json
import os
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.util

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


class LabelRules(object):

    def __init__(self, *, filepath=None):
        if filepath is None:
            filepath = os.path.join(astutus.util.get_user_data_path(), 'label_rules.json')
        self.filepath = filepath
        self.read()

    def read(self):
        if not os.path.isfile(self.filepath):
            # Just read it from default values
            self.rules = copy.deepcopy(original_rules)
        else:
            with open(self.filepath, 'r') as rules_file:
                content = json.load(rules_file)
            self.rules = content['rules']

    def write(self):
        # Wrap rules in a dictionary for flexibility
        content = {
            'rules': self.rules,
        }
        output_dir = os.path.dirname(self.filepath)
        os.makedirs(output_dir, exist_ok=True)
        with open(self.filepath, 'w') as rules_file:
            json.dump(content, rules_file, indent=4, sort_keys=True)

    def get_rules(self) -> List[Dict]:
        return self.rules

    def get_rule(self, idx: int) -> Dict:
        for rule in self.rules:
            if rule['id'] == idx:
                return rule
        return None

    def update(self, rule_with_updated_value: Dict):
        idx = rule_with_updated_value['id']
        for item_idx, rule in enumerate(self.rules):
            if rule['id'] == idx:
                self.rules[item_idx] = rule_with_updated_value
                break
        self.write()
        return None

    def sort(self, ids: List) -> str:
        """ sort the label rules in the order given by the ids.

        Returns error message or None
        """
        if len(ids) != len(self.rules):
            return f"Wrong number of ids.  Expected {len(self.rules)}, got {len(ids)}"
        ids_as_ints = [int(idx) for idx in ids]
        rules_as_dict = {rule['id']: rule for rule in self.rules}
        new_rules = [rules_as_dict[idx] for idx in ids_as_ints]
        if len(new_rules) != len(self.rules):
            return f"Incorrect or repeated ids: {ids}"
        self.rules = new_rules
        self.write()
        return None

    def new_rule(self) -> Dict:
        max_id = None
        for rule in self.rules:
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
        self.rules.insert(0, rule)
        self.write()
        return rule

    def delete_rule_by_id(self, idx: int):
        rule = self.get_rule(idx)
        self.rules.remove(rule)
        self.write()

    @staticmethod
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
