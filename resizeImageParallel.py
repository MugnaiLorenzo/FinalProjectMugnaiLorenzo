import os
import numpy as np
from PIL import Image
import multiprocessing
from functools import partial
from multiprocessing import Value

shared_px: Value


def init(px: Value):
    global shared_px
    shared_px = px


def iniziatlitation(file_name, ext, matrix):
    pool_size = multiprocessing.cpu_count() * 2
    img = Image.open(os.path.join("image", file_name))
    w = img.size[0]
    h = img.size[1]
    img_t = Image.new(mode="RGB", size=(w, h))
    px = img.load()
    px_t = img_t.load()
    pool = multiprocessing.Pool(processes=pool_size, initializer=init, initargs=(px,))
    comb_array = np.array(np.meshgrid([*range(w)], [*range(h)])).T.reshape(-1, 2)
    a = pool.map(partial(worker, matrix=matrix, w=w, h=h), comb_array)
    j = 0
    for c in comb_array:
        px_t[c[0], c[1]] = a[j]
        j = j + 1
    pool.close()
    pool.join()
    img_t.save(os.path.join("imageParallel", file_name.rsplit(".", 1)[0] + ext + "." + file_name.rsplit(".", 1)[1]))


def worker(comb_array, matrix, w, h):
    i = comb_array[0]
    j = comb_array[1]
    x = 0
    y = 0
    z = 0
    s = (np.size(matrix, 0) - 1) / 2
    row = np.arange(-(np.size(matrix, 0) - 1) / 2, (np.size(matrix, 0) - 1) / 2 + 1, 1)
    col = np.arange(-(np.size(matrix, 1) - 1) / 2, (np.size(matrix, 1) - 1) / 2 + 1, 1)
    for r in row:
        for c in col:
            if i + r in range(w - 1) and j + c in range(h - 1):
                x = x + shared_px[int(i + r), int(j + c)][0] * matrix[int(s + r), int(s + c)]
                y = y + shared_px[int(i + r), int(j + c)][1] * matrix[int(s + r), int(s + c)]
                z = z + shared_px[int(i + r), int(j + c)][2] * matrix[int(s + r), int(s + c)]
    return int(x), int(y), int(z)
