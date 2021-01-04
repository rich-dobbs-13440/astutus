#!/usr/bin/env python3
"""

This module implements the Flask web application for the package.

The web application provides:

    * A server for the Sphinx generated documentation.
    * An HTML interface for interacting with the system.
    * A REST API for interacting with the system remotely
    * or locally for automation.

The handle routines are all Flask endpoints.

Maintainence note:

    Include the app.route decorator in the docstrings
    for the handle routines.

"""
import json
import logging
import os
from http import HTTPStatus

import astutus.raspi
import astutus.web.flask_app
import astutus.db
import astutus.log
import astutus.usb
import flask
import flask.logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_app_and_db():

    app = flask.Flask('astutus.web.flask_app', template_folder='templates')
    app.config["SQLALCHEMY_DATABASE_URI"] = astutus.db.get_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = astutus.db.get_instance()
    db.init_app(app)
    with app.app_context():
        astutus.db.initialize_db_if_needed()
    return app, db


app, db = create_app_and_db()


flask.logging.default_handler.setFormatter(astutus.log.standard_formatter)
astutus.raspi.find.logger.addHandler(flask.logging.default_handler)
astutus.raspi.raspi_impl.logger.addHandler(flask.logging.default_handler)
logger.addHandler(flask.logging.default_handler)

wy_menu_vertical_list = [
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc">Welcome</a></li>'
    '<li class="toctree-l1"><a class="reference internal" href="/astutus">Browser Astutus</a></li>'
    '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc/command_line">Command Line Astutus</a></li>'  # noqa
]
wy_menu_vertical = "\n".join(wy_menu_vertical_list)

static_base = "/static/_docs/_static"


@app.template_filter('tojson_pretty')
def tojson_pretty_jinja2_template_file(json_text):
    parsed_json = json.loads(json_text)
    return json.dumps(parsed_json, indent=4, sort_keys=True)


@app.route('/')
def handle_top():
    """ app.route('/') """
    return "TODO: redirect to /astutus"


@app.route('/astutus')
def handle_astutus():

    """ app.route('/astutus') """
    breadcrumbs_list = [
        '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
        '<li>/astutus</li>',
    ]
    breadcrumbs_list_items = "\n".join(breadcrumbs_list)
    links_list = [
        '<li><p>See <a class="reference internal" href="/astutus/raspi"><span class="doc">Raspberry Pi</span></a></p></li>',  # noqa
        '<li><p>See <a class="reference internal" href="/astutus/usb"><span class="doc">USB</span></a></p></li>',  # noqa
    ]
    links = "\n".join(links_list)
    return flask.render_template(
        'transformed_dyn_astutus.html',
        static_base=static_base,
        breadcrumbs_list_items=breadcrumbs_list_items,
        wy_menu_vertical=wy_menu_vertical,
        links=links)


@app.route('/astutus/usb', methods=['GET', 'POST'])
def handle_usb():
    """ app.route('/astutus/usb', methods=['GET']) """
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
        aliases = astutus.usb.device_aliases.DeviceAliases(filepath=None)
        # Fix up aliases to be cleaner for Jinja2. (Then propagate back to class!)
        for key, value in aliases.items():
            value[0]['match'] = key
            value[0]['name'] = value[0].get('name_of_config')
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li>/usb</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        return flask.render_template(
            'transformed_dyn_usb.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            tree=json.dumps(tree_dict),
            tree_html=tree_html,
            device_configurations=device_configurations,
            aliases=aliases)
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
            return flask.redirect(flask.url_for('handle_usb'))
        return "Unhandled post", HTTPStatus.NOT_IMPLEMENTED


def process_raspi_search_using_nmap(args):
    ipv4 = args.get("ipv4")
    logger.debug(f"ipv4: {ipv4}")
    mask = args.get("mask")
    logger.debug(f"mask: {mask}")
    filter = args.getlist("filter")
    logger.debug(f"filter: {filter}")
    search_result = astutus.raspi.search_using_nmap(ipv4, mask, filter)
    return display_raspi_find(search_result=search_result, filter=filter)


def display_raspi_find(*, search_result, filter):
    breadcrumbs_list = [
        '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
        '<li><a href="/astutus">/astutus</a> &raquo;</li>',
        '<li><a href="/astutus/raspi">/raspi</a> &raquo;</li>',
        '<li>find=nmap</li>',
    ]
    breadcrumbs_list_items = "\n".join(breadcrumbs_list)
    return flask.render_template(
        'transformed_dyn_raspi_find.html',
        static_base=static_base,
        breadcrumbs_list_items=breadcrumbs_list_items,
        wy_menu_vertical=wy_menu_vertical,
        search_result=search_result,
        filter=filter)


@app.route('/astutus/raspi', methods=['POST', 'GET'])
def handle_raspi():
    """ app.route('/astutus/raspi', methods=['POST', 'GET']) """
    if flask.request.method == 'GET':
        if flask.request.args.get("action") == "seach_using_nmap":
            logger.debug("Go to process_raspi_find_form")
            return process_raspi_search_using_nmap(flask.request.args)
        if flask.request.args.get('find') is not None:
            logger.debug("Go to display_raspi_find")
            return display_raspi_find(search_result=None, filter=["Raspberry"])
        logger.error("Just display base form")
        items = astutus.db.RaspberryPi.query.all()
        links_list = []
        for item in items:
            link = f'<li><p>See <a class="reference internal" href="/astutus/raspi/{item.id}"><span class="doc">{item.id}</span></a></p></li>'  # noqa
            links_list.append(link)
        links = "\n".join(links_list)
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li>/raspi</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        return flask.render_template(
            'transformed_dyn_raspi.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            links=links,
            filter=["Raspberry"])

    if flask.request.method == 'POST':
        form = flask.request.form
        if form.get("action") == "create":
            raspi_ipv4 = form.get("raspi_ipv4")
            raspi_mac_addr = form.get("raspi_mac_addr")
            rpi = astutus.db.RaspberryPi(ipv4=raspi_ipv4, mac_addr=raspi_mac_addr)
            db.session.add(rpi)
            db.session.commit()
            logger.debug(f"rpi: {rpi}")
            return flask.redirect(flask.url_for('handle_raspi_item', idx=rpi.id))
        return "Case not handled", HTTPStatus.NOT_IMPLEMENTED


@app.route('/astutus/raspi/<int:idx>', methods=['POST', 'GET', 'DELETE'])
def handle_raspi_item(idx):
    """ app.route('/astutus/raspi/<int:idx>', methods=['POST', 'GET', 'DELETE']) """
    if flask.request.method == 'POST':
        return "Got here"
    if flask.request.method == 'DELETE':
        item = astutus.db.RaspberryPi.query.get(idx)
        db.session.delete(item)
        db.session.commit()
        data = {
            "redirect_url": "/astutus/raspi"
        }
        return data, HTTPStatus.ACCEPTED
    if flask.request.method == 'GET':
        item = astutus.db.RaspberryPi.query.get(idx)
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/raspi">/raspi</a> &raquo;</li>',
            f'<li>/{item.id}</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        return flask.render_template(
            'transformed_dyn_raspi_item.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            wy_menu_vertical=wy_menu_vertical,
            # item=item.as_json()
            item=item
            )


@app.route('/astutus/raspi/<int:idx>/ifconfig', methods=['GET'])
def handle_raspi_item_ifconfig(idx):
    """" app.route('/astutus/raspi/<int:idx>/ifconfig', methods=['GET']) """
    item = astutus.db.RaspberryPi.query.get(idx)
    raspi = astutus.raspi.RaspberryPi(item)
    ifconfig = raspi.get_ifconfig()
    page_data = {
        'title': "Raspberry Pi - ifconfig",
        'show_links_section': False,
        "show_post_section": False,
        "show_delete_section": False,
        "show_raw_json_section": True,
    }
    return flask.render_template(
        'generic_rest_page.html',
        page_data=page_data,
        data=ifconfig,
        links=None)


@app.route('/astutus/doc')
def handle_doc():
    """ @app.route('/astutus/doc') """
    return flask.redirect(flask.url_for("handle_doc_top"))


@app.route('/astutus/doc/index.html')
def handle_doc_top():
    """ app.route('/astutus/doc/index.html') """
    logger.debug(f"app.root_path: {app.root_path}")
    directory = os.path.join(app.root_path, 'static', '_docs')
    print(f"directory: {directory}")
    return flask.send_from_directory(directory, 'index.html')


@app.route('/astutus/doc/<path:path>')
def handle_doc_path(path):
    """ app.route('/astutus/doc/<path:path>') """
    print(f"path: {path}")
    # print(f"filename: {filename}")
    logger.debug(f"app.root_path: {app.root_path}")
    real_path = os.path.join(app.root_path, 'static', '_docs', path)
    print(f"real_directory: {real_path}")
    return flask.send_file(real_path)


def run_with_standard_options():
    external_visible = "0.0.0.0"
    app.run(
        host=external_visible,
        port=5000,
        # use_debugger=True,
        # use_evalex=False,
    )


if __name__ == '__main__':
    astutus.web.flask_app.run_with_standard_options()
