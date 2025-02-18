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
    """Crea una cartella se non esiste."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_image_folders(base_dir):
    """Ottiene tutte le sottocartelle della cartella principale."""
    return [os.path.join(base_dir, folder) for folder in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, folder)) and folder in ["480x270", "960x540", "1920x1080", "3840x2160"]]

def get_images_from_folder(folder):
    """Ottiene tutte le immagini da una cartella specifica."""
    return [os.path.join(folder, img) for img in os.listdir(folder) if img.endswith(('.png', '.jpg', '.jpeg'))]

def plot_results(kernel_name, folder_times, thread_counts):
    """Genera e salva i grafici per ogni kernel confrontando tutte le dimensioni delle immagini."""
    results_dir = "Risultati"
    ensure_directory_exists(results_dir)

    thread_counts_full = [1] + thread_counts  # Include il tempo sequenziale come primo valore

    plt.figure()
    for folder_name, (time_s, time_p) in folder_times.items():
        time_full = [time_s] + time_p  # Unisce il tempo sequenziale con quelli paralleli
        plt.plot(thread_counts_full, time_full, marker='o', linestyle='-', label=f"{folder_name}")

    plt.xlabel("Numero di Thread (1 = Sequenziale)")
    plt.ylabel("Tempo Totale (s)")
    plt.legend()
    plt.title(f"Confronto Tempi - Kernel: {kernel_name}")
    plt.savefig(os.path.join(results_dir, f"execution_times_{kernel_name}.png"))

    plt.figure()
    for folder_name, (time_s, time_p) in folder_times.items():
        time_full = [time_s] + time_p
        speedup = [time_s / tp if tp > 0 else 0 for tp in time_full]
        plt.plot(thread_counts_full, speedup, marker='o', label=f"{folder_name}")

    plt.xlabel("Numero di Thread (1 = Sequenziale)")
    plt.ylabel("Speedup")
    plt.legend()
    plt.title(f"Speedup - Kernel: {kernel_name}")
    plt.savefig(os.path.join(results_dir, f"speedup_{kernel_name}.png"))

def extract_resolution(folder):
    _, resolution = folder.split('/')
    width, height = map(int, resolution.split('x'))
    return width * height  # Ordiniamo in base ai pixel totali

if __name__ == "__main__":
    base_image_dir = "image"
    folders = get_image_folders(base_image_dir)
    k = Kernel()
    thread_counts = list(range(2, multiprocessing.cpu_count() + 2, 2))
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
            # Creazione delle cartelle di output
            serial_dir = os.path.join("imageSequential", folder_name)
            parallel_dir = os.path.join("imageParallel", folder_name)
            ensure_directory_exists(serial_dir)
            ensure_directory_exists(parallel_dir)

            # Esecuzione SEQUENZIALE
            total_serial = 0
            for image_path in images:
                print(f"Processing image: {image_path}")
                start_serial = time.time()
                ResizeImage(image_path, kernel_name, matrix)
                total_serial += time.time() - start_serial
                print(f" - {folder_name} - Sequenziale: {time.time() - start_serial:.4f} s")

            # Esecuzione PARALLELA con vari thread
            total_parallel = []
            for threads in thread_counts:
                total_parallel_run = 0
                for image_path in images:
                    print(f"Processing image: {image_path}")
                    start_parallel = time.time()
                    iniziatlitation(image_path, kernel_name, matrix, threads)
                    total_parallel_run += time.time() - start_parallel
                    print(f"   {threads} threads: {total_parallel_run:.4f} s")
                total_parallel.append(total_parallel_run)

            folder_times[folder_name] = (total_serial, total_parallel)

        # Generazione dei grafici per il kernel corrente
        plot_results(kernel_name, folder_times, thread_counts)

        # Stampa dei tempi di esecuzione per il kernel corrente
        x = x + f"\n📊 Risultati per Kernel: {kernel_name}\n"
        for folder_name, (time_s, time_p) in folder_times.items():
            x = x + f" - {folder_name} - Sequenziale: {time_s:.4f} s\n"
            for i, threads in enumerate(thread_counts):
                speedup = time_s / time_p[i] if time_p[i] > 0 else 0
                x = x + f"   {threads} threads: {time_p[i]:.4f} s | SpeedUp: {speedup:.2f}x\n"
    # Apri il file in modalità scrittura ('w' per sovrascrivere, 'a' per aggiungere)
    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(x)