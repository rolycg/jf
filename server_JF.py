__author__ = 'roly'
from time import localtime
import json
import hashlib
import threading
import time
import socket
import os

import main
import data_layer as data_layer_py
import comunication_layer as cl
import watch_layer


if __name__ == '__main__':
    if os.path.exists('./temp/test'):
        os.remove('./temp/test')
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.bind('./tmp/test')
    s.listen(1)
    # TODO: FIX all continue
    while 1:
        conn, _ = s.accept()
        data = conn.recv(2048)
        if data:
            _dict = json.loads(data, encoding='utf-8')
        else:
            time.sleep(0.8)
            continue
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
                t2 = threading.Thread(target=main.start, args=(main.get_paths(),))
                t2.start()
            else:
                continue
        if _dict['action'] == 'query':
            try:
                query = _dict['query']
            except KeyError:
                continue
            cl.set_query(True)
            data_layer_py.set_query()
            watch_layer.set_query(True)
            if not query.strip():
                continue
            data_layer = data_layer_py.DataLayer('database.db')
            res = []
            for item in data_layer.find_data(query.split()):
                t = localtime(item[8])
                res.append('>Name: ' + str(item[2]) + '\n' + '>File Type: ' + str(item[4]) + '\n' + '>Address: '
                           + str(data_layer.get_address(item[1], item[7])) + '\n' + '>Machine: ' +
                           data_layer.get_peer_from_uuid(item[7]) + '\n' + '>Date: ' + str(t[0]) + '-' + str(
                    t[1]) + '-' + str(
                    t[2]) + '\n')
            data_layer_py.set_query()
            cl.set_query(False)
            watch_layer.set_query(False)
            conn.send(json.dumps({'results': res}).encode())




