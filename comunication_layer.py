import socket
import ssl

import data_layer

import extra_functions as ef


username = 'bla'
password = 'bla2'


def broadcast():
    msg = b'Send your username'
    dest = ('255.255.255.255', 10101)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ssl_socket = ssl.wrap_socket(s)
    ssl_socket.sendto(msg, dest)
    ssl_socket.settimeout(5)
    while 1:
        try:
            (buf, address) = ssl_socket.recvfrom(10104)
            if not buf:
                break
            if buf == b'I coming':
                checking_client(ssl_socket, address)
                break
        except ssl.socket_error:
            break
    start_broadcast_server()


def start_broadcast_server(port=10101):
    while 1:
        try:
            host = ''
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            ssl_socket = ssl.wrap_socket(s)
            ssl_socket.bind((host, port))
            while 1:
                message, address = ssl_socket.recvfrom(10104)
                if not message:
                    ssl_socket.close()
                    break
                if message == b'Send your username':
                    ssl_socket.sendto(b'I coming', address)
                    checking_server(ssl_socket, address)
        except:
            ssl_socket.close()
            continue


def checking_client(sock, address):
    cipher = ef.get_cipher(password)
    sock.sendto(username.encode(), address)
    #print('i send ' + str(username))
    answer = sock.recvfrom(100)
    if answer == b'OK':
        ran_str = ef.random_string()
        sock.sendto(ran_str.encode(), address)
        value = sock.recvfrom(1024)
        if cipher.decrypt(value) == ran_str:
            sock.sendto(b'OK', addr=address)
            generation = int(sock.recvfrom(1024))
            switch_data(sock, address, generation)


def checking_server(sock, address):
    cipher = ef.get_cipher(password)
    user = sock.recvfrom(1000)
    if user == username:
        sock.sendto(b'OK', address)
        plain_text = sock.recvfrom()
        sol = cipher.encrypt(plain_text)
        sock.sendto(sol.enconde(), address)
        sock.timeout(2)
        conf = sock.recvfrom(1024)
        if conf == b'OK':
            receiver(sock, address)
            generation = int(sock.recvfrom(1024))
            sock.connectto(address)
            ip = sock.getsockname()[0]
            sender(sock, address, generation)


def switch_data(sock, address, generation):
    sock.connectto(address)
    ip = sock.getsockname()[0]
    sender(sock, address, generation)
    receiver(sock, address)


def receiver(sock, address):
    session = data_layer.get_session(data_layer.get_engine())
    gen = session.query(data_layer.Metadata).get(data_layer.Metadata.ip_address == str(address[0]))
    sock.sendto(gen.generation, address)
    while 1:
        data = sock.recvfrom(1024)
        if data == b'finish':
            break
            #ver que llega a data
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