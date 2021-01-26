import json
from typing import Dict, List, Optional, Set, Tuple  # noqa

from astutus.db.sqlite_db import db


class Logger(db.Model):
    name = db.Column(db.String, primary_key=True)
    level = db.Column(db.Integer)

    def __repr__(self):
        return f"Logger(name={self.name}, level={self.level})"

    def as_dict(self) -> Dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_json(self) -> str:
        return json.dumps(self.as_dict())
