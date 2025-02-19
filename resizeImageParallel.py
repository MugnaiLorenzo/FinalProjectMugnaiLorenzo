import os
import numpy as np
from PIL import Image
import multiprocessing
from functools import partial


def iniziatlitation(file_name, matrix, pool_size, vectorized=False):
    img = Image.open(file_name).convert("RGB")
    img_array = np.array(img, dtype=np.float32)
    w, h = img_array.shape[:2]
    img_t = np.zeros_like(img_array)
    kernel_size = matrix.shape[0]
    pad_size = (kernel_size - 1) // 2
    img_padded = np.pad(img_array, ((pad_size, pad_size), (pad_size, pad_size), (0, 0)), mode='constant',
                        constant_values=0)
    pool = multiprocessing.Pool(processes=pool_size)
    chunk_size = w // pool_size
    chunks = [
        (img_padded[i * chunk_size:(i + 1) * chunk_size + 2 * pad_size], matrix)
        for i in range(pool_size)
    ]
    worker_func = worker_vectorized if vectorized else worker_non_vectorized
    results = pool.map(worker_func, chunks)
    img_t = np.vstack(results)
    pool.close()
    pool.join()
    return Image.fromarray(np.clip(img_t, 0, 255).astype(np.uint8))


def worker_non_vectorized(args):
    img_chunk, matrix = args
    h, w, _ = img_chunk.shape
    s = (matrix.shape[0] - 1) // 2
    result = np.zeros((h - 2 * s, w - 2 * s, 3))
    for x in range(s, h - s):
        for y in range(s, w - s):
            pixel_value = np.zeros(3)
            for i in range(-s, s + 1):
                for j in range(-s, s + 1):
                    pixel_value += img_chunk[x + i, y + j] * matrix[s + i, s + j]
            result[x - s, y - s] = np.clip(pixel_value, 0, 255)

    return result.astype(np.uint8)


def worker_vectorized(args):
    img_chunk, matrix = args
    h, w, _ = img_chunk.shape
    k_size = matrix.shape[0]
    s = k_size // 2
    result = np.zeros((h - 2 * s, w - 2 * s, 3))
    for i in range(3):
        for y in range(k_size):
            for x in range(k_size):
                result[:, :, i] += img_chunk[y:y + h - 2 * s, x:x + w - 2 * s, i] * matrix[y, x]

    return np.clip(result, 0, 255).astype(np.uint8)
