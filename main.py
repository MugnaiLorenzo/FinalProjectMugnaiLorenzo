import os
import time
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from Kernel import Kernel
from resizeImage import ResizeImage
from resizeImageParallel import iniziatlitation


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_image_folders(base_dir):
    return [os.path.join(base_dir, folder) for folder in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, folder)) and folder in ["480x270", "960x540", "1920x1080",
                                                                            "3840x2160"]]


def get_images_from_folder(folder):
    return [os.path.join(folder, img) for img in os.listdir(folder) if img.endswith(('.png', '.jpg', '.jpeg'))]


def plot_results(kernel_name, folder_times, thread_counts):
    results_dir = "Risultati"
    ensure_directory_exists(results_dir)
    thread_counts_full = [1] + thread_counts
    for folder_name in folder_times.keys():
        time_s, time_p, time_p_vec = folder_times[folder_name]

        # **Plot per il tempo totale**
        plt.figure()
        time_full = [time_s] + time_p  # Unisce il tempo sequenziale con quelli paralleli normali
        time_full_vec = [time_s] + time_p_vec  # Tempi paralleli vettorizzati
        plt.plot(thread_counts_full, time_full, marker='o', linestyle='-', label="Non Vett.")
        plt.plot(thread_counts_full, time_full_vec, marker='s', linestyle='--', label="Vett.")
        plt.xlabel("Numero di Thread (1 = Sequenziale)")
        plt.ylabel("Tempo Totale (s)")
        plt.legend()
        plt.title(f"Confronto Tempi - {folder_name} - Kernel: {kernel_name}")
        plt.savefig(os.path.join(results_dir, f"execution_times_{kernel_name}_{folder_name}.png"))
        # **Plot per Speedup**
        plt.figure()
        speedup = [time_s / tp if tp > 0 else 0 for tp in time_full]
        speedup_vec = [time_s / tp if tp > 0 else 0 for tp in time_full_vec]
        plt.plot(thread_counts_full, speedup, marker='o', linestyle='-', label="Non Vett.")
        plt.plot(thread_counts_full, speedup_vec, marker='s', linestyle='--', label="Vett.")
        plt.xlabel("Numero di Thread (1 = Sequenziale)")
        plt.ylabel("Speedup")
        plt.legend()
        plt.title(f"Speedup - {folder_name} - Kernel: {kernel_name}")
        plt.savefig(os.path.join(results_dir, f"speedup_{kernel_name}_{folder_name}.png"))
        plt.close()


def extract_resolution(folder):
    _, resolution = folder.split('\\')
    width, height = map(int, resolution.split('x'))
    return width * height


if __name__ == "__main__":
    base_image_dir = "image"
    folders = get_image_folders(base_image_dir)
    print(folders)
    k = Kernel()
    print(range(2, multiprocessing.cpu_count() + 2, 2))
    thread_counts = list([2, 4, 8, 12])
    folders = sorted(folders, key=extract_resolution)
    x = ""
    print("Cartelle:", folders)
    for matrix, kernel_name in k.getMatrix():
        print(f"\n🔍 Analizzando Kernel: {kernel_name}\n")
        folder_times = {}

        for folder in folders:
            folder_name = os.path.basename(folder)
            images = get_images_from_folder(folder)
            if not images:
                continue
            print(f"🖼️ Processing images in folder: {folder_name}...")
            x = x + f"🖼️ Processing images in folder: {folder_name}...\n"
            serial_dir = os.path.join("imageSequential", folder_name)
            parallel_dir = os.path.join("imageParallel", folder_name)
            ensure_directory_exists(serial_dir)
            ensure_directory_exists(parallel_dir)
            # # Esecuzione SEQUENZIALE
            total_serial = 0
            for image_path in images:
                print(f"Processing image: {image_path}")
                seq = ResizeImage(image_path, kernel_name, matrix)
                start_serial = time.time()
                img_t = seq.transform()
                total_serial += time.time() - start_serial
                img_t.save(os.path.join("imageSequential",
                                        image_path.replace("image\\", "").rsplit(".", 1)[0] + kernel_name + "." +
                                        image_path.rsplit(".", 1)[1]))
                print(f" - {folder_name} - Sequenziale: {time.time() - start_serial:.4f} s")
            # Esecuzione PARALLELA
            total_parallel_vec = []
            total_parallel = []
            for threads in thread_counts:
                total_parallel_run = 0
                total_parallel_run_vec = 0
                for image_path in images:
                    file_name = image_path.replace("image\\", "")
                    print(f"Processing image: {image_path}")
                    start_parallel = time.time()
                    img_t = iniziatlitation(image_path, matrix, threads, vectorized=False)
                    total_parallel_run += time.time() - start_parallel
                    print(f"   {threads} threads: {total_parallel_run:.4f} s")
                    if threads == 2:
                        output_path = os.path.join("imageParallel", file_name.rsplit(".", 1)[0] + kernel_name + "." +
                                                   file_name.rsplit(".", 1)[1])
                        img_t.save(output_path)
                    print(f"Processing image (Vectorized): {image_path}")
                    start_parallel_vec = time.time()
                    iniziatlitation(image_path, matrix, threads, vectorized=True)
                    total_parallel_run_vec += time.time() - start_parallel_vec
                    print(f"   {threads} threads (Vett.): {total_parallel_run_vec:.4f} s")
                total_parallel_vec.append(total_parallel_run_vec)
                total_parallel.append(total_parallel_run)
            folder_times[folder_name] = (total_serial, total_parallel, total_parallel_vec)
        # Generazione dei grafici per il kernel corrente
        plot_results(kernel_name, folder_times, thread_counts)
        # Stampa dei tempi di esecuzione per il kernel corrente
        x = x + f"\n📊 Risultati per Kernel: {kernel_name}\n"
        for folder_name, (time_s, time_p, time_p_vec) in folder_times.items():
            x = x + f" - {folder_name} - Sequenziale: {time_s:.4f} s\n"
            for i, threads in enumerate(thread_counts):
                speedup = time_s / time_p[i] if time_p[i] > 0 else 0
                speedup_vec = time_s / time_p_vec[i] if time_p_vec[i] > 0 else 0
                x = x + f"   {threads} threads: {time_p[i]:.4f} s | SpeedUp: {speedup:.2f}x\n"
                x = x + f"   {threads} threads (Vett.): {time_p_vec[i]:.4f} s | SpeedUp: {speedup_vec:.2f}x\n"
    # Apri il file in modalità scrittura ('w' per sovrascrivere, 'a' per aggiungere)
    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(x)
