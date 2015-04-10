__author__ = 'roly'
from time import localtime
import json
import hashlib
import threading
import socket
import os

import main
import data_layer as data_layer_py
import comunication_layer as cl
import watch_layer


if __name__ == '__main__':
    if os.path.exists('./tmp/test'):
        os.remove('./tmp/test')
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind('./tmp/test')
    s.listen(1)
    collection = []
    # TODO: Fix all continue
    while 1:
        conn, _ = s.accept()
        data = conn.recv(2048)
        _dict = json.loads(data.decode(), encoding='utf-8')
        if _dict['action'] == 'create':
            try:
                user_name = _dict['username']
            except KeyError:
                continue
            try:
                password = _dict['password']
            except KeyError:
                continue
            data_layer = data_layer_py.DataLayer('database.db')
            data_layer.create_databases()
            sha = hashlib.md5(password.encode())
            data_layer.insert_username_password(user_name, sha.hexdigest())
            data_layer.close()
            t = threading.Thread(target=main.create)
            t.start()
            t.join()
            t2 = threading.Thread(target=main.start, args=(main.get_paths(),))
            t2.start()
        if _dict['action'] == 'start':
            while 1:
                try:
                    user_name = _dict['username']
                except KeyError:
                    continue
                try:
                    password = _dict['password']
                except KeyError:
                    continue
                data_layer = data_layer_py.DataLayer('database.db')
                u_p = data_layer.get_username_password()
                data_layer.close()
                sha = hashlib.md5(password.encode())
                if user_name == u_p[0] and sha.hexdigest() == u_p[1]:
                    conn.send(json.dumps({'login': True}).encode())
                    t2 = threading.Thread(target=main.start, args=(main.get_paths(),))
                    t2.start()
                    break
                else:
                    conn.send(json.dumps({'login': False}).encode())
                    break
                    # data = conn.recv(2048)
                    # _dict = json.loads(data.decode(), encoding='utf-8')
        if _dict['action'] == 'query' or _dict['action'] == 'more':
            query = None
            more = None
            count = 5
            try:
                query = _dict['query']
            except KeyError:
                more = _dict['action']
            cl.set_query(True)
            data_layer_py.set_query()
            watch_layer.set_query(True)
            if query:
                query.strip()
            res = []
            if query or more:
                data_layer = data_layer_py.DataLayer('database.db')
                if query:
                    collection = data_layer.find_data(query.split())
                for item in collection:
                    t = localtime(item[8])
                    res.append('>Name: ' + str(item[2]) + '\n' + '>File Type: ' + str(item[4]) + '\n' + '>Address: '
                               + str(data_layer.get_address(item[1], item[7])) + '\n' + '>Machine: ' +
                               data_layer.get_peer_from_uuid(item[7]) + '\n' + '>Date: ' + str(t[0]) + '-' + str(
                        t[1]) + '-' + str(t[2]) + '\n')
                    count -= 1
                    if not count:
                        break
            data_layer_py.set_query()
            cl.set_query(False)
            watch_layer.set_query(False)
            conn.send(json.dumps({'results': res}).encode())




