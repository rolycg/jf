__author__ = 'roly'

import time
from threading import Thread
from queue import Queue
import os
import socket
import json
import uuid
import pwd

import dbus
from gi.overrides.GLib import MainLoop
from dbus.mainloop.glib import DBusGMainLoop

import data_layer as data_layer_py
from main import save_to_disk
from main import dfs
import extra_functions
import watch_layer

collection = None
messages = []
login = pwd.getpwuid(os.getuid())[0]

###
# TODO: Make the concurrency test
###

def _add_device_(path, device_name, device_id):
    global collection
    with data_layer_py.semaphore:
        data_layer = data_layer_py.DataLayer()
        data_layer.insert_peer(uuid=device_id, pc_name=device_name, memory=1)
        peer = data_layer.get_id_from_uuid(device_id)
        data_layer.insert_data(id=1, file_name='', file_type='Folder', parent=path, generation=0, first=True,
                               peer=peer)
        data_layer.database.commit()
        _queue = Queue()
        t = Thread(target=dfs, args=(path, _queue))
        t.start()
        t2 = Thread(target=save_to_disk, args=(data_layer, _queue, peer))
        t2.start()
        t.join()
        t2.join()
        data_layer.database.close()
    return peer


def add_watch(path, queue):
    return watch_layer.create_watcher([path], queue)[0][0]


def device_added_callback(*args):
    global collection
    try:
        values = args[1]['org.freedesktop.UDisks2.Job']
    except KeyError:
        return
    try:
        operation = values['Operation']
        if operation == 'filesystem-mount':
            block = values['Objects'][0]
            _id, block, name = get_mount_point(block)
            data = data_layer_py.DataLayer()
            exist = data.get_id_from_device(_id)
            data.close()
            if exist:
                execute(exist, block, collection[block], False)
        elif operation == 'filesystem-unmount':
            block = values['Objects'][0]
            try:
                if collection[block][4] and collection[block][4].is_alive():
                    try:
                        collection[block][4]._stop()
                    except Exception:
                        pass
                del collection[block]
            except Exception:
                return
        elif operation == 'cleanup':
            pass
    except KeyError:
        return


def get_mount_point(block):
    global collection
    global messages
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.UDisks2', block)
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')  # Here we use this 'magic' interface
    dbus_mount_point = iface.Get('org.freedesktop.UDisks2.Filesystem', 'MountPoints')
    mount_point = ''
    while not len(dbus_mount_point):
        time.sleep(0.5)
        dbus_mount_point = iface.Get('org.freedesktop.UDisks2.Filesystem', 'MountPoints')
    dbus_id = iface.Get('org.freedesktop.UDisks2.Block', 'Id')
    dbus_name = iface.Get('org.freedesktop.UDisks2.Block', 'IdLabel')
    dbus_space = iface.Get('org.freedesktop.UDisks2.Block', 'Size')
    for letter in dbus_mount_point[0]:
        mount_point += chr(letter)
    if not dbus_name:
        dbus_name = mount_point[:-1].split(os.sep)
        dbus_name = dbus_name[len(dbus_name) - 1]
    if not dbus_id:
        dbus_id = uuid.uuid3(uuid.uuid4(), dbus_name)
    collection[block] = [str(mount_point[:-1]), str(dbus_id), str(dbus_name), None, None]
    messages.append(
        'You have a new device connected (' + dbus_name + ', ' + extra_functions.convert_to_human_readable(
            dbus_space) + '). To have JF track it, execute:' + '\n' + 'jf ' + '-i ' + block)
    return dbus_id, block, dbus_name


def execute(exist, block, device_name, re_index):
    if exist and re_index:
        data = data_layer_py.DataLayer()
        with data_layer_py.semaphore:
            data.delete_drive(exist)
        data.close()
        machine = _add_device_(device_name[0], device_name[2], device_name[1])
        queue = Queue()
        collection[block][3] = add_watch(device_name[0], queue)
        t = Thread(target=watch_layer.make_watch, args=(queue, machine))
        t.start()
        collection[block][4] = t
    if exist:
        queue = Queue()
        collection[block][3] = add_watch(device_name[0], queue)
        t = Thread(target=watch_layer.make_watch, args=(queue, exist))
        t.start()
        collection[block][4] = t
    else:
        queue = Queue()
        machine = _add_device_(device_name[0], device_name[2], device_name[1])
        collection[block][3] = add_watch(device_name[0], queue)
        t = Thread(target=watch_layer.make_watch, args=(queue, machine))
        t.start()
        collection[block][4] = t


def add_device(name, re_index):
    global collection
    device_name = None
    block = None
    for x in collection.keys():
        if name.strip() == x.strip():
            device_name = collection[x]
            block = x
    if device_name:
        if collection[block][4] and collection[block][4].is_alive():
            try:
                collection[block][4]._stop()
            except Exception:
                pass
            collection[block][4] = None
        data = data_layer_py.DataLayer()
        exist = data.get_id_from_device(device_name[1])
        data.close()
        thread = Thread(target=execute, args=(exist, block, device_name, True))
        thread.start()
    return device_name


def _start_observer():
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    # obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
    # iface_properties = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')  # Here we use this 'magic' interface
    # a = iface_properties.Get('org.freedesktop.UDisks2.Drive', 'Size')
    # iface_obj_manager = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
    iface = 'org.freedesktop.DBus.ObjectManager'
    signal = 'InterfacesAdded'
    bus.add_signal_receiver(device_added_callback, signal, iface)

    # start the main loop
    MainLoop().run()


def start_observer():
    global collection
    global messages
    collection = {}
    t = Thread(target=_start_observer)
    t.start()
    if os.path.exists('/tmp/JF_ext_dv_' + login):
        os.remove('/tmp/JF_ext_dv_' + login)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind('/tmp/JF_ext_dv_' + login)
    s.listen(1)
    while 1:
        conn, _ = s.accept()
        data = conn.recv(2048)
        _dict = json.loads(data.decode(), encoding='utf-8')
        try:
            tmp = _dict['messages']
            conn.send(json.dumps({'messages': messages}).encode())
            messages = []
        except KeyError:
            continue


if __name__ == '__main__':
    start_observer()
    if os.path.exists('/tmp/FJ_ext_dv'):
        os.remove('/tmp/FJ_ext_dv')
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind('/tmp/FJ_ext_dv')
    s.listen(1)
    while 1:
        conn, _ = s.accept()
        data = conn.recv(2048)
        _dict = json.loads(data.decode(), encoding='utf-8')
        try:
            tmp = _dict['messages']
            conn.send(json.dumps({'messages': messages}).encode())
            messages = []
        except KeyError:
            continue
