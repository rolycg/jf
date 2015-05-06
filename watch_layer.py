import os
import time
from queue import Queue, Empty

from data_layer import semaphore as sem
from watchdog import observers
from watchdog.events import FileSystemEventHandler
import data_layer
import extra_functions


query = False

cache = Queue()


def set_query(value):
    global query
    query = value


class MyFileSystemWatcher(FileSystemEventHandler):
    def __init__(self, cache):
        self.cache = cache
        super(FileSystemEventHandler).__init__()

    def on_created(self, event):
        if hasattr(event, 'dest_path'):
            path = extra_functions.split_paths(event.dest_path)
        else:
            path = extra_functions.split_paths(event.src_path)
        if event.is_directory:
            self.cache.put(('created', path[len(path) - 1], 'Folder', path[len(path) - 2], None,
                            None, os.path.join(*path[:len(path) - 1])))

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
            self.cache.put(('created', path[len(path) - 1], _type, path[len(path) - 2],
                            None, None, os.path.join(*path[:len(path) - 1])))
            # self.data_obj.insert_data(path[len(path) - 1], _type, path[len(path) - 2],
            # generation, peer=self.data_obj.get_uuid_from_peer())
            # extra_functions.wite_data_in_disk(self.f, (0, path[len(path) - 1], _type, path[len(path) - 2]))
            # self.cache.append((0, path[len(path) - 1], _type, path[len(path) - 2]))
            # self.data_obj.database.commit()

    def on_deleted(self, event):
        path = extra_functions.split_paths(event.src_path)
        self.cache.put(('deleted', path[len(path) - 1], os.path.join(*path[:len(path) - 1])))
        # self.data_obj.delete_data(path[len(path) - 1])

    def on_updated(self, event):
        old_path = extra_functions.split_paths(event.src_path)
        path = extra_functions.split_paths(event.dest_path)
        self.cache.put(('updated', path[len(path) - 1], 'Folder', path[len(path) - 2], None,
                        None, os.path.join(*path[:len(path) - 1]), old_path[len(old_path) - 1],
                        os.path.join(*old_path[:len(old_path) - 1])))

    def on_moved(self, event):
        if event.is_directory:
            self.on_updated(event)
        else:
            self.on_deleted(event)
            self.on_created(event)

    def dispatch(self, event):
        if event.event_type == 'created':
            self.on_created(event)
        elif event.event_type == 'deleted':
            self.on_deleted(event)
        elif event.event_type == 'moved':
            self.on_moved(event)
        elif event.event_type == 'modified':
            pass
        else:
            print(event.event_type)


def create_watcher(paths, cache):
    watchers = []
    obj = MyFileSystemWatcher(cache)
    for path in paths:
        watchers.append((observers.Observer(), path))
    for x in range(0, len(watchers)):
        watchers[x][0].schedule(obj, watchers[x][1], recursive=True)
        watchers[x][0].start()
    return watchers


def make_watch(cache, machine=1):
    global query
    data_obj = data_layer.DataLayer('database.db')
    while 1:
        time.sleep(2)
        if not cache.empty():
            with sem:
                number = data_obj.get_max_id(machine)
                generation = data_obj.get_max_generation() + 1
                while 1:
                    try:
                        x = cache.get(timeout=0.5)
                        if not data_obj:
                            data_obj = data_layer.DataLayer('database.db')
                        number += 1
                        if x[0] == 'created':
                            data_obj.insert_data(number, x[1], x[2], x[3], generation, machine,
                                                 real_path=x[6])
                        elif x[0] == 'deleted':
                            data_obj.delete_data(x[1], x[2])
                        else:
                            data_obj.update_data(x[1:], machine)
                        if query:
                            data_obj.database.commit()
                            data_obj.close()
                            data_obj = None
                            while query:
                                time.sleep(0.5)
                    except Empty:
                        break
                    data_obj.database.commit()
                    print('Commit Did it')


def add_multi_platform_watch(paths, cache):
    create_watcher(paths, cache)
    make_watch(cache)