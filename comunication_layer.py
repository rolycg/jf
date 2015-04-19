import socket
import random
import re
import time

from data_layer import semaphore as sem
import data_layer
import extra_functions as ef


query = False


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
            r = random.uniform(1, 5)
            if r == 3:
                break
            continue
        except socket.error:
            s.close()
            continue


def start():
    while 1:
        data_obj = data_layer.DataLayer('database.db')
        broadcast(data_obj)
        start_broadcast_server(data_obj=data_obj)


def set_query(value):
    global query
    query = value


def checking_client(sock, address, data_obj):
    password = data_obj.get_password()
    cipher = ef.get_cipher(password)
    ran_str = ef.random_string()
    sol = cipher.encrypt(ran_str)
    sock.settimeout(2)
    sock.sendto(sol, address)
    value, _ = sock.recvfrom(1000)
    sock.settimeout(15)
    if value.decode() == ran_str:
        sock.sendto(b'OK', address)
        machine = data_obj.get_id_from_peer()
        sock.sendto(str(machine).encode(), address)
        generation, _ = sock.recvfrom(1024)
        sender(sock, address, int(generation), data_obj)


def checking_server(sock, address, data_obj):
    password = data_obj.get_password()
    cipher = ef.get_cipher(password)
    plain_text, _ = sock.recvfrom(1000)
    value = cipher.decrypt(plain_text)
    sock.sendto(value, address)
    conf, _ = sock.recvfrom(1024)
    if conf == b'OK':
        uuid, _ = sock.recvfrom(1024)
        last_generation = data_obj.get_last_generation(uuid.decode())
        if last_generation:
            sock.sendto(str(last_generation).encode(), address)
        else:
            data_obj.insert_peer(uuid, socket.gethostbyname(address[0]))
            sock.sendto(str(-1).encode(), address)
        receiver(sock, address, uuid.decode(), data_obj)


def receiver(sock, address, uuid, data_obj):
    global query
    password = data_obj.get_password()
    cipher = ef.get_cipher(password)
    with sem:
        while 1:
            data, _ = sock.recvfrom(10024)
            if data == b'finish':
                break
            else:
                value = cipher.decrypt(data)
                try:
                    elements = re.split('\\?+', value.decode())
                except UnicodeDecodeError:
                    elements = re.split('\\?+', value.decode(encoding='LATIN-1'))
                ###
                # DONE: Fix concurrency between writers
                ###
                if not data_obj:
                    data_obj = data_layer.DataLayer('database.db')
                elements[0] = elements[0][1:]
                elements[len(elements) - 1] = ef.unpad(elements[len(elements) - 1])
                elements = [x.strip() for x in elements]
                elements[len(elements) - 1] = data_obj.get_id_from_uuid(elements[len(elements) - 1])
                if elements[4] == '-1':
                    data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[2],
                                         file_type=elements[3], generation=elements[5], peer=elements[6],
                                         first=True, date=elements[len(elements) - 1])
                else:
                    data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[4],
                                         file_type=elements[3], generation=elements[5], peer=elements[6],
                                         first=False, date=elements[len(elements) - 1])

                if query:
                    data_obj.database.commit()
                    data_obj.close()
                    data_obj = None

                    while query:
                        time.sleep(0.5)
        data_obj.database.commit()
    gen, _ = sock.recvfrom(1024)
    if gen.decode():
        data_obj.edit_generation(uuid, gen.decode())
    with sem:
        while 1:
            data, _ = sock.recvfrom(10024)
            if data == b'finish':
                break
            else:
                value = cipher.decrypt(data)
                try:
                    elements = re.split('\\?+', value.decode())
                except UnicodeDecodeError:
                    elements = re.split('\\?+', value.decode(encoding='LATIN-1'))
                if not data_obj:
                    data_obj = data_layer.DataLayer('database.db')
                elements[0] = elements[0][1:]
                elements[len(elements) - 1] = ef.unpad(elements[len(elements) - 1])
                elements = [x.strip() for x in elements]
                # elements[len(elements) - 1] = data_obj.get_id_from_uuid(elements[len(elements) - 1])
                # if elements[4] == '-1':
                # data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[2],
                # file_type=elements[3], generation=elements[5], peer=elements[6],
                #                          first=True, date=elements[len(elements) - 1])
                # else:
                #     data_obj.insert_data(id=elements[0], file_name=elements[1], parent=elements[4],
                #                          file_type=elements[3], generation=elements[5], peer=elements[6],
                #                          first=False, date=elements[len(elements) - 1])
                if elements[0] == 'deleted':
                    data_obj.delete_data(elements[1], elements[2], data_obj.get_id_from_uuid(uuid))
                elif elements[0] == 'updated':
                    data_obj.update_data(elements[1:], data_obj.get_id_from_uuid(uuid))
                if query:
                    data_obj.database.commit()
                    data_obj.close()
                    data_obj = None
                    while query:
                        time.sleep(0.5)
        data_obj.database.commit()


def sender(sock, address, generation, data_obj):
    password = data_obj.get_password()
    query = data_obj.get_files(generation, data_obj.get_uuid_from_peer())
    _max = -1
    cipher = ef.get_cipher(password)
    cont = 0
    for x in query:
        tmp = data_obj.get_peer_from_id(x[len(x) - 2])
        x = (x[0], x[1], x[2], x[3], x[4], x[5], x[6], tmp, x[len(x) - 1])
        send = cipher.encrypt(ef.convert_to_str(x))
        sock.sendto(send, address)
        cont += 1
        _max = max(_max, x[6])
    sock.sendto(b'finish', address)
    if _max == -1:
        sock.sendto(''.encode(), address)
    else:
        sock.sendto(str(_max).encode(), address)
    uuid, _ = sock.recvfrom(10024)
    if _max > -1:
        data_obj.edit_my_generation(uuid, _max)
    _id = data_obj.get_id_from_uuid(uuid=uuid.decode())
    query2 = data_obj.get_action_from_machine(_id)
    for y in query2:
        send = cipher.encrypt(ef.convert_to_str(y))
        sock.sendto(send, address)
    sock.sendto(b'finish', address)
    data_obj.delete_actions_from_machine(_id)
