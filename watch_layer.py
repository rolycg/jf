from pyinotify import WatchManager, ALL_EVENTS, ThreadedNotifier


def handle_events(x):
    if x.mask == 256:
        print('file was created')
    if x.mask == 512:
        print('file was deleted')
    if x.mask == 1073742080:
        print('folder was created')
    if x.mask == 1073742336:
        print('folder was deleted')
    if x.mask == 64 or x.mask == 1073741888:
        print('file was moved from here')
    if x.mask == 128 or x.mask == 1073741952:
        print(x.pathname + 'file was moved to here')


def add_linux_watch(path):
    watch = WatchManager()
    watch.add_watch(path, ALL_EVENTS, lambda x: handle_events(x), True, True, quiet=True)
    t = ThreadedNotifier(watch)
    t.run()
