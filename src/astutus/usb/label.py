""" This module is used for most aspect of labeling device nodes.


At this time, it's not clear on whether formatting data should be part of the the LabelRules class,
or a separate class.

This implementation uses a Python dictionary representation of rules.  The dictionary is not
simple, so that may design may need to be revisited.
"""

import copy
import json
import logging
import os
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.util

logger = logging.getLogger(__name__)

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
        # Return a copy, so that the content can only be changed
        # by using the class interface.  This is needed for persistance.
        return copy.deepcopy(self.rules)

    def get_rule(self, idx: int) -> Dict:
        for rule in self.rules:
            if rule['id'] == idx:
                return rule
        return None

    def update(self, rule_with_updated_value: Dict):
        idx = rule_with_updated_value['id']
        found = False
        for item_idx, rule in enumerate(self.rules):
            if rule['id'] == idx:
                self.rules[item_idx] = rule_with_updated_value
                found = True
                break
        if not found:
            logger.debug(f'self.rules: {self.rules}')
        assert found, rule_with_updated_value
        self.write()
        return None

    def sort(self, ids: List) -> str:
        """ Sort the label rules in the order given by the ids.

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

    def new_rule(self, device_data=None) -> Dict:
        """ Create a new rule, which has been added at the top of the rules list.

        The rule will have a unique id.  It will have reasonable defaults based
        on the data available.
         """
        max_id = None
        for rule in self.rules:
            if max_id is None:
                max_id = rule['id']
            elif rule['id'] > max_id:
                max_id = rule['id']
        if max_id is None:
            max_id = 0
        idx = max_id + 1
        if device_data is None:
            ilk = 'usb'
            node_check = None
        else:
            ilk = device_data.get('ilk')
            node_check = {'field': 'node_id', 'operator': 'equals', 'value': device_data.get('node_id')}
        checks_list = [{'field': 'ilk', 'operator': 'equals', 'value': ilk}]
        if node_check is not None:
            checks_list.append(node_check)
        rule = {
            'name': f'-- name rule {idx} --',
            'id': idx,
            'checks': checks_list,
            'template': '{color_for_' + ilk + '} {vendor} {product_text} {end_color}'
        }
        self.rules.insert(0, rule)
        self.write()
        return rule

    def delete_rule_by_id(self, idx: int):
        rule = self.get_rule(idx)
        self.rules.remove(rule)
        self.write()

    def check_field_set(self) -> List[str]:
        """ Returns a list of unique fields used in the checks for all rules."""
        field_set = set()
        for rule in self.rules:
            logger.debug(f'rule: {rule}')
            checks = rule.get('checks')
            if checks is None:
                continue
            for check in checks:
                field = check.get('field')
                if field is None:
                    continue
                field_set.add(field)
        return list(field_set)

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
                if data_value is None:
                    return False
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

ansi = astutus.util.AnsiSequenceStack()

ansi_terminal_formatting_data = {
    'color_for_usb': ansi.push('ForestGreen'),
    'color_for_pci': ansi.push('DarkOrange'),
    'color_for_other': ansi.push('DarkOrange'),
    'color_purple': ansi.push('Purple'),
    'end_color': ansi.pop()
}


def get_formatting_data(kind: str) -> Dict[str, str]:
    if kind == 'html':
        return html_formatting_data
    elif kind == 'ansi_terminal':
        return ansi_terminal_formatting_data
    else:
        raise NotImplementedError(f'Formating data for kind "{kind}" not defined.')
