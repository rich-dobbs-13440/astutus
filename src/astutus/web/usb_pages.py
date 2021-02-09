import logging
from datetime import datetime
from http import HTTPStatus

import astutus.usb
import astutus.usb.label
import flask
import flask.logging

logger = logging.getLogger(__name__)

usb_page = flask.Blueprint('usb', __name__, template_folder='templates')


def get_labelrules_items_list():
    label_rules = astutus.usb.LabelRules().get_rules()
    items_list = []
    for rule in label_rules:
        logger.debug(f'rule: {rule}')
        items_list.append({'value': rule.id, 'link_text': rule.name})
    return items_list


@usb_page.route('/astutus/app/usb/index.html', methods=['GET'])
def handle_usb():
    if flask.request.method == 'GET':
        return flask.render_template(
            'app/usb/styled_index.html')


def item_to_html(item):
    if isinstance(item, str):
        return [item]
    elif isinstance(item, dict):
        lines = []
        for key, value in item.items():
            if key == 'children':
                lines.append('<ul>')
                for child in item['children']:
                    lines.append('<li>')
                    lines.extend(item_to_html(child))
                    lines.append('</li>')
                lines.append('</ul>')
            elif key == 'data':
                pass
            else:
                dirpath = value['data']['dirpath']
                dirname = value['data']['dirname']
                button_class = 'class="astutus-tree-item-button"'
                lines.append(f'<button data-dirpath="{dirpath}" {button_class}>{dirname}</button>')
                lines.append('<span></span>')
                lines.extend(item_to_html(value))
        return lines
    elif isinstance(item, list):
        assert False, item
    assert False, type(item)


def tree_to_html(tree_dict):
    lines = []
    lines.append('<ul class="ast"><li>')
    lines.extend(item_to_html(tree_dict))
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
        logger.debug(f"node_data: {device_data}")
        label_rules = astutus.usb.LabelRules()
        label = label_rules.get_label(
            sys_devices_path, device_classifier, astutus.usb.label.get_formatting_data('html'))
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
    # if path == 'devices/pci0000:00':
    #     pci_device_info = None
    #     ilk = "other"
    # elif pci_device_info_arg == "Nothing!":
    #     pci_device_info = None
    #     ilk = "usb"
    # else:
    #     pci_device_info = json.loads(pci_device_info_arg.replace("'", '"'))
    #     ilk = "pci"

    device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)
    device_data = device_classifier.get_device_data(sys_devices_path, ['nodepath'])
    # data = astutus.usb.tree.get_data_for_dirpath(ilk, sys_devices_path, pci_device_info)
    data_for_return = {
        # 'data_for_dir': data,
        'data_for_dir': device_data,
    }
    return data_for_return, HTTPStatus.OK


def process_update_label_rule(idx: int) -> None:
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


@usb_page.route('/astutus/app/usb/device_tree.html', methods=['GET', 'POST'])
def handle_usb_device_tree():
    if flask.request.method == 'GET':
        begin = datetime.now()
        logger.info("Start device tree data creation")
        device_tree = astutus.usb.UsbDeviceTree(basepath=None)
        bare_tree_dict = device_tree.execute_tree_cmd(to_bare_tree=True)
        bare_tree_html = tree_to_html(bare_tree_dict)
        background_color = astutus.util.get_setting('/astutus/app/usb/settings', 'background_color', "#fcfcfc")
        delta = datetime.now() - begin
        logger.info(f"Start rendering template for device tree.  Generation time: {delta.total_seconds()}")
        return flask.render_template(
            'app/usb/styled_device_tree.html',
            bare_tree=bare_tree_html,
            tree_html=None,
            tree_html_background_color=background_color)
    if flask.request.method == 'POST':
        idx = int(flask.request.form.get('idx'))
        process_update_label_rule(idx)
        return flask.redirect(flask.url_for('usb.handle_usb_device_tree'))


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
        createNewString = flask.request.args.get('createNew')
        if createNewString == 'false':
            createNew = False
        elif createNewString == 'true':
            createNew = True
        device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)
        label_rules = astutus.usb.LabelRules()
        check_fields = label_rules.check_field_set()
        device_data = device_classifier.get_device_data(dirpath, extra_fields=check_fields)
        device_data_for_rule = [device_data]
        rules = label_rules.get_rules()
        if createNew:
            rule = astutus.usb.LabelRules().new_rule(device_data)
        else:
            idx, rule = device_classifier.get_rule(dirpath, rules)
            logger.debug(f'rule: {rule}')

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
        device_tree = astutus.usb.UsbDeviceTree(basepath=None)
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
        process_update_label_rule(idx)
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


def get_html_labels_for_paths(device_paths):
    label_rules = astutus.usb.LabelRules()
    check_fields = label_rules.check_field_set()
    device_classifier = astutus.usb.DeviceClassifier(expire_seconds=20)
    labels = []
    for dirpath in device_paths:
        device_classifier.get_device_data(dirpath, extra_fields=check_fields)
        label = label_rules.get_label(dirpath, device_classifier, astutus.usb.label.get_formatting_data('html'))
        labels.append(label)
    return labels


def get_device_path_item_list():
    _, usb_device_dirpaths, _, _ = astutus.usb.usb_impl.walk_basepath_for_ilk()
    labels = get_html_labels_for_paths(usb_device_dirpaths)
    items_list = []
    for dirpath, label in zip(usb_device_dirpaths, labels):
        value = dirpath.replace(astutus.usb.usb_impl.DEFAULT_BASEPATH + '/', '')
        items_list.append({'value': value, 'link_text': label})
    return items_list


@usb_page.route('/astutus/app/usb/devices.html', methods=['GET'])
def handle_usb_devices():
    return flask.render_template(
        'app/usb/styled_devices.html',
        device_path_item_list=get_device_path_item_list(),
        )


@usb_page.route('/astutus/app/usb/device/<path:bare_device_path>/index.html', methods=['GET'])
def handle_usb_device_item(bare_device_path):
    if flask.request.method == 'GET':
        sys_devices_path = astutus.usb.usb_impl.DEFAULT_BASEPATH + '/' + bare_device_path + '/'
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
        label_rules = astutus.usb.LabelRules()
        labels = []
        for device_path in device_paths:
            device_data = device_classifier.get_device_data(device_path)
            label = label_rules.get_label(device_path, device_classifier, astutus.usb.label.get_formatting_data('html'))
            augumented_label = f"{device_data['dirname']} {label}"
            labels.append(augumented_label)

        return flask.render_template(
            'app/usb/device/styled_index.html',
            device_data_list=device_data_list,
            device_path_item_list=get_device_path_item_list(),  # Used for vertical menu
            labels=labels)
