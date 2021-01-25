import logging
from http import HTTPStatus

import astutus.raspi
import flask

logger = logging.getLogger(__name__)

raspi_page = flask.Blueprint('raspi', __name__, template_folder='templates')
db = None


def process_raspi_search_using_nmap(args):
    ipv4 = args.get("ipv4")
    logger.debug(f"ipv4: {ipv4}")
    mask = args.get("mask")
    logger.debug(f"mask: {mask}")
    filter = args.getlist("filter")
    logger.debug(f"filter: {filter}")
    search_result = astutus.raspi.search_using_nmap(ipv4, mask, filter)
    return display_raspi_find(search_result=search_result, filter=filter)


def get_items_list():
    items = astutus.db.RaspberryPi.query.all()
    items_list = []
    for item in items:
        items_list.append({'value': item.id, 'link_text': item.ipv4})
    return items_list


def display_raspi_find(*, search_result, filter):
    return flask.render_template(
        'app/raspi/styled_index.html',
        search_result=search_result,
        filter=filter,
        idx_item_list=get_items_list())


@raspi_page.route('/astutus/app/raspi/index.html', methods=['POST', 'GET'])
def handle_raspi():
    if flask.request.method == 'GET':
        if flask.request.args.get("action") == "seach_using_nmap":
            logger.debug("Go to process_raspi_find_form")
            return process_raspi_search_using_nmap(flask.request.args)
        if flask.request.args.get('find') is not None:
            logger.debug("Go to display_raspi_find")
            return display_raspi_find(search_result=None, filter=["Raspberry"])
        return flask.render_template(
            'app/raspi/styled_index.html',
            filter=["Raspberry"],
            idx_item_list=get_items_list())

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


@raspi_page.route('/astutus/app/raspi/<int:idx>', methods=['PATCH'])
def handle_raspi_item_rest(idx):
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


@raspi_page.route('/astutus/app/raspi/<int:idx>/index.html', methods=['GET', 'DELETE'])
def handle_raspi_item(idx):
    if flask.request.method == 'DELETE':
        item = astutus.db.RaspberryPi.query.get(idx)
        db.session.delete(item)
        db.session.commit()
        data = {
            "redirect_url": "/astutus/app/raspi/index.html"
        }
        return data, HTTPStatus.ACCEPTED
    if flask.request.method == 'GET':
        item = astutus.db.RaspberryPi.query.get(idx)
        if item is None:
            # Create a dummy item to display error message
            item = astutus.db.RaspberryPi(id=f"non-existent {idx}", ipv4="no such id", mac_addr="no such id")
        return flask.render_template(
            'app/raspi/idx/styled_index.html',
            item=item,
            idx_item_list=get_items_list())


@raspi_page.route('/astutus/app/raspi/<int:idx>/ifconfig.html', methods=['GET'])
def handle_raspi_item_ifconfig(idx):
    if flask.request.method == 'GET':
        item = astutus.db.RaspberryPi.query.get(idx)
        raspi = astutus.raspi.RaspberryPi(db_data=item)
        ifconfig = raspi.get_ifconfig()
        return flask.render_template(
            'app/raspi/idx/styled_ifconfig.html',
            idx=idx,
            ifconfig=ifconfig,
            idx_item_list=get_items_list())
