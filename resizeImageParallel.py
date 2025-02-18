import os
import numpy as np
from PIL import Image
import multiprocessing
from functools import partial


def iniziatlitation(file_name, matrix, pool_size, vectorized=False):
    """Parallelizza la convoluzione su chunk d'immagine, sia in modo vettorizzato che non."""
    img = Image.open(file_name).convert("RGB")  # Convertiamo a RGB per garantire coerenza
    img_array = np.array(img, dtype=np.float32)  # Convertiamo l'immagine in un array NumPy
    w, h = img_array.shape[:2]  # Otteniamo larghezza e altezza
    img_t = np.zeros_like(img_array)  # Creiamo un array vuoto per l'output

    # Determiniamo la dimensione del kernel
    kernel_size = matrix.shape[0]

    # Calcoliamo il padding necessario in base al numero di thread
    pad_size = kernel_size // pool_size  # Aumentiamo il padding in base ai thread

    # Aggiungiamo padding attorno all'immagine
    img_padded = np.pad(img_array, ((pad_size, pad_size), (pad_size, pad_size), (0, 0)), mode='constant', constant_values=0)

    pool = multiprocessing.Pool(processes=pool_size)

    # Suddivisione in chunk (a ogni processo viene assegnata una parte dell'immagine)
    chunk_size = w // pool_size
    chunks = [
        (img_padded[i * chunk_size:(i + 1) * chunk_size + 2 * pad_size], matrix)
        for i in range(pool_size)
    ]

    # Seleziona quale versione usare
    worker_func = worker_vectorized if vectorized else worker_non_vectorized

    # Parallelizziamo la convoluzione
    results = pool.map(worker_func, chunks)

    # Ricostruzione dell'immagine dai risultati
    img_t = np.vstack(results)

    pool.close()
    pool.join()

    # Convertiamo il risultato in immagine e salviamo
    return Image.fromarray(np.clip(img_t, 0, 255).astype(np.uint8))


def worker_non_vectorized(args):
    """Applica la convoluzione pixel per pixel (non vettorizzata)."""
    img_chunk, matrix = args
    h, w, _ = img_chunk.shape
    s = (matrix.shape[0] - 1) // 2  # Determiniamo la metà del kernel
    result = np.zeros((h - 2 * s, w - 2 * s, 3))  # Output senza il padding

    for x in range(s, h - s):
        for y in range(s, w - s):
            pixel_value = np.zeros(3)
            for i in range(-s, s + 1):
                for j in range(-s, s + 1):
                    pixel_value += img_chunk[x + i, y + j] * matrix[s + i, s + j]
            result[x - s, y - s] = np.clip(pixel_value, 0, 255)

    return result.astype(np.uint8)


def worker_vectorized(args):
    """Applica la convoluzione vettorizzata su un chunk dell'immagine usando NumPy."""
    img_chunk, matrix = args
    h, w, _ = img_chunk.shape
    k_size = matrix.shape[0]
    s = k_size // 2  # Determiniamo la metà del kernel
    result = np.zeros((h - 2 * s, w - 2 * s, 3))  # Output senza il padding

    # Estrarre finestre dell'immagine e applicare la convoluzione con broadcasting
    for i in range(3):  # Per ogni canale RGB
        for y in range(k_size):
            for x in range(k_size):
                result[:, :, i] += img_chunk[y:y + h - 2 * s, x:x + w - 2 * s, i] * matrix[y, x]

    return np.clip(result, 0, 255).astype(np.uint8)
