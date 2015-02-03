import sqlite3
import uuid as uu
import socket
import os


__author__ = 'roly'


class DataLayer():
    def __init__(self, database_url):
        self.database_url = database_url
        self.database = sqlite3.connect(self.database_url, check_same_thread=False)
        self.cursor = self.database.cursor()

    def create_databases(self):
        self.cursor.execute(
            'CREATE TABLE Login (username VARCHAR, password VARCHAR)')
        self.cursor.execute(
            'CREATE TABLE File (id INTEGER PRIMARY KEY AUTOINCREMENT, name_ext VARCHAR , root VARCHAR, '
            'file_type VARCHAR, parent INTEGER REFERENCES File(id), generation  INTEGER, '
            'machine VARCHAR REFERENCES Metadata(uuid))')
        self.cursor.execute('CREATE INDEX name_index ON  File (name_ext)')
        self.cursor.execute(
            'CREATE TABLE Metadata (uuid VARCHAR, pc_name VARCHAR, last_generation INTEGER, own INTEGER)')
        self.database.commit()

    def get_last_generation(self, uuid):
        for value in self.cursor.execute('SELECT last_generation FROM Metadata WHERE uuid =?', (uuid,)):
            return value[0]

    def get_all_databases_elements(self, table):
        execute = 'SELECT * FROM ' + table
        self.cursor.execute(execute)
        return self.cursor

    def get_max_generation(self):
        for value in self.cursor.execute('SELECT max(generation) FROM File'):
            return value[0]

    def insert_username_password(self, username, password):
        self.cursor.execute('INSERT INTO Login VALUES (?,?)', (username, password))
        self.database.commit()

    def get_username_password(self):
        for value, value2 in self.cursor.execute('SELECT username, password FROM Login'):
            return value, value2

    def get_files(self, generation):
        return self.cursor.execute('SELECT * FROM File WHERE genration>?', (generation,))

    def insert_peer(self, uuid=None, pc_name=None, ip=None):
        if not uuid and not pc_name and not ip:
            self.cursor.execute('INSERT INTO Metadata VALUES (?,?,?,?)',
                                (str(uu.uuid4()), socket.gethostname(), -1, 1))
        else:
            self.cursor.execute('INSERT INTO Metadata VALUES (?,?,?,?)',
                                (str(uuid), pc_name, ip, 0))
        self.database.commit()

    def edit_generation(self, uuid, generation):
        # execute = 'UPDATE Metadata SET last_generation = '' + str(generation) + ' WHERE uuid = ' + str(uuid)
        self.cursor.execute('UPDATE Metadata SET last_generation = ?   WHERE uuid = ?', (generation, str(uuid)))
        self.database.commit()

    def get_uuid_from_peer(self, owner=1):
        for value in self.cursor.execute('SELECT uuid FROM Metadata WHERE own =?', (owner,)):
            return value[0]

    def insert_file(self, file_name, parent, file_type, root, generation, peer):
        self.cursor.execute('INSERT INTO File VALUES (?,?,?,?,?,?,?)',
                            (None, file_name, root, file_type, parent, generation, peer))

    def insert_data(self, file_name, file_type, parent, generation, peer=None, first=False, real_path=None):
        if not first and real_path:
            paren = self.get_parent(parent, real_path, peer)
            self.insert_file(file_name, paren, file_type, '', generation, peer)
        elif not real_path and not first:
            self.insert_file(file_name, parent, file_type, '', generation, peer)
        else:
            self.insert_file(file_name, -1, file_type, parent, generation, peer)
        self.database.commit()

    def delete_data(self, name):
        peer = self.get_uuid_from_peer()
        self.cursor.execute('DELETE FROM File WHERE name_ext=? AND machine = ?', (name, peer))
        self.database.commit()

    def get_parent(self, path, real_path, peer):
        tmp = []
        for value in self.cursor.execute('SELECT * FROM File WHERE name_ext=? AND machine=?', (path, peer)):
            tmp.append(value)
        if len(tmp) > 1:
            real_paths = [self.get_address(x[0], peer) for x in tmp]
            for x in range(len(real_paths) - 1, -1, -1):
                if real_paths[x] == real_path:
                    return tmp[x][0]
            raise Exception('Error')
        else:
            return tmp[0][0]

    def dynamic_insert_data(self, path, dirs, files, session_count, total_files, count, real_path, peer):
        parent = self.get_parent(path, real_path, peer)
        for dir in dirs:
            self.insert_file(dir, parent=parent, file_type='Folder', generation=0, root='', peer=peer)
            total_files += 1
        for file in files:
            _type = file.split('.')
            self.insert_file(file_name=file, file_type='File: ' + _type[len(_type) - 1], parent=parent, generation=0,
                             root='', peer=peer)
            total_files += 1
        return session_count, total_files, count

    def get_element(self, item, peer):
        for x in self.cursor.execute('SELECT * FROM File WHERE id=? AND machine=?', (item, peer)):
            return x

    def get_address(self, item, peer):
        item = self.get_element(item, peer)
        address = ''
        while 1:
            if item[4] == -1:
                break
            address = str(item[1]) + os.sep + address
            item = self.get_element(item[4], item[6])
            if item[2]:
                address = str(item[2]) + os.sep + address
        return address[:len(address) - 1]

    def find_data(self, word_list):
        return self.cursor.execute('SELECT * FROM File WHERE name_ext LIKE ?', ('%' + word_list[0] + '%',))

    def get_peer_from_uuid(self, name):
        for value in self.cursor.execute('SELECT pc_name FROM Metadata WHERE uuid == ?', (name,)):
            return value[0]


if __name__ == '__main__':
    data = DataLayer('database.db')
    print(data.get_last_generation(data.get_uuid_from_peer()))



