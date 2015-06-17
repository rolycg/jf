import socket
import random
import re
import time
import json
import base64
import sqlite3
import datetime
import netifaces
from threading import Thread

from data_layer import semaphore as sem
import data_layer
import extra_functions as ef

query = False
PORT = 10101


def get_broadcast_address():
    broadcasts = []
    for x in netifaces.interfaces():
        addrs = netifaces.ifaddresses(x)
        try:
            q = addrs[netifaces.AF_INET]
        except KeyError:
            continue
        try:
            broadcasts.append(q[0]['broadcast'])
        except KeyError:
            continue
    return broadcasts


def message_broadcast():
    msg = b'I am JF'
    dest = get_broadcast_address()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    for d in dest:
        s.sendto(msg, (d, 10102))
    s.close()


def receive_broadcast(data_obj):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen(1)
    threads = []
    while 1:
        try:
            sock, address = s.accept()
            sock.close()
            data_layer.edit_status('network', [])
            data_layer.edit_status('network', [address[0]])
            threads.append(Thread(target=checking_client, args=(address, data_obj)))
            threads[len(threads) - 1].start()
        except socket.error:
            continue
        except socket.timeout:
            continue


def start_broadcast_server(data_obj, port=10101):
    while 1:
        try:
            host = ''
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, 10102))
            r = random.uniform(10, 20)
            s.settimeout(int(r))
            while 1:
                message, address = s.recvfrom(1024)
                if not message:
                    s.close()
                    break
                if message == b'I am JF':
                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((address[0], PORT))
                    s.close()
                    data_layer.edit_status('network', [])
                    data_layer.edit_status('network', [address[0]])
                    checking_server(data_obj)
                    break
        except socket.timeout:
            s.close()
            break
        except socket.error:
            s.close()
            break
        break


def network_main(data_obj):
    while 1:
        message_broadcast()
        start_broadcast_server(data_obj)


def start():
    data_obj = data_layer.DataLayer()
    while 1:
        try:
            password = data_obj.get_password()
        except sqlite3.OperationalError:
            time.sleep(10)
            continue
        if not password:
            time.sleep(10)
        else:
            break
    t = Thread(target=receive_broadcast, args=(data_obj,))
    t.start()
    network_main(data_obj=data_obj)


def set_query(value):
    global query
    query = value


def checking_client(address, data_obj):
    print('I am in checking client')
    time.sleep(50)
    time.sleep(0.5)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((address[0], PORT))
    password = data_obj.get_password()
    cipher = ef.get_cipher(password)
    ran_str = ef.random_string()
    sol = cipher.encrypt(ran_str)
    sock.settimeout(2)
    sock.send(sol)
    value = sock.recv(1000)
    sock.settimeout(15)
    if value.decode('LATIN-1') == ran_str:
        sock.send(b'OK')
        machine = data_obj.get_id_from_peer()
        name_machine = data_obj.get_peer_from_uuid(1)

        sock.send(json.dumps({'machine': machine, 'name_machine': name_machine}).encode())
        generation = sock.recv(1024)
        sender(sock, address, int(generation), data_obj)
    else:
        data_layer.edit_status('network', [])
        sock.close()


def checking_server(data_obj):
    print('I am in checking server')
    time.sleep(50)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen(1)
    sock, address = s.accept()
    password = data_obj.get_password()
    cipher = ef.get_cipher(password)
    plain_text = sock.recv(1000)
    value = cipher.decrypt(plain_text)
    sock.send(value)
    sock.settimeout(2)
    conf = sock.recv(1024)
    if conf == b'OK':
        uuid = sock.recv(1024)
        _dict = json.loads(uuid.decode(), encoding='LATIN-1')
        uuid = _dict['machine']
        name = _dict['name_machine']
        last_generation = data_obj.get_last_generation(uuid)
        if last_generation:
            sock.send(str(last_generation).encode())
        else:
            data_obj.insert_peer(uuid, name)
            sock.send(str(-1).encode())
        receiver(sock, address, uuid, data_obj)
    else:
        data_layer.edit_status('network', [])


def receiver(sock, address, uuid, data_obj):
    global query
    sock.send(data_obj.get_id_from_peer().encode())
    password = data_obj.get_password()
    cipher = ef.get_cipher(password)
    devices = data_obj.get_memory_devices()
    a = json.dumps({'devices': devices})
    time.sleep(2)
    sock.send(a.encode())
    _dict = {'add': [], 'delete': [], 'generation': ''}
    with sem:
        cont = 0
        test = b''
        balance = 0
        while 1:
            data = sock.recv(1000)
            test += data
            if data:
                for x in data.decode():
                    if x == '{':
                        balance += 1
                    if x == '}':
                        balance -= 1
            if not balance:
                break
        try:
            _dict = json.loads(test.decode())
            print(_dict)
        except ValueError:
            data_layer.edit_status('network', [])
            return
        for data in _dict['add']:
            value = cipher.decrypt(base64.b64decode(data))
            try:
                elements = re.split('\\?+', value.decode(encoding='LATIN-1'))
            except UnicodeDecodeError:
                elements = re.split('\\?+', value.decode(encoding='utf_8'))
            if not data_obj:
                data_obj = data_layer.DataLayer()
            elements[0] = elements[0][1:]
            elements[len(elements) - 1] = ef.unpad(elements[len(elements) - 1])
            elements = [x.strip() for x in elements]
            elements[len(elements) - 2] = data_obj.get_id_from_uuid(elements[len(elements) - 2])
            if elements[4] == '-1':
                data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[2],
                                     file_type=elements[3], generation=elements[5], peer=elements[6],
                                     first=True, date=elements[len(elements) - 1])
            else:
                data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[4],
                                     file_type=elements[3], generation=elements[5], peer=elements[6],
                                     first=False, date=elements[len(elements) - 1])
            if cont > 10000:
                data_obj.database.commit()
                cont = 0
            if query:
                data_obj.database.commit()
                data_obj.close()
                data_obj = None

                while query:
                    time.sleep(0.5)
    data_obj.database.commit()
    if _dict['generation']:
        data_obj.edit_generation(uuid, _dict['generation'])
    with sem:
        cont = 0
        for data in _dict['delete']:
            value = cipher.decrypt(base64.b64decode(data))
            try:
                elements = re.split('\\?+', value.decode(encoding='LATIN-1'))
            except UnicodeDecodeError:
                elements = re.split('\\?+', value.decode(encoding='utf_8'))
            if not data_obj:
                data_obj = data_layer.DataLayer()
            elements[0] = elements[0][1:]
            elements[len(elements) - 1] = ef.unpad(elements[len(elements) - 1], 0)
            elements = ef.convert_to_tuple(elements[0])
            elements = [x.strip()[1:-1] for x in elements]
            if elements[0] == 'deleted':
                data_obj.delete_data(elements[1], elements[2], data_obj.get_id_from_uuid(uuid))
            elif elements[0] == 'updated':
                data_obj.update_data(elements[1:], data_obj.get_id_from_uuid(uuid))
            if cont > 10000:
                data_obj.database.commit()
                cont = 0
            if query:
                data_obj.database.commit()
                data_obj.close()
                data_obj = None
            while query:
                time.sleep(0.5)
        data_obj.database.commit()
        cont = 0
        for key in _dict['devices'].keys():
            for data in _dict['devices'][key]:
                _id = data_obj.get_id_from_uuid(key)
                description = _dict['devices_description'][key][0]
                if _id:
                    data_obj.delete_files_from_drive(description[0])
                else:
                    data_obj.insert_peer(description[0], description[2], 1, description[3],
                                         datetime.datetime.now().timestamp())
                value = cipher.decrypt(base64.b64decode(data))
                try:
                    elements = re.split('\\?+', value.decode(encoding='LATIN-1'))
                except UnicodeDecodeError:
                    elements = re.split('\\?+', value.decode(encoding='utf_8'))
                if not data_obj:
                    data_obj = data_layer.DataLayer()
                elements[0] = elements[0][1:]
                elements[len(elements) - 1] = ef.unpad(elements[len(elements) - 1])
                elements = [x.strip() for x in elements]
                peer = data_obj.get_id_from_uuid(description[0])
                if elements[4] == '-1':
                    data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[2],
                                         file_type=elements[3], generation=elements[5], peer=peer,
                                         first=True, date=elements[len(elements) - 1])
                else:
                    data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[4],
                                         file_type=elements[3], generation=elements[5], peer=peer,
                                         first=False, date=elements[len(elements) - 1])
                if cont > 10000:
                    data_obj.database.commit()
                    cont = 0
                if query:
                    data_obj.database.commit()
                    data_obj.close()
                    data_obj = None
                    while query:
                        time.sleep(0.5)
    data_obj.database.commit()
    data_layer.edit_status('network', [])
    sock.close()


def sender(sock, address, generation, data_obj):
    uuid = sock.recv(100)
    uuid = uuid.decode()
    password = data_obj.get_password()
    query = data_obj.get_files(generation, data_obj.get_uuid_from_peer())
    _max = -1
    d = sock.recv(10024)
    devices = json.loads(d.decode())
    devices = devices['devices']
    cipher = ef.get_cipher(password)
    _dict = {'add': [], 'delete': [], 'generation': '', 'devices': {}, 'devices_description': {}}
    for x in query:
        tmp = data_obj.get_peer_from_id(x[len(x) - 2])
        x = (x[0], x[1], x[2], x[3], x[4], x[5], x[6], tmp, x[len(x) - 1])
        send = cipher.encrypt(ef.convert_to_str(x))
        _dict['add'].append(base64.b64encode(send).decode())
        _max = max(_max, x[6])
    if _max == -1:
        _dict['generation'] = ''
    else:
        _dict['generation'] = str(_max)
    _id = data_obj.get_id_from_uuid(uuid=uuid)
    if _max > -1:
        if _id:
            for y in data_obj.get_action_from_machine(_id):
                send = cipher.encrypt(ef.convert_to_str(y[0]))
                _dict['delete'].append(base64.b64encode(send).decode())
        else:
            data_obj.insert_peer(uuid, socket.gethostbyname(address[0]))
        data_obj.edit_my_generation(uuid, _max)
    my_devices = data_obj.get_memory_devices()
    result_devices = []
    if len(devices):
        for x in my_devices:
            for y in devices:
                if x[0] == y[0]:
                    if x[1] < y[1]:
                        _dict['devices_description'][x[0]] = result_devices
                        result_devices.append(x)
                else:
                    _dict['devices_description'][x[0]] = result_devices
                    result_devices.append(x)
    else:
        for x in my_devices:
            _dict['devices_description'][x[0]] = result_devices
            result_devices.append(x)
    for y in result_devices:
        q = data_obj.get_files(-1, data_obj.get_id_from_uuid(y[0]))
        for x in q:
            tmp = data_obj.get_peer_from_id(x[len(x) - 2])
            x = (x[0], x[1], x[2], x[3], x[4], x[5], x[6], tmp, x[len(x) - 1])
            print(x)
            a = ef.convert_to_str(x)
            print(len(a))
            send = cipher.encrypt(ef.convert_to_str(x))
            try:
                _dict['devices'][y[0]].append(base64.b64encode(send).decode())
            except KeyError:
                _dict['devices'][y[0]] = [base64.b64encode(send).decode()]
    try:
        sock.sendall(json.dumps(_dict).encode())
    except:
        data_layer.edit_status('network', [])
        return
    sock.close()
    with sem:
        data_obj.delete_actions_from_machine(_id)
    data_layer.edit_status('network', [])
