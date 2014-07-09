import socket
import ssl
import hashlib as hashl

username = 'bla'
password = 'bla2'


def broadcast():
    msg = b'Send your username'
    dest = ('255.255.255.255', 10100)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ssl_socket = ssl.wrap_socket(s)
    ssl_socket.sendto(msg, dest)
    while 1:
        try:
            (buf, address) = ssl_socket.recvfrom(10104)
            if not buf:
                break
            if buf == b'I coming':
                checking_client(ssl_socket, address, 10101)
                break
        except ssl_socket.timeout:
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
                    checking_server(ssl_socket, address, 10101)
        except:
            ssl_socket.close()
            continue


def checking_client(sock, address, port):
    sock.bind((address, port))
    sock.send((username, hashl.sha1(password).hexdigest()))
    answer = sock.recv(100)
    if answer == b'OK':
        switch_data(sock, address, port)


def checking_server(sock, address, port):
    sock.bind((address, port))
    user, passw = sock.recv(1000)
    if user == username and hashl.sha1(password).hexdigest() == passw:
        sock.send(b'OK')
        switch_data(sock, address, port)
    sock.send(b'NOT')


def switch_data(sock, address, port):
    pass