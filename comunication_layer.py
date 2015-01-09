import socket
import random

import data_layer
import extra_functions as ef


username = 'bla'
password = 'bla2'


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
    cipher = ef.get_cipher(password)
    sock.sendto(username.encode(), address)
    answer, _ = sock.recvfrom(100)
    if answer == b'OK':
        ran_str = ef.random_string()
        sol = cipher.encrypt(ran_str)
        sock.settimeout(2)
        sock.sendto(sol.enconde(), address)
        value, _ = sock.recvfrom(1000)
        sock.settimeout(15)
        if cipher.decrypt(value.decode()) == ran_str:
            sock.sendto(b'OK', addr=address)
            generation = int(sock.recvfrom(1024))
            switch_data(sock, address, generation)


def checking_server(sock, address):
    cipher = ef.get_cipher(password)
    user, _ = sock.recvfrom(1000)
    if user.decode() == username:
        sock.sendto(b'OK', address)
        plain_text = sock.recvfrom(1000)
        value = cipher.decrypt(plain_text)
        sock.sendto(value.encode(), addr=address)
        conf = sock.recvfrom(1024)
        if conf == b'OK':
            receiver(sock, address)


def switch_data(sock, address, generation):
    sock.connectto(address)
    sender(sock, address, generation)


def receiver(sock, address):
    session = data_layer.get_session(data_layer.get_engine())
    gen = session.query(data_layer.Metadata).get(data_layer.Metadata.ip_address == str(address[0]))
    sock.sendto(gen.generation, address)
    while 1:
        data = sock.recvfrom(1024)
        if data == b'finish':
            break
            # ver que llega a data
    gen = sock.recvfrom(1024)
    session = data_layer.get_session(data_layer.get_engine())
    session.query(data_layer.Metadata).filter(data_layer.Metadata.ip_address == str(address[0])).update(
        {'generation': int(gen)})


def sender(sock, address, generation):
    session = data_layer.get_session(data_layer.get_engine())
    query = session.query(data_layer.File).filter(data_layer.File.last_generation > generation)
    _max = -1
    for x in query:
        sock.sendto(x, address)
        _max = max(_max, x.generation)
    sock.sendto(b'finish', address)
    sock.sendto(_max, address)
