import sqlite3

__author__ = 'roly'


class DataLayer():
    def __init__(self, database_url):
        self.database_url = database_url
        self.database = sqlite3.connect(self.database_url, check_same_thread=False)

    def create_databases(self):
        self.database.execute('CREATE TABLE Login (username VARCHAR, password VARCHAR)')
        self.database.execute(
            'CREATE TABLE File (id INTEGER PRIMARY KEY, name_ext VARCHAR , root VARCHAR, file_type VARCHAR, '
            'parent INTEGER REFERENCES File(id), generation  INTEGER)')
        self.database.execute('CREATE INDEX name_index ON  File (name_ext)')
        self.database.execute('CREATE TABLE Metadata (uuid VARCHAR, pc_name VARCHAR, last_generation INTEGER)')
        self.database.commit()

    def get_all_databases_elements(self, table):
        cursor = self.database.cursor()
        execute = 'SELECT * FROM ' + table
        cursor.execute(execute)
        return cursor

    def get_max_generation(self):
        cursor = self.database.cursor()
        return cursor.execute('SELECT max(generation) FROM File')

if __name__ == '__main__':
    data = DataLayer('test.db')
    data.create_databases()
    print(data.get_max_generation())