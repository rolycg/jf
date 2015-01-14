import sqlite3
import uuid as uu
import socket

__author__ = 'roly'


class DataLayer():
    def __init__(self, database_url):
        self.database_url = database_url
        self.database = sqlite3.connect(self.database_url, check_same_thread=False)
        self.cursor = self.database.cursor()

    def create_databases(self):
        self.cursor.execute('CREATE TABLE Login (username VARCHAR, password VARCHAR)')
        self.cursor.execute(
            'CREATE TABLE File (id INTEGER PRIMARY KEY, name_ext VARCHAR , root VARCHAR, file_type VARCHAR, '
            'parent INTEGER REFERENCES File(id), generation  INTEGER, machine VARCHAR REFERENCES Metadata(uuid))')
        self.cursor.execute('CREATE INDEX name_index ON  File (name_ext)')
        self.cursor.execute('CREATE TABLE Metadata (uuid VARCHAR, pc_name VARCHAR, last_generation INTEGER)')
        self.database.commit()

    def get_all_databases_elements(self, table):
        execute = 'SELECT * FROM ' + table
        self.cursor.execute(execute)
        return self.cursor

    def get_max_generation(self):
        return self.cursor.execute('SELECT max(generation) FROM File')

    def insert_username_password(self, username, password):
        self.cursor.execute('INSERT INTO Login VALUES (?,?)', (username, password))
        self.database.commit()

    def get_username_password(self):
        return self.cursor.execute('SELECT username, password FROM Login')

    def insert_peer(self, uuid=None, pc_name=None, ip=None):
        if not uuid and not pc_name and not ip:
            self.cursor.execute('INSERT INTO Metadata VALUES (?,?,?)',
                                (str(uu.uuid4()), socket.gethostname(), -1))
        else:
            self.cursor.execute('INSERT INTO Metadata VALUES (?,?,?)',
                                (str(uuid), pc_name, ip))
        self.database.commit()

    def edit_generation(self, uuid, generation):
        # execute = 'UPDATE Metadata SET last_generation = '' + str(generation) + ' WHERE uuid = ' + str(uuid)
        self.cursor.execute('UPDATE Metadata SET last_generation = ?   WHERE uuid = ?', (generation, str(uuid)))
        self.database.commit()


if __name__ == '__main__':
    data = DataLayer('test.db')

    data.edit_generation('51b08c6a-25bb-45be-9bf1-d7e71879fb49', 7)

