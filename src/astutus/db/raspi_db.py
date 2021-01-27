import json
import logging
from typing import Dict, List, Optional, Set, Tuple  # noqa

from astutus.db.sqlite_db import db

logger = logging.getLogger(__name__)


class RaspberryPi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_addr = db.Column(db.String, unique=True)
    ipv4 = db.Column(db.String)

    def __repr__(self) -> str:
        return f"RaspberryPi(id={self.id}, mac_addr='{self.mac_addr}', ipv4='{self.ipv4}')"

    def as_dict(self) -> Dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_json(self) -> str:
        return json.dumps(self.as_dict())
