"""
Database engine and shared session factory.

All modules that need database access should import `db_session` from here.
The DATABASE_URL can be overridden via the DATABASE_URL environment variable.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://catalog:catalog@localhost:5432/catalog",
)

engine = create_engine(DATABASE_URL)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()
