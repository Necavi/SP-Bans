from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from auth.manager import auth_manager
from players.helpers import uniqueid_from_index
from steam import SteamID


Base = declarative_base()
Session = sessionmaker()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    # http://docs.sqlalchemy.org/en/latest/orm/session_basics.html
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class BanRecord(Base):
    __tablename__ = "bans"

    id = Column(Integer, primary_key=True)
    target_id = Column(BigInteger, nullable=False)
    admin_id = Column(BigInteger)
    name = Column(String(128))
    start_date = Column(DateTime, default=func.now())
    stop_date = Column(DateTime)
    duration = Column(Integer, default=0)
    reason = Column(String(256))
    ip_address = Column(String(32))
    server_id = Column(Integer, default=-1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load()


class BanManager(object):
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        Base.metadata.create_all(self.engine)
        Session.configure(bind=self.engine)

    def add_ban(self, target, duration=0, admin=0, reason=None):
        target_id = SteamID.Parse(uniqueid_from_index(target)).to_uint64()
        if admin == 0:
            admin_id = None
        else:
            admin_id = SteamID.Parse(uniqueid_from_index(admin)).to_uint64()
        ban_record = BanRecord(target_id=target_id, admin_id=admin_id, duration=duration, reason=reason)
        with session_scope() as session:
            session.add(ban_record)


