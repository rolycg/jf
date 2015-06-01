__author__ = 'roly'

import sys
import time
import subprocess
import os
import pwd
import argparse
import socket
import json
import getpass
import hashlib

error = 'Something went wrong, call emergency'
cmd = ['python3', 'server_JF.py']
login = pwd.getpwuid(os.getuid())[0]
database_path = './database.db'


def start_server(s):
    subprocess.Popen(cmd)
    time.sleep(0.8)
    try:
        s.connect('/tmp/JF_' + login)
        if os.path.exists(database_path):
            password = getpass.getpass()
            sha = hashlib.md5(password.encode()).hexdigest()
            j = json.dumps({'action': 'login', 'password': sha})
            s.send(j.encode())
            d = s.recv(2048)
            d = json.loads(d.decode())
            try:
                message = d['login']
                if not message:
                    print('Wrong password')
                    s.close()
                else:
                    s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
                    s.connect('/tmp/JF_' + login)
                    return s
            except KeyError:
                print(error)
    except FileNotFoundError:
        print(error)
    except ConnectionRefusedError:
        print(error)
    return s


def connect_server(s):
    try:
        s.settimeout(2)
        s.connect('/tmp/JF_' + login)
    except FileNotFoundError:
        return start_server(s)
    except ConnectionRefusedError:
        return start_server(s)
    return s


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='JF: desktop finder for local networks', prog=sys.argv[0])
    parser.add_argument('query', metavar='q', type=str, help="Execute a query with arguments values", nargs='*')
    parse = parser.add_mutually_exclusive_group()
    parse.add_argument('-c', '--create', help='Create a index from given address', nargs=1, type=str)
    parse.add_argument('-m', '--more', help='Show more results', nargs='?', default='5')
    parse.add_argument('-i', '--index', help='Index a device', nargs='+')
    arg = parser.parse_args()

    s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
    s = connect_server(s)
    if arg.query:
        words = ''
        for word in arg.query:
            words += word + ' '
        j = json.dumps({'action': 'query', 'query': words})
        s.send(j.encode())
        value = None
        s.settimeout(3)
        value = s.recv(15048)
        _dict = json.loads(value.decode(), encoding='latin-1')
        for x in _dict['results']:
            print(x)
        try:
            message = _dict['message']
            print('JF says: ' + message)
        except KeyError:
            pass
        except socket.timeout:
            print("Server not respond")
    elif arg.create:
        password = getpass.getpass()
        sha = hashlib.md5(password.encode())
        j = json.dumps({'action': 'create', 'password': sha.hexdigest(), 'path': arg.create[0]})
        s.send(j.encode())
    elif arg.index:
        name = ''
        for x in arg.index:
            name += x + ' '
        j = json.dumps({'action': 'index', 'device': name, 'index': True})
        s.send(j.encode())
        d = json.loads(s.recv(100).decode())
        if not d['results'] == 'OK':
            print(d['results'])
    elif arg.more:
        j = json.dumps({'action': 'more', 'cant': arg.more})
        s.send(j.encode())
        value = None
        s.settimeout(2)
        try:
            value = s.recv(15048)
            _dict = json.loads(value.decode(), encoding='latin-1')
            for x in _dict['results']:
                print(x)
            try:
                message = _dict['message']
                print('JF says: ' + message)
            except KeyError:
                pass
        except socket.timeout:
            print("Server not respond")
    s.close()
    # args = sys.argv[1:]
    # s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
    # if not len(args):
    #     print('Blank not allowed. Must pass: \ncreate\nstart\nquery <some query>\nindex <some device>\n')
    # elif 'create' == args[0].lower() or 'start' == args[0].lower():
    #     try:
    #         s.connect('/tmp/JF_' + login)
    #     except FileNotFoundError:
    #         s = start_server(s)
    #     except ConnectionRefusedError:
    #         s = start_server(s)
    #     password = getpass.getpass()
    #     j = json.dumps({'action': args[0], 'password': password})
    #     s.send(j.encode())
    #     if 'start' == args[0].lower():
    #         d = s.recv(2048)
    #         d = json.loads(d.decode())
    #         try:
    #             message = d['message']
    #             print(message)
    #         except KeyError:
    #             try:
    #                 if d['login'] == 'False':
    #                     print('Wrong password')
    #             except KeyError:
    #                 print(error)
    #     if 'create' == args[0].lower():
    #         s.settimeout(0.5)
    #         try:
    #             d = s.recv(2048)
    #             d = json.loads(d.decode())
    #             try:
    #                 message = d['message']
    #                 print(message)
    #             except KeyError:
    #                 print('Server Error')
    #             resp = input()
    #             while 1:
    #                 if resp.lower().strip() == 'y' or resp.lower().strip() == 'n':
    #                     break
    #                 else:
    #                     print('(Y/N)')
    #                     resp = input()
    #             s.send(json.dumps({'answer': resp}).encode())
    #         except socket.timeout:
    #             pass
    # elif 'query' == args[0].lower():
    #     try:
    #         s.connect('/tmp/JF_' + login)
    #         words = ''
    #         for word in args[1:]:
    #             words += word + ' '
    #         j = json.dumps({'action': 'query', 'query': words})
    #         s.send(j.encode())
    #         value = None
    #         s.settimeout(2)
    #         try:
    #             value = s.recv(15048)
    #             _dict = json.loads(value.decode(), encoding='latin-1')
    #             for x in _dict['results']:
    #                 print(x)
    #             try:
    #                 message = _dict['message']
    #                 print('JF says: ' + message)
    #             except KeyError:
    #                 pass
    #         except socket.timeout:
    #             print("Server not respond")
    #     except ConnectionRefusedError:
    #         print('You must start server first, execute: jf start')
    # elif 'more' == args[0].lower():
    #     s.connect('/tmp/JF')
    #     j = json.dumps({'action': 'more'})
    #     s.send(j.encode())
    #     value = None
    #     s.settimeout(2)
    #     try:
    #         value = s.recv(15048)
    #         _dict = json.loads(value.decode(), encoding='latin-1')
    #         for x in _dict['results']:
    #             print(x)
    #         try:
    #             message = _dict['message']
    #             print('JF says: ' + message)
    #         except KeyError:
    #             pass
    #     except socket.timeout:
    #         print("Server not respond")
    # elif 'index' == args[0].lower():
    #     s.connect('/tmp/JF')
    #     index = False
    #     if args[len(args) - 1] == '-r':
    #         index = True
    #     name = ''
    #     if index:
    #
    #         for x in args[1:len(args) - 1]:
    #             name += x + ' '
    #         j = json.dumps({'action': 'index', 'device': name, 'index': index})
    #     else:
    #         for x in args[1:]:
    #             name += x + ' '
    #         j = json.dumps({'action': 'index', 'device': name})
    #     s.send(j.encode())
    #     d = json.loads(s.recv(100).decode())
    #     if not d['results'] == 'OK':
    #         print(d['results'])
    # else:
    #     print('Wrong parameter. Must pass: \ncreate\nstart\nquery <some query>\nindex <some device>\n')
