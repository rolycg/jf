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


def sign_in(s):
    logged = s.recv(100)
    logged = logged.decode()
    logged = json.loads(logged)
    if logged['logged']:
        return s
    password = getpass.getpass()
    sha = hashlib.md5(password.encode()).hexdigest()
    j = json.dumps({'action': 'login', 'password': sha})
    s.send(j.encode())
    d = s.recv(2048)
    d = json.loads(d.decode())
    try:
        message = d['login']
        if not message:
            print('Wrong password.')
            s.close()
            return None
        else:
            s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
            s.connect('/tmp/JF_' + login)
            return s
    except KeyError:
        print(error)


def start_server(s):
    subprocess.Popen(cmd)
    time.sleep(0.8)
    try:
        s.connect('/tmp/JF_' + login)
        # return sign_in(s)
    except FileNotFoundError:
        print(error)
    except ConnectionRefusedError:
        print(error)
    return s


def connect_server(s):
    try:
        s.settimeout(1)
        s.connect('/tmp/JF_' + login)
        return s
        # return sign_in(s)
    except FileNotFoundError:
        return start_server(s)
    except ConnectionRefusedError:
        return start_server(s)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='JF: desktop finder for local networks', prog=sys.argv[0])
    parser.add_argument('query', metavar='q', type=str, help="Execute a query with arguments values", nargs='*')
    parse = parser.add_mutually_exclusive_group()
    parse.add_argument('-c', '--create', help='Create a index from given address', nargs=1, type=str)
    parse.add_argument('-m', '--more', help='Show more results', nargs='?', default='5')
    parse.add_argument('-i', '--index', help='Add a device', nargs='+')
    arg = parser.parse_args()
    prog = sys.argv[0]
    s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
    s = connect_server(s)
    if s:
        if arg.query:
            words = ''
            for word in arg.query:
                words += word + ' '
            j = json.dumps({'action': 'query', 'query': words})
            s.send(j.encode())
            value = ''
            s.settimeout(3)
            while 1:
                try:
                    tmp = s.recv(1000)
                    s.settimeout(0.2)
                    tmp = tmp.decode()
                    if not tmp:
                        break
                    value += tmp
                except socket.timeout:
                    break
            _dict = json.loads(value, encoding='latin-1')
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
            value = s.recv(1024)
            value = json.loads(value.decode())
            if value['result'] == 'Not path':
                print('Wrong path, try another')
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
            value = ''
            s.settimeout(2)
            try:
                while 1:
                    try:
                        tmp = s.recv(1000)
                        s.settimeout(0.2)
                        tmp = tmp.decode()
                        if not tmp:
                            break
                        value += tmp
                    except socket.timeout:
                        break
                _dict = json.loads(value, encoding='latin-1')
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
