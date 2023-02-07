CREATE_TABLE = """CREATE TABLE slots
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    time INTEGER NOT NULL UNIQUE);"""

SELECT_ALL_SLOTS = "SELECT time FROM slots"
CREATE_SLOT = "INSERT INTO slots (username, time) VALUES('{username}', '{time}')"
