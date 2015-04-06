__author__ = 'roly'

import sys
import subprocess
import os
import json
import time

if __name__ == '__main__':
    if not os.path.exists('./temp/read_server'):
        os.mkfifo('./temp/read_server')
    if not os.path.exists('./temp/write_server'):
        os.mkfifo('./temp/write_server')
    f = os.fdopen(os.open('./temp/write_server', os.O_NONBLOCK))
    fw = open('./temp/read_server', 'w')
    args = sys.argv[1:]
    if 'create' in args or 'start' in args:
        subprocess.call('python3 server_pipe.py')
        fw.write(json.dumps({'action': 'create', 'username': 'r', 'password': 'r'}))
    if 'query':
        words = args[2:]
        fw.write(json.dumps({'action': 'query', 'query': words}))
        value = None
        while 1:
            value = f.readlines()
            if value:
                break
            time.sleep(0.5)
        _dict = json.loads(value)
        for x in _dict['result']:
            print(x)
