from pyinotify import WatchManager, ALL_EVENTS, ThreadedNotifier
from watchdog import observers
from watchdog.events import FileSystemEventHandler
import data_layer


class MyFileSystemWatcher (FileSystemEventHandler):
    def __int__(self):
        super(FileSystemEventHandler).__init__()

    def on_created(self, event):
        engine = data_layer.connect_database()
        if event.dest_path:
            path = str(event.dest_path).split('/')
        else:
            path = str(event.src_path).split('/')
        if event.is_directory:
            data_layer.insert_data(engine, path[len(path) - 1], 'Folder', path[len(path) - 2])
        else:
            _type = path[len(path) - 1].split('.')
            if len(_type) > 1:
                _type = _type[len(_type) - 1]
            else:
                _type = ''
            data_layer.insert_data(engine, path[len(path) - 1], _type, path[len(path) - 2])

    def on_deleted(self, event):
        engine = data_layer.connect_database()
        path = str(event.src_path).split('/')
        data_layer.delete_data(engine, path[len(path) - 1])

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


def handle_linux_events(x):
    if x.mask == 256:
        print('file was created')
    if x.mask == 512:
        print('file was deleted')
    if x.mask == 1073742080:
        print('folder was created')
    if x.mask == 1073742336:
        print('folder was deleted')
    if x.mask == 64 or x.mask == 1073741888:
        print('file or folder was moved from here')
    if x.mask == 128 or x.mask == 1073741952:
        print(x.pathname + 'file or folder was moved to here')
    print('HOla')


def add_linux_watch(path):
    watch = WatchManager()
    t = ThreadedNotifier(watch)
    t.start()
    watch.add_watch(path, ALL_EVENTS, lambda x: handle_linux_events(x), True, True, quiet=True)


def add_multi_platform_watch(path):
    watch = observers.Observer()
    watch.schedule(MyFileSystemWatcher(), path, recursive=True)
    watch.start()
