from peewee import SqliteDatabase
from ..config import DATABASE_PATH
_database = None

def get_database():
    global _database
    if _database is None:
        _database = SqliteDatabase(DATABASE_PATH)
    return _database

def init_database():
    from .models import Trade, Price, FetchLog
    db = get_database()
    db.create_tables([Trade, Price, FetchLog])
    return

def close_database():
    db = get_database()
    if not db.is_closed():
        db.close()
    return



