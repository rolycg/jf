__author__ = 'roly'

import sys
import json
import socket
import time
import subprocess
import getpass

cmd = ['python3', 'server_JF.py']

if __name__ == '__main__':
    args = sys.argv[1:]
    # if os.path.exists('./temp/test'):
    # os.remove('./tmp/test')
    s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
    if 'create' == args[0].lower() or 'start' == args[0].lower():
        subprocess.Popen(cmd)
        time.sleep(0.5)
        s.connect('/tmp/JF')
        print('Username: ')
        username = input()
        password = getpass.getpass()
        j = json.dumps({'action': args[0], 'username': username, 'password': password})
        s.send(j.encode())
        if 'start' == args[0].lower():
            d = s.recv(2048)
            d = json.loads(d.decode())
            if d['login'] == 'False':
                print('Wrong username or password')
    if 'query' == args[0].lower():
        s.connect('/tmp/JF')
        words = ''
        for word in args[1:]:
            words += word + ' '
        j = json.dumps({'action': 'query', 'query': words})
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
    if 'more' == args[0].lower():
        s.connect('/tmp/JF')
        j = json.dumps({'action': 'more'})
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
    if 'index' == args[0].lower():
        s.connect('/tmp/JF')
        j = json.dumps({'action': 'index', 'device': args[1]})
        s.send(j.encode())
        d = json.loads(s.recv(10000).decode())
        if not d['results'] == 'OK':
            print(d['results'])

