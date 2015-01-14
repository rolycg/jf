import socket
import random
import json
import re

import data_layer
import extra_functions as ef


def broadcast():
    try:
        msg = b'I am everything'
        dest = ('255.255.255.255', 10101)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg, dest)
        s.settimeout(5)
        while 1:
            try:
                buf, address = s.recvfrom(1024)
                if not buf:
                    break
                if buf == b'Mee too':
                    checking_client(s, address)
                    break
            except socket.error:
                break
            except socket.timeout:
                break
    except OSError:
        pass


def start_broadcast_server(port=10101):
    while 1:
        try:
            host = ''
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind((host, port))
            s.settimeout(15)
            while 1:
                message, address = s.recvfrom(1024)
                if not message:
                    s.close()
                    break
                if message == b'I am everything':
                    s.sendto(b'Mee too', address)
                    checking_server(s, address)
        except socket.timeout:
            r = random.uniform(1, 8)
            if r == 3:
                break
            continue
        except socket.error:
            s.close()
            continue


def start():
    while 1:
        broadcast()
        start_broadcast_server()


def checking_client(sock, address):
    username, password = data_layer.get_username_password()
    cipher = ef.get_cipher(password)
    sock.sendto(username.encode(), address)
    answer, _ = sock.recvfrom(100)
    if answer == b'OK':
        ran_str = ef.random_string()
        sol = cipher.encrypt(ran_str)
        sock.settimeout(2)
        sock.sendto(sol, address)
        value, _ = sock.recvfrom(1000)
        sock.settimeout(15)
        if value.decode() == ran_str:
            sock.sendto(b'OK', address)
            session = data_layer.get_session(data_layer.get_engine())
            machine = session.query(data_layer.Metadata).filter(data_layer.Metadata._id == 1)
            tmp = None
            for x in machine:
                tmp = x
            sock.sendto(str(tmp._uuid).encode(), address)
            generation, _ = sock.recvfrom(1024)
            sender(sock, address, int(generation))


def checking_server(sock, address):
    username, password = data_layer.get_username_password()
    cipher = ef.get_cipher(password)
    user, _ = sock.recvfrom(1000)
    if user.decode() == username:
        sock.sendto(b'OK', address)
        plain_text, _ = sock.recvfrom(1000)
        value = cipher.decrypt(plain_text)
        sock.sendto(value, address)
        conf, _ = sock.recvfrom(1024)
        if conf == b'OK':
            uuid, _ = sock.recvfrom(1024)
            receiver(sock, address, uuid)


def receiver(sock, address, uuid):
    _, password = data_layer.get_username_password()
    engine = data_layer.get_engine()
    session = data_layer.get_session(engine)
    gen = session.query(data_layer.Metadata).filter(data_layer.Metadata._uuid == uuid)
    machine = None
    for x in gen:
        machine = x
    if machine:
        sock.sendto(str(machine.last_generation).encode(), address)
    else:
        data_layer.insert_peer(engine, uuid, socket.gethostbyname(address[0]), '127.0.0.1')
        sock.sendto(str(-1).encode(), address)
    cipher = ef.get_cipher(password)
    while 1:
        data, _ = sock.recvfrom(1024)
        if data == b'finish':
            break
        else:
            _dict = json.loads(data.decode())
            for x in _dict.keys():
                value = cipher.decrypt(_dict[x])
                elements = re.split(',+', value)
                elements[0] = elements[0][1:]
                elements[len(elements) - 1] = elements[len(elements) - 1][0:len(elements) - 1]
                if elements[2]:
                    data_layer.insert_data(engine, elements[1], elements[3], elements[2], elements[6], True)
                else:
                    data_layer.insert_data(engine, elements[1], elements[3], elements[2], elements[6], False)
    gen, _ = sock.recvfrom(1024)
    session.query(data_layer.Metadata).filter(data_layer.Metadata._uuid == uuid).update({'last_generation': int(gen)})


def sender(sock, address, generation):
    _, password = data_layer.get_username_password()
    session = data_layer.get_session(data_layer.get_engine())
    query = session.query(data_layer.File).filter(data_layer.File.generation > generation)
    _max = -1
    cipher = ef.get_cipher(password)
    _dict = {}
    cont = 0
    for x in query:
        _dict[cont] = cipher.encrypt(str(x))
        cont += 1
        _max = max(_max, x.generation)
    sock.sendto(json.dumps(_dict).encode(), address)
    sock.sendto(b'finish', address)
    sock.sendto(str(_max).encode(), address)
