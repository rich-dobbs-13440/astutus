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
from astutus.usb.device_classifier import DeviceClassifier, Rule, Check

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


class LabelRule(Rule):

    def __init__(self, data: Dict):
        self.template = data['template']
        logger.debug(f'self.template: {self.template}')
        self.id = data['id']
        self.name = data['name']
        self.extra_fields = data.get('extra_fields')
        self.checks = []
        checks = data.get('checks')
        if checks is not None:
            for raw_check in checks:
                check = Check(raw_check['field'], raw_check['operator'], raw_check['value'])
                self.checks.append(check)

    def as_dict(self) -> Dict:
        checks_list = []
        for check in self.checks:
            checks_list.append(check.as_dict())
        data = {
           'template': self.template,
           'id': self.id,
           'name': self.name,
           'extra_fields': self.extra_fields,
           'checks': checks_list,
        }
        return data

    def __repr__(self):
        # return f'LabelRule({dir(self)})'
        return f'LabelRule({self.as_dict()})'


class LabelRules(object):

    def __init__(self, *, filepath=None):
        if filepath is None:
            filepath = os.path.join(astutus.util.get_user_data_path(), 'label_rules.json')
        self.filepath = filepath
        self.rules = []
        self.read()
        self.parse_rules()

    def read(self) -> None:
        if not os.path.isfile(self.filepath):
            # Just read it from default values
            self.raw_rules = copy.deepcopy(original_rules)
        else:
            with open(self.filepath, 'r') as rules_file:
                content = json.load(rules_file)
            self.raw_rules = content['rules']

    def parse_rules(self) -> None:
        self.rules = []
        for rule_as_dict in self.raw_rules:
            rule = LabelRule(rule_as_dict)
            self.rules.append(rule)
            logger.debug(f'rule: {rule}')

    def write(self) -> None:
        # Wrap rules in a dictionary for flexibility
        rules_as_dict = []
        for rule in self.rules:
            rules_as_dict.append(rule.as_dict())
        content = {
            'rules': rules_as_dict,
        }
        output_dir = os.path.dirname(self.filepath)
        os.makedirs(output_dir, exist_ok=True)
        with open(self.filepath, 'w') as rules_file:
            json.dump(content, rules_file, indent=4, sort_keys=True)

    def get_rules(self) -> List[Dict]:
        # Return a copy, so that the content can only be changed
        # by using the class interface.  This is needed for persistance.
        return copy.deepcopy(self.rules)

    def get_rule(self, idx: int) -> LabelRule:
        for rule in self.rules:
            logger.debug(f'rule: {rule}')
            if rule.id == idx:
                return rule
        return None

    def update(self, rule_with_updated_value: LabelRule):
        idx = rule_with_updated_value.id
        found = False
        for item_idx, rule in enumerate(self.rules):
            if rule.id == idx:
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
        rules_as_dict = {rule.id: rule for rule in self.rules}
        new_rules = [rules_as_dict[idx] for idx in ids_as_ints]
        if len(new_rules) != len(self.rules):
            return f"Incorrect or repeated ids: {ids}"
        self.rules = new_rules
        self.write()
        return None

    def new_rule(self, device_data=None) -> LabelRule:
        """ Create a new rule, which has been added at the top of the rules list.

        The rule will have a unique id.  It will have reasonable defaults based
        on the data available.
         """
        max_id = None
        for rule in self.rules:
            if max_id is None:
                max_id = rule.id
            elif rule.id > max_id:
                max_id = rule.id
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
        data = {
            'name': f'-- name rule {idx} --',
            'id': idx,
            'checks': checks_list,
            'template': '{color_for_' + ilk + '} {vendor} {product_text} {end_color}'
        }
        rule = LabelRule(data)
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
            if rule.checks is None:
                continue
            for check in rule.checks:
                if check.field is None:
                    continue
                field_set.add(check.field)
        return list(field_set)

    def get_template(self, device_path: str, device_classifier: DeviceClassifier) -> str:
        rule = device_classifier.get_rule(device_path, self.rules)
        if rule is None:
            return '-- no rule_applies --'
        extra_fields = rule.extra_fields
        if extra_fields is not None:
            # Need to augment data before using the this template,
            # so do so now.
            device_classifier.get_device_data(device_path, extra_fields)
        return rule.template

    def get_label(
            self, device_path: str, device_classifier: DeviceClassifier, formatting_data: Dict[str, str] = []) -> str:
        template = self.get_template(device_path, device_classifier)
        device_data = device_classifier.get_device_data(device_path)
        label = self.robust_format_map(template, device_data, formatting_data)
        return label

    @staticmethod
    def robust_format_map(template: str, device_data: Dict[str, str], formatting_data: Dict[str, str]):
        data = copy.deepcopy(device_data)
        data.update(formatting_data)
        data
        max_count = template.count('{')
        count = 0
        while True:
            try:
                value = template.format_map(data)
                return value
            except KeyError as exception:
                logger.error(f'exception: {exception}')
                data[exception.args[0]] = f"--{exception.args[0]} missing--"
                count += 1
                if count > max_count:
                    # Just a double check to prevent infinite loop in case of coding error'
                    return f'robust_format_map error. template: {template} - data: {data}'


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
