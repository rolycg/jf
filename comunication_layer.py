import socket
import ssl


def broadcast():
    import socket

    msg = b'Send your username'
    dest = ('255.255.255.255', 10100)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ssl_socket = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED)
    ssl_socket.sendto(msg, dest)
    ssl_socket.settimeout(10)
    while 1:
        try:
            (buf, address) = ssl_socket.recvfrom(10100)
            if not buf:
                break
        except ssl_socket.timeout:
            break


def start_broadcast_server(port=10100):
    while 1:
        try:
            host = ''
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.bind((host, port))
            while 1:
                message, address = s.recvfrom(10104)
                if not message:
                    s.close()
                    break
                if message == b'Send your username':
                    s.sendto(b'I coming', address)
        except:
            s.close()
            continue