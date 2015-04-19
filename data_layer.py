import sqlite3
import uuid as uu
import socket
import os
import sys
from threading import Semaphore
import time

import extra_functions as ef


query = False


def set_query(value):
    global query
    query = value


__author__ = 'Roly'

semaphore = Semaphore()


class DataLayer():
    def __init__(self, database_url='database.db'):
        self.database_url = database_url
        self.database = sqlite3.connect(self.database_url, check_same_thread=False)
        # self.database.execute('PRAGMA read_uncommitted = FALSE ')
        self.cursor = self.database.cursor()
        # self.database.isolation_level = 'DEFERRED'

    def create_databases(self):
        cursor = self.database.cursor()
        cursor.execute(
            'CREATE TABLE Login (password VARCHAR)')
        cursor.execute(
            'CREATE TABLE File (_id INTEGER PRIMARY KEY AUTOINCREMENT,id INTEGER, name_ext VARCHAR , root VARCHAR, '
            'file_type VARCHAR, parent INTEGER REFERENCES File(id), generation  INTEGER, '
            'machine INTEGER REFERENCES Metadata(id), date_modified INTEGER)')
        cursor.execute('CREATE INDEX name_index ON  File (name_ext)')
        cursor.execute('CREATE INDEX id_index ON  File (id)')
        cursor.execute(
            'CREATE TABLE Metadata (id INTEGER PRIMARY KEY AUTOINCREMENT,uuid VARCHAR, '
            'pc_name VARCHAR, last_generation INTEGER, own INTEGER, my_generation INTEGER)')
        cursor.execute(
            'CREATE TABLE Journal '
            '(id INTEGER PRIMARY KEY AUTOINCREMENT, actio VARCHAR, machine INTEGER REFERENCES Metadata(id))')
        self.database.commit()
        cursor.close()

    def close(self):
        self.database.close()

    def get_action_from_machine(self, machine):
        ret = self.cursor.execute('SELECT actio FROM Journal WHERE machine=?', (machine,))
        return ret

    def delete_actions_from_machine(self, machine):
        cursor = self.database.cursor()
        cursor.execute('DELETE FROM Journal WHERE machine=?', (machine,))
        self.database.commit()
        cursor.close()

    def add_action(self, action, machine, generation):
        cursor = self.database.cursor()
        for x in cursor.execute('SELECT id FROM Metadata WHERE my_generation<=?', (generation,)):
            pass

    def get_last_generation(self, uuid):
        cursor = self.database.cursor()
        for value in cursor.execute('SELECT last_generation FROM Metadata WHERE uuid =?', (uuid,)):
            cursor.close()
            return value[0]

    def get_all_databases_elements(self, table):
        cursor = self.database.cursor()
        execute = 'SELECT * FROM ' + table
        cursor.execute(execute)
        return cursor

    def get_max_generation(self, machine=1):
        cursor = self.database.cursor()
        for value in cursor.execute('SELECT max(generation) FROM File WHERE machine=?', (machine,)):
            cursor.close()
            return value[0]

    def insert_password(self, password):
        cursor = self.database.cursor()
        cursor.execute('INSERT INTO Login VALUES (?)', (password,))
        self.database.commit()
        cursor.close()

    def get_password(self):
        cursor = self.database.cursor()
        for value in cursor.execute('SELECT password FROM Login'):
            cursor.close()
            return value

    def get_files(self, generation, peer):
        cursor = self.database.cursor()
        return cursor.execute('SELECT * FROM File WHERE generation>=? AND machine=? ORDER BY id ASC',
                              (generation, peer))

    def insert_peer(self, uuid=None, pc_name=None):

        cursor = self.database.cursor()
        if not uuid and not pc_name:
            cursor.execute('INSERT INTO Metadata VALUES (?,?,?,?,?)',
                           (None, str(uu.uuid4()), socket.gethostname(), -1, 1))
        else:
            try:
                cursor.execute('INSERT INTO Metadata VALUES (?,?,?,?,?)',
                               (None, uuid.decode(), pc_name, -1, 0))
            except AttributeError:
                cursor.execute('INSERT INTO Metadata VALUES (?,?,?,?,?)',
                               (None, str(uuid), pc_name, -1, 0))
        self.database.commit()
        cursor.close()

    def edit_generation(self, uuid, generation):
        cursor = self.database.cursor()
        # execute = 'UPDATE Metadata SET last_generation = '' + str(generation) + ' WHERE uuid = ' + str(uuid)
        generation = int(generation) + 1
        cursor.execute('UPDATE Metadata SET last_generation=?   WHERE uuid = ?', (generation, str(uuid)))
        self.database.commit()
        cursor.close()

    def edit_my_generation(self, uuid, generation):
        cursor = self.database.cursor()
        # execute = 'UPDATE Metadata SET last_generation = '' + str(generation) + ' WHERE uuid = ' + str(uuid)
        generation = int(generation) + 1
        cursor.execute('UPDATE Metadata SET my_generation=?   WHERE uuid = ?', (generation, str(uuid)))
        self.database.commit()
        cursor.close()

    def get_uuid_from_peer(self, owner=1):
        cursor = self.database.cursor()
        for value in self.cursor.execute('SELECT id FROM Metadata WHERE own =?', (owner,)):
            cursor.close()
            return value[0]

    def get_id_from_peer(self, owner=1):
        cursor = self.database.cursor()
        for value in cursor.execute('SELECT uuid FROM Metadata WHERE own =?', (owner,)):
            cursor.close()
            return value[0]

    def insert_file(self, id, file_name, parent, file_type, root, generation, peer, date=0):
        self.cursor.execute('INSERT INTO File VALUES (?,?,?,?,?,?,?,?,?,?)',
                            (None, id, file_name, root, file_type, parent, generation, peer, date, 0))

    def insert_data(self, id, file_name, file_type, parent, generation, peer=None, first=False, real_path=None,
                    date=None):
        if not first and real_path:
            _date = ef.get_date(real_path)
            if date:
                _date = date
            paren = self.get_parent(parent, real_path, peer)
            self.insert_file(id, file_name, paren, file_type, '', generation, peer, _date)
        elif not real_path and not first:
            if date:
                self.insert_file(id, file_name, parent, file_type, '', generation, peer, date)
            else:
                self.insert_file(id, file_name, parent, file_type, '', generation, peer)
        else:
            if date:
                self.insert_file(id, file_name, -1, file_type, parent, generation, peer, date)
            else:
                self.insert_file(id, file_name, -1, file_type, parent, generation, peer)

    def delete_data(self, name, real_path, machine):
        # cursor = self.database.cursor()
        # peer = self.get_uuid_from_peer()
        parent = self.get_parent(name, real_path, machine)
        self.cursor.execute('DELETE FROM File WHERE name_ext=? AND parent=? AND machine = ?', (name, parent, machine))
        # cursor.close()

    def get_parent(self, path, real_path, peer):
        cursor = self.database.cursor()
        tmp = []
        for value in cursor.execute('SELECT * FROM File WHERE id=? AND machine=?', (1, peer)):
            tmp.append(value)
        if len(tmp) == 1:
            walk = real_path.split(tmp[0][3])
            if len(walk) == 1 or not walk[1]:
                return tmp[0][1]
            if os.sep in walk[1]:
                walk = walk[1].split(os.sep)
            if sys.platform == 'linux':
                walk.pop(0)
            tmp = tmp[0]
            while len(walk):
                folder = walk[0]
                walk.pop(0)
                for value in cursor.execute('SELECT * FROM File WHERE name_ext=? AND parent=?',
                                            (folder, tmp[1])):
                    tmp = value
            cursor.close()
            return tmp[1]
            # real_paths = [self.get_address(x[0], peer) for x in tmp]
            # for x in range(len(real_paths) - 1, -1, -1):
            # if real_paths[x] == real_path:
            # return tmp[x][0]
            # raise Exception('Error')

        else:
            raise Exception('Error in database')

    def dynamic_insert_data(self, path, dirs, files, session_count, total_files, count, real_path, peer, generation=0):
        global query
        parent = self.get_parent(path, real_path, peer)
        for dir in dirs:
            count += 1
            date = ef.get_date(real_path + os.sep + dir)
            self.insert_file(total_files, dir, parent=parent, file_type='Folder', generation=0, root='',
                             peer=peer,
                             date=date)
            if count > 100000:
                self.database.commit()
                count = 0
            if query:
                self.database.commit()
                while query:
                    time.sleep(0.5)
            total_files += 1
        for file in files:
            count += 1
            date = ef.get_date(real_path + os.sep + file)
            _type = file.split('.')
            self.insert_file(file_name=file, file_type='' + _type[len(_type) - 1], parent=parent, generation=0,
                             root='', peer=peer, id=total_files, date=date)
            if count > 100000:
                self.database.commit()
                count = 0
            if query:
                self.database.commit()
                while query:
                    time.sleep(0.5)
            total_files += 1
        return session_count, total_files, count

    def get_element(self, item, peer):
        for x in self.cursor.execute('SELECT * FROM File WHERE id=? AND machine=?', (item, peer)):
            return x

    def get_address(self, item, peer):
        item = self.get_element(item, peer)
        address = ''
        while 1:
            if item[5] == -1:
                break
            address = str(item[2]) + os.sep + address
            tm = item[5], item[7]
            item = self.get_element(item[5], item[7])
            if not item:
                print(str(tm))
            if item[3]:
                address = str(item[3]) + os.sep + address
        return address[:len(address) - 1]

    def update_data(self, data, peer):
        parent = self.get_parent(data[len(data) - 2], data[len(data) - 1], peer)
        self.cursor.execute('UPDATE File SET name_ext=? WHERE name_ext=? AND parent=?',
                            (data[0], data[len(data) - 2], parent))

    def find_data(self, word_list):
        cursor = self.database.cursor()
        query = 'SELECT * FROM File WHERE '
        cont = 0
        l = len(word_list)
        while cont < l:
            if cont == 0:
                query += 'name_ext LIKE ?'
            else:
                query += ' OR name_ext LIKE ?'
            cont += 1
        query += ' ORDER BY date_modified DESC'
        word_list = ['%' + x + '%' for x in word_list]
        return cursor.execute(query, word_list)

    def get_cursor(self):
        return self.database.cursor()

    def get_peer_from_uuid(self, name):
        for value in self.cursor.execute('SELECT pc_name FROM Metadata WHERE id == ?', (name,)):
            return value[0]

    def get_peer_from_id(self, id):
        cursor = self.database.cursor()
        for value in cursor.execute('SELECT uuid FROM Metadata WHERE id=?', (id,)):
            cursor.close()
            return value[0]

    def get_id_from_uuid(self, uuid):
        cursor = self.database.cursor()
        for value in cursor.execute('SELECT id FROM Metadata WHERE uuid=?', (uuid,)):
            cursor.close()
            return value[0]

    def get_max_id(self, machine=1):
        cursor = self.database.cursor()
        for value in cursor.execute('SELECT max(id) FROM File WHERE machine=?', (machine,)):
            number = int(value[0])
            cursor.close()
            return number

    def get_id_from_device(self, device):
        cursor = self.database.cursor()
        _id = None
        for x in cursor.execute('SELECT id FROM Metadata WHERE uuid=?', (device,)):
            _id = x[0]
            break
        cursor.close()
        return _id

    def delete_drive(self, device):
        cursor = self.database.cursor()
        cursor.execute('DELETE FROM File WHERE machine = ?', (device,))
        cursor.execute('DELETE FROM Metadata WHERE id = ?', (device,))
        self.database.commit()
        cursor.close()


if __name__ == '__main__':
    data = DataLayer('database.db')
    # data.create_databases()
    id = data.get_id_from_device('276f15a5-0b53-4a0f-b130-4f56af55ec9f')
    print(id)
    data.delete_drive(id)
    for x in data.cursor.execute('SELECT * FROM File'):
        print(x)




