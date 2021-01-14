import json
import logging
from datetime import datetime
from http import HTTPStatus

import astutus.usb
import flask
import flask.logging

logger = logging.getLogger(__name__)
logger.addHandler(flask.logging.default_handler)

usb_page = flask.Blueprint('usb', __name__, template_folder='templates')

wy_menu_vertical_list = [
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc">Welcome</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus">Browser Astutus</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/usb">Browser USB Capabilities</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/usb/device">Browser USB Devices</a></li>',
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/usb/alias">Browser USB Device Aliases</a></li>',  # noqa
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc/command_line">Command Line Astutus</a></li>',  # noqa
]
wy_menu_vertical = "\n".join(wy_menu_vertical_list)

static_base = None  # Will be set when pages are registered.


@usb_page.route('/astutus/usb', methods=['GET'])
def handle_usb():
    if flask.request.method == 'GET':
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li>/usb</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        links_list = [
            '<li><p>See <a class="reference internal" href="/astutus/usb/device"><span class="doc">Devices</span></a></p></li>',  # noqa
            '<li><p>See <a class="reference internal" href="/astutus/usb/alias"><span class="doc">Device Aliases</span></a></p></li>',  # noqa
            '<li><p>See <a class="reference internal" href="/astutus/usb/configuration"><span class="doc">Device Configurations</span></a></p></li>',  # noqa
        ]
        links = "\n".join(links_list)
        return flask.render_template(
            'usb/dyn_usb.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            links=links)


def item_to_html(item, device_info_map):
    if isinstance(item, str):
        return [item]
    elif isinstance(item, dict):
        lines = []
        for key, value in item.items():
            if key == 'children':
                lines.append('<ul>')
                for child in item['children']:
                    lines.append('<li>')
                    lines.extend(item_to_html(child, device_info_map))
                    lines.append('</li>')
                lines.append('</ul>')
            elif key == 'data':
                pass
            else:
                dirpath = value['data']['dirpath']
                dirname = value['data']['dirname']
                maybe_slot = dirname[5:]
                device_info = device_info_map.get(maybe_slot)
                if device_info is not None:
                    data_info = f' data-info="{device_info}"'
                else:
                    data_info = ""
                button_class = 'class="astutus-tree-item-button"'
                lines.append(f'<button data-dirpath="{dirpath}" {button_class}{data_info}>{dirname}</button>')
                lines.append('<span></span>')
                lines.extend(item_to_html(value, device_info_map))
        return lines
    elif isinstance(item, list):
        assert False, item
    assert False, type(item)


def tree_to_html(tree_dict, device_info_map):
    lines = []
    lines.append('<ul class="ast"><li>')
    lines.extend(item_to_html(tree_dict, device_info_map))
    lines.append('</li></ul>')
    return '\n' + '\n'.join(lines)


@usb_page.route('/astutus/usb/label/sys/<path:path>', methods=['PUT'])
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
                device_config = astutus.usb.DeviceConfigurations.make_pci_configuration(data)
            elif data.get('ilk') == 'usb':
                device_config = astutus.usb.DeviceConfigurations.make_generic_usb_configuration(data)
            elif data.get('ilk') == 'other':
                device_config = astutus.usb.DeviceConfigurations.make_generic_other_configuration(data)
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


@usb_page.route('/astutus/usb/sys/<path:path>', methods=['GET', 'PATCH', 'PUT'])
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

    # form = flask.request.form
    device_info_arg = request_data.get('info')
    logger.debug(f'device_info_arg: {device_info_arg}')
    if path == 'devices/pci0000:00':
        device_info = None
        ilk = "other"
    elif device_info_arg == "Nothing!":
        device_info = None
        ilk = "usb"
    else:
        device_info = json.loads(device_info_arg.replace("'", '"'))
        ilk = "pci"
    data = astutus.usb.tree.get_data_for_dirpath(ilk, sys_devices_path, device_info)
    data_for_return = {
        'data_for_dir': data,
    }
    return data_for_return, HTTPStatus.OK


@usb_page.route('/astutus/usb/device_with_ajax', methods=['GET'])
def handle_usb_device_with_ajax():
    if flask.request.method == 'GET':
        begin = datetime.now()
        logger.info("Start device tree data creation")
        device_info_map = astutus.util.pci.get_slot_to_device_info_map_from_lspci()
        logger.debug(f"device_info_map: {device_info_map}")
        device_tree = astutus.usb.UsbDeviceTree(basepath=None, device_aliases_filepath=None)
        device_configurations = astutus.usb.DeviceConfigurations()
        bare_tree_dict = device_tree.execute_tree_cmd(to_bare_tree=True)
        bare_tree_html = tree_to_html(bare_tree_dict, device_info_map)
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/usb">/usb</a> &raquo;</li>',
            '<li>/device</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        background_color = astutus.util.get_setting('/astutus/usb/settings', 'background_color', "#fcfcfc")
        delta = datetime.now() - begin
        logger.info(f"Start rendering template for device tree.  Generation time: {delta.total_seconds()}")

        return flask.render_template(
            'usb/dyn_usb_device.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            bare_tree=bare_tree_html,
            aliases_javascript=aliases.to_javascript(),
            configurations_javascript=device_configurations.to_javascript(),
            tree_html=None,
            tree_html_background_color=background_color)


@usb_page.route('/astutus/usb/device', methods=['GET', 'POST'])
def handle_usb_device():
    """ usb_page.route('/astutus/usb/device', methods=['GET', 'POST']) """
    if flask.request.method == 'GET':
        begin = datetime.now()
        logger.info("Start device tree data creation")
        device_tree = astutus.usb.UsbDeviceTree(basepath=None, device_aliases_filepath=None)
        logger.info("Obtained tree_dict")
        tree_html = device_tree.execute_tree_cmd(to_html=True)
        logger.info("Obtained tree_html")
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/usb">/usb</a> &raquo;</li>',
            '<li>/device</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        background_color = astutus.util.get_setting('/astutus/usb/settings', 'background_color', "#fcfcfc")
        delta = datetime.now() - begin
        logger.info(f"Start rendering template for device tree.  Generation time: {delta.total_seconds()}")

        return flask.render_template(
            'usb/dyn_usb_device.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            tree_html=tree_html,
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
            aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
            aliases[nodepath] = [{
                "color": f"{color}",
                "description_template": f"{template}",
                "order": "00",
                "priority": 50
            }]
            astutus.usb.device_aliases.DeviceAliases.write_raw_as_json(filepath=None, raw_aliases=aliases)
            return flask.redirect(flask.url_for('usb.handle_usb_device'))
        return "Unhandled post", HTTPStatus.NOT_IMPLEMENTED


@usb_page.route('/astutus/usb/alias', methods=['GET'])
def handle_usb_alias():
    if flask.request.method == 'GET':
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/usb">/usb</a> &raquo;</li>',
            '<li>/alias</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        return flask.render_template(
            'usb/dyn_usb_alias.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            aliases=aliases)


@usb_page.route('/astutus/usb/alias/<path:nodepath>', methods=['GET', "DELETE", "POST"])
def handle_usb_alias_item(nodepath):
    if flask.request.method == 'GET':
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/usb">/usb</a> &raquo;</li>',
            '<li><a href="/astutus/usb/alias">/alias</a> &raquo;</li>',
            f'<li>/{nodepath}</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        item = {
            'id': nodepath,
        }
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)

        alias = aliases.get(nodepath)
        if alias is not None:
            return flask.render_template(
                'usb/dyn_alias_item.html',
                static_base=static_base,
                breadcrumbs_list_items=breadcrumbs_list_items,
                wy_menu_vertical=wy_menu_vertical,
                item=item,
                alias=alias)
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
            "redirect_url": "/astutus/usb/alias"
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
        aliases[pattern] = [alias]
        aliases.write(filepath=None)
        return flask.redirect(flask.url_for('usb.handle_usb_alias'))


@usb_page.route('/astutus/usb/configuration', methods=['GET'])
def handle_usb_configuration():
    if flask.request.method == 'GET':
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/usb">/usb</a> &raquo;</li>',
            '<li>/configuration</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        device_configurations = astutus.usb.DeviceConfigurations()
        return flask.render_template(
            'usb/dyn_device_configurations.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            device_configurations=device_configurations)


@usb_page.route('/astutus/usb/configuration/<node_id>', methods=['GET', "DELETE"])
def handle_usb_configuration_item(node_id):
    if flask.request.method == 'GET':
        logger.debug(f"node_id: {node_id}")
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/usb">/usb</a> &raquo;</li>',
            '<li><a href="/astutus/usb/configuration">/configuration</a> &raquo;</li>',
            '<li>/configuration</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        device_configurations = astutus.usb.DeviceConfigurations()
        device_config = device_configurations.get_item(node_id)
        return flask.render_template(
            'usb/dyn_configuration_item.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            item=node_id,
            device_config=device_config)
    if flask.request.method == 'DELETE':
        logger.debug(f"Delete the item now: {node_id}")
        return "TODO", HTTPStatus.NOT_IMPLEMENTED


@usb_page.route('/astutus/usb/settings', methods=['GET', 'POST'])
def handle_usb_settings():
    """ usb_page.route('/astutus/usb/settings', methods=['GET', 'POST']) """
    if flask.request.method == 'GET':
        return "Should return settings here", HTTPStatus.NOT_IMPLEMENTED
    if flask.request.method == 'POST':
        background_color = flask.request.form.get('background-color')
        if background_color is not None:
            logger.info(f"background_color: {background_color}")
            astutus.util.persist_setting('/astutus/usb/settings', 'background_color', background_color)
            return "Setting persisted", HTTPStatus.OK
        return "Need to persist settings here", HTTPStatus.NOT_IMPLEMENTED
