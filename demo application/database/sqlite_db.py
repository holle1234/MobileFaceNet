import sqlite3
from datetime import datetime
from pathlib import Path


class SqliteDB:

    __database_name = "data.db"

    def __init__(self, data_path):
        self.data_path = Path(data_path)  / self.__database_name
        self.db_conn = self.init_sqlite_db()

    def init_sqlite_db(self):
        conn = sqlite3.connect(self.data_path)
        table = '''CREATE TABLE IF NOT EXISTS PERSONS(
                    ID TEXT NOT NULL,
                    NAME TEXT NOT NULL,
                    IMAGE TEXT NOT NULL,
                    ADDED INT NOT NULL,
                    MATCHED_LAST INT NOT NULL,
                    MATCHED_TEMP INT NOT NULL,
                    N_MATCHES INT NOT NULL);'''
        make_index = '''CREATE INDEX IF NOT EXISTS Idx ON PERSONS(ID);'''
        conn.execute(table)
        conn.execute(make_index)
        return conn

    def write(self, name, unique_id, image_path):
        unique_id = str(unique_id).zfill(6)
        date = datetime.now()
        date_str = date.strftime('%d.%m.%Y %H:%M:%S')
        date_stamp = int(datetime.timestamp(date))

        statement = """
        INSERT INTO 'PERSONS'
            ('ID', 'NAME', 'N_MATCHES', 'IMAGE', 'ADDED', 'MATCHED_LAST', 'MATCHED_TEMP')
            VALUES (?, ?, ?, ?, ?, ?, ?);"""

        data_tuple = (unique_id, name, 0, image_path, date_stamp, date_stamp, date_stamp)
        self.db_conn.execute(statement, data_tuple)
        self.db_conn.commit()
        return unique_id, name, 0, image_path, date_str, date_str

    def read(self, unique_id):
        statement = '''
        UPDATE PERSONS
            SET 
                MATCHED_LAST = MATCHED_TEMP,
                MATCHED_TEMP = ?,
                N_MATCHES = N_MATCHES + 1
        WHERE ID=? 
        RETURNING 
            ID, 
            NAME, 
            N_MATCHES,
            IMAGE,
            strftime('%d.%m.%Y %H:%M:%S', datetime(ADDED, 'unixepoch', 'localtime')),
            strftime('%d.%m.%Y %H:%M:%S', datetime(MATCHED_LAST, 'unixepoch', 'localtime'))'''

        date = datetime.now()
        date_stamp = int(datetime.timestamp(date))
        ret = self.db_conn.execute(statement, (date_stamp, unique_id)).fetchone()
        self.db_conn.commit()
        return ret

    def remove(self, unique_id):
        statement = '''
        DELETE FROM 'PERSONS'
        WHERE ID=? 
        RETURNING 
            ID, 
            NAME, 
            N_MATCHES,
            IMAGE,
            strftime('%d.%m.%Y %H:%M:%S', datetime(ADDED, 'unixepoch', 'localtime')),
            strftime('%d.%m.%Y %H:%M:%S', datetime(MATCHED_LAST, 'unixepoch', 'localtime'))'''


        cursor = self.db_conn.execute(statement, (unique_id,))
        return cursor.fetchone()