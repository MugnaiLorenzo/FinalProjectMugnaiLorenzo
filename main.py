import resizeImage
import resizeImageParallel
import Kernel
import multiprocessing
import time
import draw


def worker(matrix):
    start = time.time()
    resizeImage.ResizeImage("dog.jpg", matrix[1], matrix[0])
    end = time.time()
    return end - start


if __name__ == "__main__":
    k = Kernel.Kernel()
    list_time = []
    time_parallel = []
    for matrix in k.getMatrix():
        start = time.time()
        resizeImageParallel.iniziatlitation("dog.jpg", matrix[1], matrix[0])
        end = time.time()
        list_time.append(end - start)
    s_time = 0
    for t in list_time:
        s_time += t
        time_parallel.append(s_time)
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    time_transform = pool.map(worker, k.getMatrix())
    draw.Draw(time_transform, time_parallel, k.getMatrix())
