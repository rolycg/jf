__author__ = 'roly'
import json
import socket
import os
from multiprocessing import Pipe, Process
from threading import Thread
import time
import pwd

import external_devices_layer as edl
import data_layer as data_layer_py
import comunication_layer as cl
import watch_layer
from extra_functions import convert_message
import main

t2 = None
login = pwd.getpwuid(os.getuid())[0]


def finish_query(devices, data_layer, son):
    res = {}
    for x in devices.keys():
        for item in devices[x]:
            try:
                res[repr((x[0], x[1], x[2]))].append(repr(data_layer.get_address(item[1], item[7])))
            except KeyError:
                res[repr((x[0], x[1], x[2]))] = [repr(data_layer.get_address(item[1], item[7]))]
    s_qp = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
    son.send(json.dumps(res))
    for x in devices.keys():
        devices[x].close()
    data_layer.close()
    try:
        s_qp.connect('/tmp/process_com_' + login)
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
    if os.path.exists('/tmp/process_com_' + login):
        os.remove('/tmp/process_com_' + login)
    sqp = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sqp.bind('/tmp/process_com_' + login)
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
    if not os.path.exists('/usr/share/JF'):
        os.mkdir('/usr/share/JF')
    database_path = '/home/' + login + '/.local/share/JF/database.db'
    temp_res = Pipe()
    data_layer = None
    logged = False
    total_answers = 5
    parent = None
    son = None
    more_dict = None
    thread_cq = Thread(target=query_process_communication)
    thread_cq.start()
    allow_start = os.path.exists(database_path)
    if os.path.exists('/tmp/JF_' + login):
        os.remove('/tmp/JF_' + login)
    if not os.path.exists('/home/' + login + '/.local/share/JF'):
        os.mkdir('/home/' + login + '/.local/share/JF')
    if not os.path.exists(database_path):
        data_layer = data_layer_py.DataLayer()
        data_layer.create_databases()
        t = Thread(target=main.create, args=('/home',))
        t.start()
    else:
        t = Thread(target=main.start, args=(['/home'],))
        t.start()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind('/tmp/JF_' + login)
    s.listen(1)
    collection = []
    while 1:
        conn, _ = s.accept()
        data = conn.recv(2048)
        data = data.decode()
        if not data:
            continue
        _dict = json.loads(data, encoding='latin-1')
        if _dict['action'] == 'create':
            if not os.path.exists(_dict['path']):
                conn.send(json.dumps({'result': 'Not path'}).encode())
                continue
            if os.path.exists(database_path):
                os.remove(database_path)
            conn.send(json.dumps({'result': 'OK'}).encode())

            data_layer = data_layer_py.DataLayer()
            data_layer.create_databases()
            data_layer.insert_password(_dict['password'])
            data_layer.close()
            t = Thread(target=main.create, args=(_dict['path'],))
            t.start()
        elif _dict['action'] == 'query' or _dict['action'] == 'more':
            try:
                query = None
                more = None
                _from = None
                count = None
                try:
                    count = _dict['cant']
                    count = int(_dict['cant'])
                except KeyError:
                    count = 15
                try:
                    _from = _dict['from']
                except KeyError:
                    _from = None
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
                    if query:
                        query.strip()
                    parent, son = Pipe()
                res = {}
                if more:
                    if parent:
                        try:
                            d = parent.recv()
                            parent = None
                            more_dict = json.loads(d)
                            for x in more_dict.keys():
                                c = count
                                for item in more_dict[x].copy():
                                    try:
                                        res[x].append(item)
                                    except KeyError:
                                        res[x] = [item]
                                    more_dict[x].remove(item)
                                    c -= 1
                                    if not c:
                                        break
                        except Exception as e:
                            raise e
                    else:
                        for x in more_dict.keys():
                            c = count
                            for item in more_dict[x].copy():
                                try:
                                    res[x].append(item)
                                except KeyError:
                                    res[x] = [item]
                                more_dict[x].remove(item)
                                c -= 1
                                if not c:
                                    break
                if query:
                    data_layer = data_layer_py.DataLayer()
                    dev = data_layer.get_devices()
                    if _from:
                        __from = ''
                        for x in _from:
                            __from += x + ' '
                        dev = data_layer.get_device(__from.strip())
                        if len(dev):
                            devices = {dev[0]: data_layer.find_data(query.split(), dev[0][0])}
                        else:
                            devices = {}
                    else:
                        devices = {x: data_layer.find_data(query.split(), x[0]) for x in dev}
                    # collection = data_layer.find_data(query.split())
                    for x in devices.keys():
                        c = count
                        for item in devices[x]:
                            try:
                                res[str((x[0], x[1], x[2]))].append(str(data_layer.get_address(item[1], item[7])))
                            except KeyError:
                                res[str((x[0], x[1], x[2]))] = [str(data_layer.get_address(item[1], item[7]))]
                            c -= 1
                            if not c:
                                break
                    t2 = Process(target=finish_query, args=(devices.copy(), data_layer, son))
                    t2.start()
                    for x in devices.keys():
                        devices[x].close()
                    open_writing()
                    data_layer.close()
                s2 = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
                s2.settimeout(0.2)
                try:
                    s2.connect('/tmp/JF_ext_dv_' + login)
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
                raise e
        elif _dict['action'] == 'index':
            device = _dict['device']
            ret = edl.add_device(device, False)
            if not ret:
                conn.send(json.dumps({'results': 'Name device not found'}).encode())
            else:
                conn.send(json.dumps({'results': 'OK'}).encode())
