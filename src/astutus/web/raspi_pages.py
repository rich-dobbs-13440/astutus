import json
import logging
from http import HTTPStatus

import astutus.raspi
import flask

logger = logging.getLogger(__name__)

raspi_page = flask.Blueprint('raspi', __name__, template_folder='templates')
db = None

# wy_menu_vertical_list = [
#     '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc">Welcome</a></li>'
#     '<li class="toctree-l1"><a class="reference internal" href="/astutus">Browser Astutus</a></li>'
#     '<li class="toctree-l1"><a class="reference internal" href="/astutus/doc/command_line">Command Line Astutus</a></li>'  # noqa
# ]
# wy_menu_vertical = "\n".join(wy_menu_vertical_list)

static_base = "/static/_docs/_static"


def process_raspi_search_using_nmap(args):
    ipv4 = args.get("ipv4")
    logger.debug(f"ipv4: {ipv4}")
    mask = args.get("mask")
    logger.debug(f"mask: {mask}")
    filter = args.getlist("filter")
    logger.debug(f"filter: {filter}")
    search_result = astutus.raspi.search_using_nmap(ipv4, mask, filter)
    return display_raspi_find(search_result=search_result, filter=filter)


def get_items_list_as_json():
    items = astutus.db.RaspberryPi.query.all()
    items_list = []
    for item in items:
        items_list.append({'value': item.id, 'innerHTML': item.ipv4})
    return json.dumps(items_list)


def display_raspi_find(*, search_result, filter):
    breadcrumbs_list = [
        '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
        '<li><a href="/astutus">/astutus</a> &raquo;</li>',
        '<li><a href="/astutus/raspi">/raspi</a> &raquo;</li>',
        '<li>find=nmap</li>',
    ]
    breadcrumbs_list_items = "\n".join(breadcrumbs_list)
    return flask.render_template(
        'raspi/dyn_raspi_find.html',
        static_base=static_base,
        breadcrumbs_list_items=breadcrumbs_list_items,
        # wy_menu_vertical=wy_menu_vertical,
        search_result=search_result,
        filter=filter,
        raspi_items_list=get_items_list_as_json())


@raspi_page.route('/astutus/raspi', methods=['POST', 'GET'])
def handle_raspi():
    """ raspi_page.route('/astutus/raspi', methods=['POST', 'GET']) """
    if flask.request.method == 'GET':
        if flask.request.args.get("action") == "seach_using_nmap":
            logger.debug("Go to process_raspi_find_form")
            return process_raspi_search_using_nmap(flask.request.args)
        if flask.request.args.get('find') is not None:
            logger.debug("Go to display_raspi_find")
            return display_raspi_find(search_result=None, filter=["Raspberry"])
        # items = astutus.db.RaspberryPi.query.all()
        # links_list = []
        # for item in items:
        #     link = f'<li><p>See <a class="reference internal" href="/astutus/raspi/{item.id}"><span class="doc">{item.id}</span></a></p></li>'  # noqa
        #     links_list.append(link)
        # links = "\n".join(links_list)
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li>/raspi</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        return flask.render_template(
            'raspi/dyn_raspi.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            # wy_menu_vertical=wy_menu_vertical,
            # links=links,
            filter=["Raspberry"],
            raspi_items_list=get_items_list_as_json())

    if flask.request.method == 'POST':
        form = flask.request.form
        if form.get("action") == "create":
            raspi_ipv4 = form.get("raspi_ipv4")
            raspi_mac_addr = form.get("raspi_mac_addr")
            rpi = astutus.db.RaspberryPi(ipv4=raspi_ipv4, mac_addr=raspi_mac_addr)
            db.session.add(rpi)
            db.session.commit()
            logger.debug(f"rpi: {rpi}")
            return flask.redirect(flask.url_for('raspi.handle_raspi_item', idx=rpi.id))
        return "Case not handled", HTTPStatus.NOT_IMPLEMENTED


@raspi_page.route('/astutus/raspi/<int:idx>', methods=['PATCH', 'GET', 'DELETE'])
def handle_raspi_item(idx):
    """ raspi_page.route('/astutus/raspi/<int:idx>', methods=['POST', 'GET', 'DELETE']) """
    if flask.request.method == 'PATCH':
        request_data = flask.request.get_json(force=True)
        action = request_data.get('action')
        item = astutus.db.RaspberryPi.query.get(idx)
        raspi = astutus.raspi.RaspberryPi(db_data=item)
        if action == 'publish_wheels':
            raspi.publish_wheels()
            return "Publishing windows apparently succeeded.", HTTPStatus.OK
        if action == 'install_or_upgrade_astutus':
            raspi.uninstall_and_then_install_astutus()
            return "Install or upgrade Astutus apparently succeeded.", HTTPStatus.OK
        if action == 'launch_web_app':
            running, results = raspi.launch_web_app()
            # Results is a list, which Flask doesn't automatically turn into JSON
            web_results = flask.jsonify(results)
            if not running:
                # The BAD_GATEWAY HTTP status is selected because the
                # actual error probably happened on Raspberry Pi, or the
                # computer hosting this web application.  So this web server
                # is acting as a gateway to another server.
                return web_results, HTTPStatus.BAD_GATEWAY
            # The start up of the flask application can take a non trivial amount of time,
            # so OK can't be assumed or tested for.  However, the request
            # seems to have worked, so ACCEPTED is appropriate.
            return web_results, HTTPStatus.ACCEPTED

        raise NotImplementedError(f"The action '{action}'' is not handled.")
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
        if item is None:
            # Create a dummy item to display error message
            item = astutus.db.RaspberryPi(id=f"non-existent {idx}", ipv4="no such id", mac_addr="no such id")
        # items = astutus.db.RaspberryPi.query.all()
        # raspi_items_list = []
        # for item in items:
        #     raspi_items_list.append({'value': item.id, 'innerHTML': item.ipv4})
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/raspi">/raspi</a> &raquo;</li>',
            f'<li>/{item.id}</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        return flask.render_template(
            'raspi/dyn_raspi_item.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            # wy_menu_vertical=wy_menu_vertical,
            item=item,
            idx=idx,
            raspi_items_list=get_items_list_as_json())


@raspi_page.route('/astutus/raspi/<int:idx>/ifconfig', methods=['GET'])
def handle_raspi_item_ifconfig(idx):
    """" raspi_page.route('/astutus/raspi/<int:idx>/ifconfig', methods=['GET']) """
    if flask.request.method == 'GET':
        item = astutus.db.RaspberryPi.query.get(idx)
        raspi = astutus.raspi.RaspberryPi(db_data=item)
        ifconfig = raspi.get_ifconfig()
        # items = astutus.db.RaspberryPi.query.all()
        # raspi_items_list = []
        # for item in items:
        #     raspi_items_list.append({'value': item.id, 'innerHTML': item.ipv4})
        breadcrumbs_list = [
            '<li><a href="/astutus/doc" class="icon icon-home"></a> &raquo;</li>',
            '<li><a href="/astutus">/astutus</a> &raquo;</li>',
            '<li><a href="/astutus/raspi">/raspi</a> &raquo;</li>',
            f'<li><a href="/astutus/raspi/{idx}">/{idx}</a> &raquo;</li>',
            '<li>/ifconfig</li>',
        ]
        breadcrumbs_list_items = "\n".join(breadcrumbs_list)
        return flask.render_template(
            'raspi/dyn_item_ifconfig.html',
            static_base=static_base,
            breadcrumbs_list_items=breadcrumbs_list_items,
            idx=idx,
            ifconfig=ifconfig,
            raspi_items_list=get_items_list_as_json())
