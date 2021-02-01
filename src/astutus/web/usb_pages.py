import json
import logging
from datetime import datetime
from http import HTTPStatus

import astutus.usb
import flask
import flask.logging

logger = logging.getLogger(__name__)

usb_page = flask.Blueprint('usb', __name__, template_folder='templates')


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


@usb_page.route('/astutus/app/usb/index.html', methods=['GET'])
def handle_usb():
    if flask.request.method == 'GET':
        # links_list = [
        #     '<li><p>See <a class="reference internal" href="/astutus/app/usb/device.html"><span class="doc">Devices</span></a></p></li>',  # noqa
        #     '<li><p>See <a class="reference internal" href="/astutus/app/usb/alias.html"><span class="doc">Device Aliases</span></a></p></li>',  # noqa
        #     '<li><p>See <a class="reference internal" href="/astutus/app/usb/configuration.html"><span class="doc">Device Configurations</span></a></p></li>',  # noqa
        # ]
        # links = "\n".join(links_list)
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
    # logger.info(f"flask.request.data: {flask.request.data}")
    # logger.info(f"flask.request.headers: {flask.request.headers}")
    # logger.info(f"flask.request.is_json: {flask.request.is_json}")
    if flask.request.is_json:
        request_data = flask.request.get_json(force=True)
        logger.debug(f"request_data: {request_data}")
        # logger.info(f"request_data.get('alias'): {request_data.get('alias')}")
        alias = request_data.get('alias')
        sys_devices_path = '/sys/' + path
        data = request_data.get('data')
        # TODO: Pass configuration from web page.  Maybe security risk.  Need to consider protection from
        #       running arbitrary code.
        config_data = request_data.get('device_config')
        if config_data is not None:
            device_config = astutus.usb.DeviceConfiguration(config_data)
        else:
            if data.get('ilk') == 'pci':
                device_config = astutus.usb.DeviceConfiguration.make_pci_configuration(data)
            elif data.get('ilk') == 'usb':
                device_config = astutus.usb.DeviceConfiguration.make_generic_usb_configuration(data)
            elif data.get('ilk') == 'other':
                device_config = astutus.usb.DeviceConfiguration.make_generic_other_configuration(data)
            else:
                raise NotImplementedError(f"Unhandled ilk: {data.get('ilk')}")
        logger.debug(f"device_config: {device_config}")
        node_data = astutus.usb.tree.get_node_data(data, device_config, alias)
        logger.debug(f"node_data: {node_data}")
        result = {
            'html_label': node_data.get('html_label'),
            'sys_devices_path': sys_devices_path,
            'node_data': node_data,
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
def handle_usb_device():
    if flask.request.method == 'GET':
        begin = datetime.now()
        logger.info("Start device tree data creation")
        pci_device_info_map = astutus.util.pci.get_slot_to_device_info_map_from_lspci()
        logger.debug(f"pci_device_info_map: {pci_device_info_map}")
        device_tree = astutus.usb.UsbDeviceTree(basepath=None, device_aliases_filepath=None)
        bare_tree_dict = device_tree.execute_tree_cmd(to_bare_tree=True)
        bare_tree_html = tree_to_html(bare_tree_dict, pci_device_info_map)
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        background_color = astutus.util.get_setting('/astutus/app/usb/settings', 'background_color', "#fcfcfc")
        delta = datetime.now() - begin
        logger.info(f"Start rendering template for device tree.  Generation time: {delta.total_seconds()}")

        return flask.render_template(
            'app/usb/styled_device_tree.html',
            bare_tree=bare_tree_html,
            aliases_javascript=aliases.to_javascript(),
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
            return flask.redirect(flask.url_for('usb.handle_usb_device'))
        return "Unhandled post", HTTPStatus.NOT_IMPLEMENTED


@usb_page.route('/astutus/app/usb/alias.html', methods=['GET'])
def handle_usb_alias():
    if flask.request.method == 'GET':
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        return flask.render_template(
            'app/usb/styled_alias.html',
            aliases=aliases,
            nodepath_item_list=get_alias_path_item_list())


@usb_page.route('/astutus/app/usb/alias/<path:nodepath>/index.html', methods=['GET', "DELETE", "POST"])
def handle_usb_alias_item(nodepath):
    if flask.request.method == 'GET':
        item = {
            'id': nodepath,
        }
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        alias = aliases.get(nodepath)
        if alias is not None:
            return flask.render_template(
                'app/usb/alias/nodepath/styled_index.html',
                item=item,
                nodepath=nodepath,
                alias=alias,
                nodepath_item_list=get_alias_path_item_list())
        return f"No alias for {nodepath} found.", HTTPStatus.BAD_REQUEST
    if flask.request.method == 'DELETE':
        logger.debug(f"Delete the item now: {nodepath}")
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        logger.debug(f"aliases: {aliases}")
        del aliases[nodepath]
        logger.debug(f"After deletion: aliases: {aliases}")
        aliases.write(filepath=None)
        logger.debug(f"After write: aliases: {aliases}")
        data = {
            "redirect_url": "/astutus/app/usb/alias.html"
        }
        return data, HTTPStatus.ACCEPTED
    if flask.request.method == 'POST':
        form = flask.request.form
        name = form.get('name')
        pattern = form.get('pattern')
        template = form.get('template')
        color = form.get('color')
        order = form.get('order')
        priority = form.get('priority')
        alias = {
            'name': name,
            'pattern': pattern,
            'description_template': template,
            'color': color,
            'order': order,
            'priority': priority
        }
        logger.info(f"alias: {alias}")
        original_pattern = form.get('original_pattern')
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        del aliases[original_pattern]
        aliases[pattern] = alias
        aliases.write(filepath=None)
        return flask.redirect(flask.url_for('usb.handle_usb_alias'))


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
        device_classifier = astutus.usb.DeviceClassifier(expire_seconds=10)
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
        rules = [
            {
                'checks': [
                    {'field': 'ilk', 'equals': 'usb'},
                    {'field': 'node_id', 'equals': 'usb(1a86:7523)'},
                    {'field': 'nodepath', 'contains': 'usb(05e3:0610)'},
                ],
                'extra_fields': ['tty'],
                'template': '{color_purple} {vendor} {product_text} {tty} {end_color}'
            },
            {
                'checks': [
                    {'field': 'ilk', 'equals': 'usb'},
                    {'field': 'node_id', 'equals': 'usb(1a86:7523)'},
                ],
                'extra_fields': ['tty'],
                'template': '{color_for_usb} {vendor} {product_text} {tty} {end_color}'
            },
            {
                'checks': [{'field': 'ilk', 'equals': 'pci'}],
                'template': '{color_for_pci} {vendor} {product_text} {end_color}'
            },
            {
                'checks': [{'field': 'ilk', 'equals': 'usb'}],
                'template': '{color_for_usb} {vendor} {product_text} {end_color}'
            },
            {
                'checks': [{'field': 'ilk', 'equals': 'other'}],
                'template': '{color_for_other} {node_id} {end_color}'
            },
            {
                'template': '{node_id}'
            }
        ]
        html_formatting_data = {
            'color_for_usb': '<span style="color:ForestGreen">',
            'color_for_pci': '<span style="color:DarkOrange">',
            'color_for_other': '<span style="color:DarkOrange">',
            'color_purple': '<span style="color:Purple">',
            'end_color': '</span>'
        }

        labels = []
        for device_path in device_paths:
            device_data = device_classifier.get_device_data(device_path)
            template = device_classifier.get_template(device_path, rules)
            label = device_classifier.get_label(device_path, rules, html_formatting_data)
            augumented_label = f"{device_data['dirname']} {label}  - template: {template}"
            labels.append(augumented_label)

        return flask.render_template(
            'app/usb/device/nodepath/styled_index.html',
            device_data_list=device_data_list,
            labels=labels)
