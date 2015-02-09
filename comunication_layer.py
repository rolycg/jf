import socket
import random
import re

import extra_functions as ef


def broadcast(data_obj):
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
                    checking_client(s, address, data_obj)
                    break
            except socket.error:
                break
            except socket.timeout:
                break
    except OSError:
        pass


def start_broadcast_server(data_obj, port=10101):
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
                    checking_server(s, address, data_obj)
        except socket.timeout:
            r = random.uniform(1, 8)
            if r == 3:
                break
            continue
        except socket.error:
            s.close()
            continue


def start(data_obj_param):
    while 1:
        # data_obj = data_layer.DataLayer('database.db')
        data_obj = data_obj_param
        broadcast(data_obj)
        start_broadcast_server(data_obj=data_obj)


def checking_client(sock, address, data_obj):
    username, password = data_obj.get_username_password()
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
            machine = data_obj.get_uuid_from_peer()
            sock.sendto(str(machine).encode(), address)
            generation, _ = sock.recvfrom(1024)
            sender(sock, address, int(generation), data_obj)


def checking_server(sock, address, data_obj):
    username, password = data_obj.get_username_password()
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
            receiver(sock, address, uuid, data_obj)


def receiver(sock, address, uuid, data_obj):
    _, password = data_obj.get_username_password()
    # gen = session.query(data_layer_old.Metadata).filter(data_layer_old.Metadata._uuid == uuid)
    last_generation = data_obj.get_last_generation(uuid)
    if last_generation:
        sock.sendto(str(last_generation).encode(), address)
    else:
        data_obj.insert_peer(uuid, socket.gethostbyname(address[0]))
        sock.sendto(str(-1).encode(), address)
    cipher = ef.get_cipher(password)
    while 1:
        data, _ = sock.recvfrom(10024)
        if data == b'finish':
            break
        else:
            value = cipher.decrypt(data)
            elements = re.split('\\?+', value.decode())
            elements[0] = elements[0][1:]
            elements[len(elements) - 1] = ef.unpad(elements[len(elements) - 1])
            elements = [x.strip() for x in elements]

            if elements[4] == '-1':
                data_obj.insert_data(elements[1], elements[3], elements[2], elements[5], elements[6], True)
            else:
                data_obj.insert_data(elements[1], elements[3], elements[4], elements[5], elements[6], False)
    data_obj.database.commit()
    gen, _ = sock.recvfrom(1024)
    data_obj.edit_generation(uuid, gen.decode())
    # session.query(data_layer_old.Metadata).filter(data_layer_old.Metadata._uuid == uuid).update(
    # {'last_generation': int(gen)})


def sender(sock, address, generation, data_obj):
    _, password = data_obj.get_username_password()
    query = data_obj.get_files(generation, data_obj.get_uuid_from_peer())
    # session.query(data_layer_old.File).filter(data_layer_old.File.generation > generation)
    _max = -1
    cipher = ef.get_cipher(password)
    cont = 0
    for x in query:
        send = cipher.encrypt(ef.convert_to_str(x))
        sock.sendto(send, address)
        cont += 1
        _max = max(_max, x[5])
    sock.sendto(b'finish', address)
    sock.sendto(str(_max).encode(), address)
