import os
import time
from threading import Semaphore

from watchdog import observers
from watchdog.events import FileSystemEventHandler

import data_layer
import extra_functions


semaphore = Semaphore()
cache = []


class MyFileSystemWatcher(FileSystemEventHandler):
    def __init__(self, data_obj):
        self.data_obj = data_obj
        super(FileSystemEventHandler).__init__()

    def on_created(self, event):
        generation = self.data_obj.get_max_generation() + 1
        if hasattr(event, 'dest_path'):
            path = extra_functions.split_paths(event.src_path)
        else:
            path = extra_functions.split_paths(event.src_path)
        if event.is_directory:
            with semaphore:
                cache.append(('created', path[len(path) - 1], 'Folder', path[len(path) - 2], generation,
                              self.data_obj.get_uuid_from_peer(), os.path.join(*path[:len(path) - 1])))

                # self.data_obj.insert_data(path[len(path) - 1], 'Folder', path[len(path) - 2], generation,
                # peer=self.data_obj.get_uuid_from_peer())
                # extra_functions.copy_data(1, (0, path[len(path) - 1], 'Folder', path[len(path) - 2]),)
                # self.cache.append((0, path[len(path) - 1], 'Folder', path[len(path) - 2]))
        else:
            _type = path[len(path) - 1].split('.')
            if len(_type) > 1:
                _type = _type[len(_type) - 1]
            else:
                _type = ''
            with semaphore:
                cache.append(('created', path[len(path) - 1], _type, path[len(path) - 2],
                              generation, self.data_obj.get_uuid_from_peer(), os.path.join(*path[:len(path) - 1])))
                # self.data_obj.insert_data(path[len(path) - 1], _type, path[len(path) - 2],
                # generation, peer=self.data_obj.get_uuid_from_peer())
                # extra_functions.wite_data_in_disk(self.f, (0, path[len(path) - 1], _type, path[len(path) - 2]))
                # self.cache.append((0, path[len(path) - 1], _type, path[len(path) - 2]))
                # self.data_obj.database.commit()

    def on_deleted(self, event):
        path = extra_functions.split_paths(event.src_path)
        with semaphore:
            cache.append(('deleted', path[len(path) - 1], os.path.join(*path[:len(path) - 1])))
            # self.data_obj.delete_data(path[len(path) - 1])

    def on_moved(self, event):
        self.on_deleted(event)
        self.on_created(event)

    def dispatch(self, event):
        if event.event_type == 'created':
            self.on_created(event)
        elif event.event_type == 'deleted':
            self.on_deleted(event)
        elif event.event_type == 'moved':
            self.on_moved(event)
        else:
            print(event.event_type)


# def handle_linux_events(x):
# if x.mask == 256:
# print('file was created')
# if x.mask == 512:
# print('file was deleted')
# if x.mask == 1073742080:
# print('folder was created')
# if x.mask == 1073742336:
# print('folder was deleted')
# if x.mask == 64 or x.mask == 1073741888:
# print('file or folder was moved from here')
# if x.mask == 128 or x.mask == 1073741952:
# print(x.pathname + 'file or folder was moved to here')


# def add_linux_watch(path):
# watch = WatchManager()
# t = ThreadedNotifier(watch)
# t.start()
# watch.add_watch(path, ALL_EVENTS, lambda x: handle_linux_events(x), True, True, quiet=True)


def add_multi_platform_watch(path):
    data_obj = data_layer.DataLayer('database.db')
    watch = observers.Observer()
    obj = MyFileSystemWatcher(data_obj)
    watch.schedule(obj, path, recursive=True)
    watch.start()
    while 1:
        time.sleep(3)
        with semaphore:
            for x in cache:
                if x[0] == 'created':
                    data_obj.insert_data(x[1], x[2], x[3], x[4], x[5], real_path=x[6])
                else:
                    data_obj.delete_data(x[1], x[2])
            cache.clear()
            data_obj.database.commit()


