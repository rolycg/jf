__author__ = 'roly'

import sys
import subprocess
import json
import time
import socket

if __name__ == '__main__':
    s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
    s.connect('./tmp/test')

    args = sys.argv[1:]
    if 'create' in args or 'start' in args:
        subprocess.call('python3 server_pipe.py')
        j = json.dumps({'action': 'create', 'username': 'r', 'password': 'r'})
        s.send(j.encode())
    if 'query':
        words = args[2:]
        j = json.dumps({'action': 'query', 'query': words})
        s.send(j.encode())
        value = None
        value = s.recv(2048)
        _dict = json.loads(value)
        for x in _dict['result']:
            print(x)
