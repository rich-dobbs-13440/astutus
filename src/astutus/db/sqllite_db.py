# import logging

# import sqlalchemy
# import sqlalchemy.ext.declarative
# import sqlalchemy.orm

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# This design was adapted from https://www.fullstackpython.com/sqlalchemy-model-examples.html

# engine = sqlalchemy.create_engine('sqlite:///astutus.sqlite', echo=True)
# db_session = sqlalchemy.orm.scoped_session(
#     sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Model = sqlalchemy.ext.declarative.declarative_base(name='Model')
# Model.query = db_session.query_property()


# def init_db():
#     Model.metadata.create_all(bind=engine)


# class RaspberryPi(Model):
#     __tablename__ = 'raspis'
#     id = sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
#     mac_addr = sqlalchemy.Column('mac_addr', sqlalchemy.String)
#     ipv4 = sqlalchemy.Column('ipv4', sqlalchemy.String)

# connection = engine.connect()
# logger.debug(f"MetaDate: {}")
# return connection
