import json
import logging
from http import HTTPStatus

import astutus.usb
import flask

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

static_base = "/static/_docs/_static"


@usb_page.route('/astutus/usb', methods=['GET'])
def handle_usb():
    if flask.request.method == 'GET':
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li>/usb</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        return flask.render_template(
            'usb/dyn_usb.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical)


@usb_page.route('/astutus/usb/device', methods=['GET', 'POST'])
def handle_usb_device():
    """ usb_page.route('/astutus/usb/device', methods=['GET', 'POST']) """
    if flask.request.method == 'GET':
        tree_dict = astutus.usb.execute_tree_cmd(
            basepath=None,
            device_aliases_filepath=None,
            to_dict=True)
        render_as_json = False
        if render_as_json:
            return tree_dict
        tree_html = astutus.usb.execute_tree_cmd(
            basepath=None,
            device_aliases_filepath=None,
            to_html=True)
        device_configurations = astutus.usb.DeviceConfigurations()
        # aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        # # Fix up aliases to be cleaner for Jinja2. (Then propagate back to class!)
        # for key, value in aliases.items():
        #     value[0]['match'] = key
        #     value[0]['name'] = value[0].get('name_of_config')
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/usb">/usb</a> &raquo;</li>',
            '<li>/device</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        background_color = astutus.util.get_setting('/astutus/usb/settings', 'background_color', "#fcfcfc")
        return flask.render_template(
            'usb/dyn_usb_device.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            tree=json.dumps(tree_dict),
            tree_html=tree_html,
            tree_html_background_color=background_color,
            device_configurations=device_configurations)
    if flask.request.method == 'POST':
        form = flask.request.form
        if form.get("action") == "add_or_update_alias":
            nodepath = form.get('nodepath')
            logger.debug(f"nodepath: {nodepath}")
            template = form.get('template')
            logger.debug(f"template: {template}")
            color = form.get('color_select')
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
        # Fix up aliases to be cleaner for Jinja2. (Then propagate back to class!)
        for key, value in aliases.items():
            value[0]['match'] = key
            value[0]['name'] = value[0].get('name_of_config')
        return flask.render_template(
            'usb/dyn_usb_alias.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            aliases=aliases)


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
