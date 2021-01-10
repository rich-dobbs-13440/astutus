import json

from astutus.db.sqlite_db import db


class Logger(db.Model):
    name = db.Column(db.String, primary_key=True)
    level = db.Column(db.Integer)

    def __repr__(self):
        return f"Logger(name={self.name}, level={self.level})"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_json(self):
        return json.dumps(self.as_dict())
