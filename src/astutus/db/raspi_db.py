import json
import logging

import flask_sqlalchemy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

db = flask_sqlalchemy.SQLAlchemy()


def get_instance():
    return db


class RaspberryPi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_addr = db.Column(db.String, unique=True)
    ipv4 = db.Column(db.String)

    def __repr__(self):
        return f"RaspberryPi(id={self.id}, mac_addr='{self.mac_addr}', ipv4='{self.ipv4}')"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_json(self):
        return json.dumps(self.as_dict())