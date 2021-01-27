import logging
import os
import re
import pathlib
from typing import Dict, List, Optional, Set, Tuple  # noqa

import astutus.util
import flask_sqlalchemy
import sqlalchemy.exc
import sqlalchemy.schema

logger = logging.getLogger(__name__)

db = flask_sqlalchemy.SQLAlchemy()


def get_instance() -> flask_sqlalchemy.SQLAlchemy:
    return db


def initialize_db_if_needed() -> None:
    """ Initialize the database for the application as and if needed.

    The directory implied by the sqlite database URL is created,
    and the database and it's tables are created.

    Please note that at this time, upgrading the database is not
    handled, as the database is considered transient, rather than
    being used for long term storage.  If the database is outdated,
    it should be deleted, and then it will be recreated with the
    current schema.
    """
    url = get_url()
    matches = re.match(r'^sqlite:\/\/\/(.+)$', url)
    dirpath = pathlib.Path(matches.group(1)).parent
    os.makedirs(dirpath, exist_ok=True)

    metadata = sqlalchemy.schema.MetaData()
    metadata.reflect(db.engine)
    logger.debug(f"metadata.tables {str(metadata.tables)}")
    if len(metadata.tables) == 0:
        logger.debug("creating tables")
        db.create_all()
        metadata.reflect(db.engine)
        logger.debug(f"metadata.tables {str(metadata.tables)}")
    assert 'raspberry_pi' in metadata.tables.keys()


def get_url() -> str:
    """  Get the sqlite database URL used for this application.

    Defaults to sqlite:////~/.astutus/astutus.db, where ~ is replaced by the
    absolute path to the user's home directory.

    Can be overridden by definining the environment variable ASTUTUS_DB_URL
    """
    db_url = os.environ.get("ASTUTUS_DB_URL")
    if db_url is None:
        db_url = 'sqlite:///' + os.path.join(astutus.util.get_user_data_path(), 'astutus.db')
    return db_url
