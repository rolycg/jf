import socket
import ssl
import hashlib as hashl

username = 'bla'
password = 'bla2'


def broadcast():
    msg = b'Send your username'
    dest = ('255.255.255.255', 10101)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ssl_socket = ssl.wrap_socket(s)
    ssl_socket.sendto(msg, dest)
    ssl_socket.settimeout(10)
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
    print(str(address))
    sock.sendto(username.encode() + '!!__'.encode() + str(hashl.sha1(password.encode()).hexdigest()).encode(), address)
    print('i send ' + str(username))
    answer = sock.recv(100)
    if answer == b'OK':
        switch_data(sock, address)


def checking_server(sock, address):
    user, passw = sock.recvfrom(1000)
    if user == username and hashl.sha1(password).hexdigest() == passw:
        sock.sendto(b'OK', address)
        switch_data(sock, address)
    sock.sendto(b'NOT', address)


def switch_data(sock, address):
    print('i am in switch data')