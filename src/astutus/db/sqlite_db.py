import logging
import os
import re
import pathlib

import astutus.util
import flask_sqlalchemy
import sqlalchemy.exc
import sqlalchemy.schema

logger = logging.getLogger(__name__)

db = flask_sqlalchemy.SQLAlchemy()


def get_instance():
    return db


def initialize_db_if_needed():
    url = get_url()
    matches = re.match(r'^sqlite:\/\/\/(.+)$', url)
    dirpath = pathlib.Path(matches.group(1)).parent
    os.makedirs(dirpath, exist_ok=True)

    metadata = sqlalchemy.schema.MetaData()
    metadata.reflect(db.engine)
    logger.error(f"metadata.tables {str(metadata.tables)}")
    if len(metadata.tables) == 0:
        logger.error("creating tables")
        db.create_all()
        metadata.reflect(db.engine)
        logger.error(f"metadata.tables {str(metadata.tables)}")
    assert 'raspberry_pi' in metadata.tables.keys()


def get_url():
    db_url = os.environ.get("ASTUTUS_DB_URL")
    if db_url is None:
        db_url = 'sqlite:///' + os.path.join(astutus.util.get_user_data_path(), 'astutus.db')
    return db_url
