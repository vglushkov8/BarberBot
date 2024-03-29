SLOTS_CREATE_TABLE = """CREATE TABLE slots
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    time TEXT NOT NULL UNIQUE);"""

BARBER_CREATE_TABLE = """CREATE TABLE barber
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL);"""

SELECT_ALL_SLOTS = "SELECT time FROM slots"
CREATE_SLOT = "INSERT INTO slots (user_id, time) VALUES('{user_id}', '{time}')"
SELECT_BARBER_CHAT_ID = "SELECT chat_id FROM barber WHERE id = 1"
CREATE_BARBER_CHAT_ID = "INSERT OR REPLACE INTO barber (id, chat_id) VALUES ('1', '{chat_id}');"
