__author__ = 'roly'
from time import localtime
import json
import hashlib
import threading
import socket
import os
from multiprocessing import Queue, Process
from queue import Empty
from threading import Thread
import sqlite3
import time

from external_devices_layer import add_device
import main
import data_layer as data_layer_py
import comunication_layer as cl
import watch_layer
from extra_functions import convert_message, get_date


t2 = None


def finish_query(collection, data_layer, temp_res):
    for item in collection:
        t = localtime(item[8])
        try:
            temp_res.put('>Name: ' + str(item[2]) + '\n' + '>File Type: ' + str(item[4]) + '\n' + '>Address: '
                         + str(data_layer.get_address(item[1], item[7])) + '\n' + '>Machine: ' +
                         data_layer.get_peer_from_uuid(item[7]) + '\n' + '>Date: ' + str(t[0]) + '-' + str(
                t[1]) + '-' + str(t[2]) + '\n')
        except sqlite3.InterfaceError as e:
            print(e.__traceback__)
            break
        except sqlite3.ProgrammingError as e:
            print(e.__traceback__)
            break
    s_qp = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
    collection.close()
    data_layer.close()
    try:
        s_qp.connect('/tmp/process_com')
    except FileNotFoundError:
        print('FileNotFoundError')
    except ConnectionRefusedError:
        print('ConnectionRefusedError')
    s_qp.send(b'True')
    s_qp.close()


def open_writing():
    data_layer_py.set_query(False)
    cl.set_query(False)
    watch_layer.set_query(False)


def query_process_communication():
    global t2
    if os.path.exists('/tmp/process_com'):
        os.remove('/tmp/process_com')
    sqp = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sqp.bind('/tmp/process_com')
    sqp.listen(1)
    while 1:
        conn_qp, _ = sqp.accept()
        data = conn_qp.recv(10)
        if data:
            if t2 and t2.is_alive():
                t2.terminate()
            open_writing()


if __name__ == '__main__':
    t = None
    database_path = './database.db'
    temp_res = Queue()
    data_layer = None
    total_answers = 5
    path = '/'
    if not os.path.exists('/tmp/path_file.jf'):
        with open('/tmp/path_file.jf', 'w') as f:
            f.write(path)
    thread_cq = Thread(target=query_process_communication)
    thread_cq.start()
    allow_start = os.path.exists(database_path)
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
                password = _dict['password']
            except KeyError:
                continue
            if not allow_start:
                data_layer = data_layer_py.DataLayer('database.db')
                data_layer.create_databases()
                sha = hashlib.md5(password.encode())
                data_layer.insert_password(sha.hexdigest())
                data_layer.close()
                t = threading.Thread(target=main.create)
                t.start()
                allow_start = True
            else:
                date = get_date(database_path)
                date = localtime(date)
                date = str(date[0]) + '-' + str(date[1]) + '-' + str(date[2])
                message = 'Index has been made on ' + date + ', do you want re-index (Y/N).'
                conn.send(json.dumps({'message': message}).encode())
                value = conn.recv(1024)
                value = json.loads(value.decode())['answer']
                if value.lower().strip() == 'y':
                    os.remove(database_path)
                    data_layer = data_layer_py.DataLayer('database.db')
                    data_layer.create_databases()
                    sha = hashlib.md5(password.encode())
                    data_layer.insert_password(sha.hexdigest())
                    data_layer.close()
                    t = threading.Thread(target=main.create)
                    t.start()
                    allow_start = True
        if _dict['action'] == 'start':
            if not allow_start:
                conn.send(json.dumps({'message': 'Must create index first.'}).encode())
            else:
                while 1:
                    try:
                        password = _dict['password']
                    except KeyError:
                        continue
                    data_layer = data_layer_py.DataLayer('database.db')
                    u_p = data_layer.get_password()
                    data_layer.close()
                    sha = hashlib.md5(password.encode())
                    if sha.hexdigest() == u_p:
                        conn.send(json.dumps({'login': True}).encode())
                        try:
                            with open('/tmp/path_file.jf', 'r') as f:
                                path = f.readline()
                        except FileNotFoundError:
                            print('Path Error')
                        main.start(path)
                        break
                    else:
                        conn.send(json.dumps({'login': False}).encode())
                        break
        if _dict['action'] == 'query' or _dict['action'] == 'more':
            try:
                query = None
                more = None
                count = 5
                try:
                    query = _dict['query']
                except KeyError:
                    more = _dict['action']
                if query and t2 and t2.is_alive():
                    t2.terminate()
                if query and data_layer:
                    data_layer.close()
                if query:
                    cl.set_query(True)
                    data_layer_py.set_query(True)
                    watch_layer.set_query(True)
                    time.sleep(0.1)
                    query.strip()
                    temp_res = Queue()
                res = []
                if more:
                    count = 5
                    while count:
                        try:
                            res.append(temp_res.get(timeout=0.2))
                            count -= 1
                        except Empty:
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
                    t2 = Process(target=finish_query, args=(collection, data_layer, temp_res))
                    t2.start()
                    collection.close()
                    data_layer.close()
                s2 = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
                s2.settimeout(0.2)
                try:
                    s2.connect('/tmp/JF_ext_dv')
                except FileNotFoundError:
                    conn.send(json.dumps({'results': res}).encode())
                    continue
                except ConnectionRefusedError:
                    conn.send(json.dumps({'results': res}).encode())
                    continue
                except socket.timeout:
                    conn.send(json.dumps({'results': res}).encode())
                    continue
                s2.send(json.dumps({'messages': True}).encode())
                s2.settimeout(0.5)
                recv = s2.recv(10048)
                messages = []
                if recv:
                    messages = json.loads(recv.decode())
                try:
                    m = messages['messages']
                    if len(m):
                        conn.send(
                            json.dumps({'results': res, 'message': convert_message(messages['messages'])}).encode())
                    else:
                        conn.send(json.dumps({'results': res}).encode())
                except KeyError:
                    conn.send(json.dumps({'results': res}).encode())
            except Exception as e:
                print(str(e.args))
        if _dict['action'] == 'index':
            device = _dict['device']
            try:
                re_index = _dict['index']
            except KeyError:
                re_index = False
            ret = add_device(device, re_index)
            if not ret:
                conn.send(json.dumps({'results': 'Name device not found'}).encode())
            else:
                conn.send(json.dumps({'results': 'OK'}).encode())





