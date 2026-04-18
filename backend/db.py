import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        with current_app.open_resource('schema.sql') as f:
            g.db.executescript(f.read().decode('utf8'))
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()