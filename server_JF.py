__author__ = 'roly'
from time import localtime
import json
import hashlib
import threading
import socket
import os

from external_devices_layer import add_device
import main
import data_layer as data_layer_py
import comunication_layer as cl
import watch_layer
from extra_functions import convert_message


temp_res = []


def finish_query(collection, data_layer):
    global temp_res
    temp_res = []
    for item in collection:
        t = localtime(item[8])
        temp_res.append('>Name: ' + str(item[2]) + '\n' + '>File Type: ' + str(item[4]) + '\n' + '>Address: '
                        + str(data_layer.get_address(item[1], item[7])) + '\n' + '>Machine: ' +
                        data_layer.get_peer_from_uuid(item[7]) + '\n' + '>Date: ' + str(t[0]) + '-' + str(
            t[1]) + '-' + str(t[2]) + '\n')
    open_writing()


def open_writing():
    data_layer_py.set_query()
    cl.set_query(False)
    watch_layer.set_query(False)


if __name__ == '__main__':
    t = None
    allow_start = os.path.exists('./database.db')
    if os.path.exists('/tmp/JF'):
        os.remove('/tmp/JF')
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind('/tmp/JF')
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
            allow_start = True
        if _dict['action'] == 'start':
            if not allow_start:
                conn.send(json.dumps({'message': 'Must create index first.'}).encode())
            else:
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
        if _dict['action'] == 'query' or _dict['action'] == 'more':
            query = None
            more = None
            count = 5
            try:
                query = _dict['query']
            except KeyError:
                more = _dict['action']
            if query and data_layer:
                data_layer.close()
            if query and t2 and t2.is_alive():
                t._stop()
            cl.set_query(True)
            data_layer_py.set_query()
            watch_layer.set_query(True)
            if query:
                query.strip()
            res = []
            if more:
                res = temp_res[:5]
                for x in range(5):
                    try:
                        temp_res.pop(0)
                    except KeyError and IndexError:
                        break
            if query:
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
                # TODO: Ver esto esta raro se demora mucho pero hay que hacerlo
                # t2 = Thread(target=finish_query(collection, data_layer))
                # t2.start()
                open_writing()
            s2 = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
            try:
                s2.connect('/tmp/JF_ext_dv')
            except FileNotFoundError:
                conn.send(json.dumps({'results': res}).encode())
                continue
            s2.send(json.dumps({'messages': True}).encode())
            s2.settimeout(0.5)
            recv = s2.recv(10048)
            print(recv)
            messages = []
            if recv:
                messages = json.loads(recv.decode())
            if len(messages.keys()):
                conn.send(json.dumps({'results': res, 'message': convert_message(messages['messages'])}).encode())
                messages = []
            else:
                conn.send(json.dumps({'results': res}).encode())
        if _dict['action'] == 'index':
            device = _dict['device']
            ret = add_device(device)
            if not ret:
                conn.send(json.dumps({'results': 'Name device not found'}).encode())
            else:
                conn.send(json.dumps({'results': 'OK'}).encode())





