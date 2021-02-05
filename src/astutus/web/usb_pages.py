import json
import logging
from datetime import datetime
from http import HTTPStatus

import astutus.usb
import astutus.usb.label
import flask
import flask.logging

logger = logging.getLogger(__name__)

usb_page = flask.Blueprint('usb', __name__, template_folder='templates')


extra_fields_for_ilk = {
    'usb': ['nodepath', 'vendor', 'product_text', 'device_class'],
    'pci': ['nodepath'],
}


def get_alias_path_item_list():
    aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
    alias_by_resolved_name = {}
    for key, alias in aliases.items():
        logger.debug(f"alias: {alias}")
        # Need to have a good name for display.  For now just use description template
        # if the name is not defined.  Long term, need to make sure name is defined
        # and unique.
        resolved_name = alias.get('name', alias['description_template'])
        while True:
            if resolved_name not in alias_by_resolved_name:
                alias_by_resolved_name[resolved_name] = {'value': alias['pattern'], 'link_text': resolved_name}
                break
            else:
                resolved_name += "+"
    # Sort before returning list.
    items_list = []
    sorted_keys = sorted([key for key in alias_by_resolved_name.keys()])
    for key in sorted_keys:
        items_list.append(alias_by_resolved_name[key])
    return items_list


def get_labelrules_items_list():
    label_rules = astutus.usb.LabelRules().get_rules()
    items_list = []
    for rule in label_rules:
        items_list.append({'value': rule['id'], 'link_text': rule['name']})
    return items_list


@usb_page.route('/astutus/app/usb/index.html', methods=['GET'])
def handle_usb():
    if flask.request.method == 'GET':
        return flask.render_template(
            'app/usb/styled_index.html')


def item_to_html(item, pci_device_info_map):
    if isinstance(item, str):
        return [item]
    elif isinstance(item, dict):
        lines = []
        for key, value in item.items():
            if key == 'children':
                lines.append('<ul>')
                for child in item['children']:
                    lines.append('<li>')
                    lines.extend(item_to_html(child, pci_device_info_map))
                    lines.append('</li>')
                lines.append('</ul>')
            elif key == 'data':
                pass
            else:
                dirpath = value['data']['dirpath']
                dirname = value['data']['dirname']
                maybe_slot = dirname[5:]
                pci_device_info = pci_device_info_map.get(maybe_slot)
                if pci_device_info is not None:
                    data_pci = f' data-pci="{pci_device_info}"'
                else:
                    data_pci = ""
                button_class = 'class="astutus-tree-item-button"'
                lines.append(f'<button data-dirpath="{dirpath}" {button_class}{data_pci}>{dirname}</button>')
                lines.append('<span></span>')
                lines.extend(item_to_html(value, pci_device_info_map))
        return lines
    elif isinstance(item, list):
        assert False, item
    assert False, type(item)


def tree_to_html(tree_dict, pci_device_info_map):
    lines = []
    lines.append('<ul class="ast"><li>')
    lines.extend(item_to_html(tree_dict, pci_device_info_map))
    lines.append('</li></ul>')
    return '\n' + '\n'.join(lines)


@usb_page.route('/astutus/app/usb/label/sys/<path:path>', methods=['PUT'])
def handle_label(path):
    # Intent is to get JSON here, rather than form data.
    if flask.request.is_json:
        request_data = flask.request.get_json(force=True)
        logger.debug(f"request_data: {request_data}")
        sys_devices_path = '/sys/' + path
        device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)
        device_data = device_classifier.get_device_data(sys_devices_path)
        extra_fields = extra_fields_for_ilk.get(device_data['ilk'])
        if extra_fields is not None:
            device_data = device_classifier.get_device_data(sys_devices_path, extra_fields)
        logger.debug(f"node_data: {device_data}")
        label = device_classifier.get_label(
            sys_devices_path, astutus.usb.LabelRules().get_rules(), astutus.usb.label.get_formatting_data('html'))
        device_data['html_label'] = f'<span class="node_id_class">{device_data["node_id"]}</span>{label}'
        result = {
            'html_label': device_data.get('html_label'),
            'sys_devices_path': sys_devices_path,
            'node_data': device_data,
        }
        return result, HTTPStatus.OK


@usb_page.route('/astutus/app/usb/sys/<path:path>', methods=['GET', 'PATCH', 'PUT'])
def handle_device_tree_item(path):
    logger.info('Start handle_device_tree_item')
    sys_devices_path = '/sys/' + path
    logger.debug(f'sys_devices_path: {sys_devices_path}')
    if sys_devices_path == '/sys/devices':
        data = {
            'data_for_dir': {
                'node_id': 'other(devices)',
                'top_of_tree': True,
                'dirpath': '/sys/devices',
                'dirname': 'devices',
                'ilk': 'other',
            },
        }
        return data, HTTPStatus.OK
    request_data = flask.request.get_json(force=True)
    pci_device_info_arg = request_data.get('pciDeviceInfo')
    logger.debug(f'pci_device_info_arg: {pci_device_info_arg}')
    if path == 'devices/pci0000:00':
        pci_device_info = None
        ilk = "other"
    elif pci_device_info_arg == "Nothing!":
        pci_device_info = None
        ilk = "usb"
    else:
        pci_device_info = json.loads(pci_device_info_arg.replace("'", '"'))
        ilk = "pci"
    data = astutus.usb.tree.get_data_for_dirpath(ilk, sys_devices_path, pci_device_info)
    data_for_return = {
        'data_for_dir': data,
    }
    return data_for_return, HTTPStatus.OK


@usb_page.route('/astutus/app/usb/device_tree.html', methods=['GET', 'POST'])
def handle_usb_device_tree():
    if flask.request.method == 'GET':
        begin = datetime.now()
        logger.info("Start device tree data creation")
        pci_device_info_map = astutus.util.pci.get_slot_to_device_info_map_from_lspci()
        logger.debug(f"pci_device_info_map: {pci_device_info_map}")
        device_tree = astutus.usb.UsbDeviceTree(basepath=None, device_aliases_filepath=None)
        bare_tree_dict = device_tree.execute_tree_cmd(to_bare_tree=True)
        bare_tree_html = tree_to_html(bare_tree_dict, pci_device_info_map)
        background_color = astutus.util.get_setting('/astutus/app/usb/settings', 'background_color', "#fcfcfc")
        delta = datetime.now() - begin
        logger.info(f"Start rendering template for device tree.  Generation time: {delta.total_seconds()}")
        return flask.render_template(
            'app/usb/styled_device_tree.html',
            bare_tree=bare_tree_html,
            tree_html=None,
            tree_html_background_color=background_color)
    if flask.request.method == 'POST':
        form = flask.request.form
        if form.get("action") == "add_or_update_alias":
            logger.info("Handle add_or_update_alias")
            nodepath = form.get('nodepath')
            logger.debug(f"nodepath: {nodepath}")
            template = form.get('template')
            logger.debug(f"template: {template}")
            color = form.get('color')
            logger.debug(f"color: {color}")
            name = form.get('name')
            if name is None:
                name = nodepath
            aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
            aliases[nodepath] = {
                "name": name,
                "color": f"{color}",
                "description_template": f"{template}",
                "order": "00",
                "priority": 50
            }
            astutus.usb.device_aliases.DeviceAliases.write_raw_as_json(filepath=None, raw_aliases=aliases)
            return flask.redirect(flask.url_for('usb.handle_usb_device_tree'))
        return "Unhandled post", HTTPStatus.NOT_IMPLEMENTED


@usb_page.route('/astutus/app/usb/labelrule/index.html', methods=['GET', 'PATCH', 'POST'])
def handle_usb_label_rule():
    if flask.request.method == 'GET':
        return flask.render_template(
            'app/usb/labelrule/styled_index.html',
            label_rules=astutus.usb.LabelRules().get_rules(),
            idx_item_list=get_labelrules_items_list())
    if flask.request.method == 'POST':
        rule = astutus.usb.LabelRules().new_rule()
        return flask.redirect(flask.url_for('usb.handle_usb_edit_label_rule', idx=rule['id']))
    if flask.request.method == 'PATCH':
        request_data = flask.request.get_json(force=True)
        ids = request_data.get('ids')
        logger.debug(f'ids: {ids}')
        err_msg = astutus.usb.LabelRules().sort(ids)
        if err_msg is not None:
            return err_msg, HTTPStatus.BAD_REQUEST
        return "Rules sorted", HTTPStatus.OK


@usb_page.route('/astutus/app/usb/labelrule/<int:idx>', methods=['DELETE'])
def handle_label_item(idx):
    if flask.request.method == 'DELETE':
        err_msg = astutus.usb.LabelRules().delete_rule_by_id(idx)
        if err_msg is not None:
            data = {
                "err_msg": "/astutus/app/usb/labelrule/index.html",
            }
            return data, HTTPStatus.BAD_REQUEST
        data = {
            "redirect_url": "/astutus/app/usb/labelrule/index.html"
        }
        return data, HTTPStatus.ACCEPTED


@usb_page.route('/astutus/app/usb/labelrule/*/editor.html', methods=['GET'])
def handle_usb_edit_label_rule_for_embbeded_content():
    """ This is used by the device tree to display a label rule editor for a particular device"""
    if flask.request.method == 'GET':
        dirpath = flask.request.args.get('forDevice')
        logger.debug(f'dirpath: {dirpath}')
        device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)
        label_rules = astutus.usb.LabelRules()
        check_fields = label_rules.check_field_set()
        device_classifier.get_device_data(dirpath, extra_fields=check_fields)
        rules = label_rules.get_rules()
        idx, rule = device_classifier.get_rule(dirpath, rules)
        logger.debug(f'rule: {rule}')
        device_data_for_rule = [device_classifier.get_device_data(dirpath)]
        cancel_onclick_action = "handleCancelLabelEditorPopup()"
        return flask.render_template(
            'app/usb/label_rule_editor.html',
            rule=rule,
            device_data_for_rule=device_data_for_rule,
            cancel_onclick_action=cancel_onclick_action
            )
        return "<div>Can you show this?</div>"


@usb_page.route('/astutus/app/usb/labelrule/<int:idx>/editor.html', methods=['GET', 'POST'])
def handle_usb_edit_label_rule(idx: int):
    if flask.request.method == 'GET':
        label_rules = astutus.usb.LabelRules()
        check_fields = label_rules.check_field_set()
        rule = label_rules.get_rule(idx)
        if rule is None:
            return f'No such label rule: {idx}', HTTPStatus.BAD_REQUEST
        device_tree = astutus.usb.UsbDeviceTree(basepath=None, device_aliases_filepath=None)
        tree_dirpaths = device_tree.get_tree_dirpaths()
        device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)
        for dirpath in tree_dirpaths:
            device_data = device_classifier.get_device_data(dirpath, extra_fields=check_fields)
            logger.debug(f'device_data: {device_data}')
        filtered_dirpaths = device_classifier.filter_device_paths_for_rule(rule, label_rules.get_rules(), tree_dirpaths)
        device_data_for_rule = []
        for dirpath in filtered_dirpaths:
            device_data_for_rule.append(device_classifier.get_device_data(dirpath))
        cancel_onclick_action = "window.location.href='/astutus/app/usb/labelrule/index.html';"
        return flask.render_template(
            'app/usb/styled_label_rule_editor.html',
            rule=rule,
            device_data_for_rule=device_data_for_rule,
            idx_item_list=get_labelrules_items_list(),
            cancel_onclick_action=cancel_onclick_action)
    if flask.request.method == 'POST':
        name = flask.request.form.get('label_rule_name')
        check_field_list = flask.request.form.getlist('check_field')
        check_operator_list = flask.request.form.getlist('check_operator')
        check_value_list = flask.request.form.getlist('check_value')
        checks = []
        for field, operator, value in zip(check_field_list, check_operator_list, check_value_list):
            check = {
                'field': field,
                'operator': operator,
                'value': value,
            }
            checks.append(check)
        template = flask.request.form.get('label_rule_template')
        # The extra fields are returned as a comma or space separated string.  They must be parsed to a list of strings
        raw_extra_fields = flask.request.form.get('label_rule_extra_fields')
        extra_fields = raw_extra_fields.replace(',', ' ').split()
        rule = {
            'name': name,
            'id': idx,
            'checks': checks,
            'template': template,
            'extra_fields': extra_fields,
        }
        astutus.usb.LabelRules().update(rule)
        logger.debug(f'rule: {rule}')
        return flask.redirect(flask.url_for('usb.handle_usb_label_rule'))


@usb_page.route('/astutus/app/usb/settings', methods=['GET', 'PATCH'])
def handle_usb_settings():
    if flask.request.method == 'GET':
        return "Should return settings here", HTTPStatus.NOT_IMPLEMENTED
    if flask.request.method == 'PATCH':
        request_data = flask.request.get_json(force=True)
        background_color = request_data.get('background-color')
        if background_color is not None:
            logger.info(f"background_color: {background_color}")
            astutus.util.persist_setting('/astutus/app/usb/settings', 'background_color', background_color)
            return "Setting persisted", HTTPStatus.OK
        return "Need to persist settings here", HTTPStatus.NOT_IMPLEMENTED


@usb_page.route('/astutus/app/usb/device/<path:nodepath>/index.html', methods=['GET'])
def handle_usb_device_item(nodepath):
    if flask.request.method == 'GET':
        sys_devices_path = flask.request.args.get('sys_device_path')
        sys_devices_path += '/'  # to pick up last element
        device_paths = []
        idx = 5
        while idx > 0:
            idx = sys_devices_path.find('/', idx + 1)
            if idx > 0:
                device_paths.append(sys_devices_path[:idx])
        logger.debug(f"device_paths: {device_paths}")

        extra_fields_for_ilk = {
            'usb': ['nodepath', 'vendor', 'product_text', 'device_class'],
            'pci': ['nodepath'],
        }
        device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)
        device_data_list = []
        for device_path in device_paths:
            device_data = device_classifier.get_device_data(device_path)
            extra_fields = extra_fields_for_ilk.get(device_data['ilk'])
            if extra_fields is not None:
                device_data = device_classifier.get_device_data(device_path, extra_fields)
            device_data_list.append(device_data)

        extra_fields_for_node_id = {
            'usb(046d:c52b)': ['logitech_unifying_receiver_input_type'],
        }
        for device_path in device_paths:
            device_data = device_classifier.get_device_data(device_path)
            extra_fields = extra_fields_for_node_id.get(device_data['node_id'])
            if extra_fields is not None:
                device_classifier.get_device_data(device_path, extra_fields)

        labels = []
        for device_path in device_paths:
            device_data = device_classifier.get_device_data(device_path)
            label = device_classifier.get_label(
                device_path, astutus.usb.LabelRules().get_rules(), astutus.usb.label.get_formatting_data('html'))
            augumented_label = f"{device_data['dirname']} {label}"
            labels.append(augumented_label)

        return flask.render_template(
            'app/usb/device/nodepath/styled_index.html',
            device_data_list=device_data_list,
            labels=labels)
