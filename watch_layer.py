from pyinotify import WatchManager, ALL_EVENTS, ThreadedNotifier
from watchdog import observers
from watchdog.events import FileCreatedEvent, DirCreatedEvent, DirModifiedEvent, DirDeletedEvent, FileDeletedEvent, \
    FileMovedEvent, FileSystemEventHandler


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


class test (FileSystemEventHandler):
    def __int__(self):
        super(FileSystemEventHandler).__init__()
    def on_created(self, event):
        print('se uso on created')
    def on_deleted(self, event):
        print('se uso on deleted')
    def on_moved(self, event):
        print('se uso on moved')
    def dispatch(self, event):
        if event.event_type == 'created':
            self.on_created(event)
        elif event.event_type == 'deleted':
            self.on_deleted(event)
        elif event.event_type == 'moved':
            self.on_moved(event)
        else:
            print(event.event_type)

def add_windows_watch(path):
    watch = observers.Observer()
    watch.schedule(test(), path, recursive=True)
    watch.start()
