__author__ = 'roly'

import sys
import subprocess
import json
import socket
import multiprocessing


def execute_server():
    subprocess.call(['python3', 'server_JF.py'])


if __name__ == '__main__':
    args = sys.argv[1:]
    # if os.path.exists('./temp/test'):
    # os.remove('./tmp/test')
    s = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
    if 'create' in args or 'start' in args:
        t = multiprocessing.Process(target=execute_server)
        t.start()
        s.connect('./tmp/test')
        j = json.dumps({'action': 'create', 'username': 'r', 'password': 'r'})
        s.send(j.encode())
    if 'query' in args:
        s.connect('./tmp/test')
        words = args[1:]
        j = json.dumps({'action': 'query', 'query': words})
        s.send(j.encode())
        value = None
        value = s.recv(2048)
        _dict = json.loads(value)
        for x in _dict['result']:
            print(x)
