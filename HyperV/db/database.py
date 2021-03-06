# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from HyperV.util.config import config
import os

engine = create_engine(config.DB_URL, convert_unicode=True)

# engine = create_engine(config.DB_URL, convert_unicode=True, pool_recycle=500, pool_size=5, max_overflow=20, echo=False,
#                        echo_pool=True, extend_existing=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(engine)
