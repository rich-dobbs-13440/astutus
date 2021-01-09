# import json
import logging
# from http import HTTPStatus

# import astutus.log
import flask
import flask.logging

logger = logging.getLogger(__name__)
logger.addHandler(flask.logging.default_handler)

log_page = flask.Blueprint('ulog', __name__, template_folder='templates')
