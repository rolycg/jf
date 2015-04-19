__author__ = 'roly'

import os

count = 0


def generate_file_system(path, depth, count_files):
    global count
    paths = []
    if not depth:
        return
    for x in range(0, 10):
        os.mkdir(path + os.sep + str(count_files))
        paths.append(path + os.sep + str(count_files))
        count_files -= 1
        count += 1
    for x in paths:
        for y in range(50):
            try:
                f = open(x + os.sep + str(count_files) + '.txt', 'w')
                f.close()
                count += 1
            except OSError:
                continue
            count_files -= 1
    for x in paths:
        generate_file_system(x, depth - 1, count_files)


if __name__ == '__main__':
    count = 0
    generate_file_system('/home/roly/file_system', 3, 100000)
    generate_file_system('/home/roly/file_system', 3, 1000000)
    print(count)
