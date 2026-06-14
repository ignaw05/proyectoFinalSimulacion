import subprocess
import datetime
import hashlib
import os
import time
import csv

def capture(num_images: int, base_filename: str):
    # pyrefly: ignore [missing-import]
    from playwright.sync_api import sync_playwright
    url = "https://share.earthcam.net/tJ90CoLmq7TzrY396Yd88A4kdLdbDd6oQl5D9Ktzt8U/times_square_locations/street_cam/live"
    output_dir = "captures"
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="en-US"
        )
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Use video selector for the EarthCam page
        video_selector = "video"
        
        print("Waiting for the video player to load...")
        page.wait_for_selector(video_selector, timeout=15000)
        
        # Wait a couple of seconds to make sure the video stream starts rendering
        print("Waiting for video stream to start...")
        time.sleep(6)
        
        video_element = page.locator(video_selector)
        video_element.scroll_into_view_if_needed()
        
        print(f"Starting capture of {num_images} screenshots...")
        for i in range(1, num_images + 1):
            filename = f"{base_filename}{i}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Take screenshot of the video element
            video_element.screenshot(path=filepath)
            print(f"Saved: {filepath}")
            
            # Wait 3 milliseconds between captures if it's not the last capture
            if i < num_images:
                time.sleep(3)
                
        browser.close()

def hashImages():
    output_dir = "captures"
    if not os.path.exists(output_dir):
        return ""
    
    hashes = []
    # Filter png files and sort them to keep order consistent
    files = sorted([f for f in os.listdir(output_dir) if f.lower().endswith(".png")])
    
    for filename in files:
        filepath = os.path.join(output_dir, filename)
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        hashes.append(sha256.hexdigest())
        
    return "".join(hashes)

def xor_process(value):
    value_str = value if isinstance(value, str) else str(value)
    
    # Ensure blockSize always produces at least 2 blocks to guarantee reduction
    blockSize = 16
    while blockSize >= 2 and len(value_str) // blockSize < 2:
        blockSize //= 2
    blockSize = max(blockSize, 1)
    
    blocks = [value_str[i:i+blockSize] for i in range(0, len(value_str), blockSize) if value_str[i:i+blockSize]]
    shortened = 0
    for block in blocks:
        try:
            shortened ^= int(block, 16)
        except ValueError:
            val = 0
            for char in block:
                val = (val << 8) | ord(char)
            shortened ^= val
    return shortened

def generateRandomNumberSet(seed, length: int, fileName: str = "randomNumbers.csv", fieldName: str = None):
    if length <= 0:
        return []
        
    # Do-while: reduce the seed via XOR until it has 3 or fewer digits
    m = 180
    actual_seed = seed
    while True:
        actual_seed = xor_process(actual_seed)
        if len(str(actual_seed)) <= 3:
            break

    # Se realiza la relacion de recurrencia del LCG usando enteros para evitar el sesgo/convergencia.
    # El primer elemento de la secuencia es la semilla reducida.
    random_integers = [actual_seed]
    a = 61
    b = 11
    
    for i in range(1, length):
        next_val = (a * random_integers[i-1] + b) % m
        random_integers.append(next_val)
    
    # Convertimos los numeros en probabilidades (Ri en el rango [0, 1)) dividiendo por m.
    # Para asegurar que todos los numeros (incluyendo la semilla si es mayor o igual a m)
    # esten en el rango [0, 1), aplicamos modulo m antes de dividir por m.
    randomNumbers = [(val % m) / m for val in random_integers]
    
    if fieldName is None:
        fieldName = os.path.splitext(os.path.basename(fileName))[0]
        
    # Se exportan los numeros generados a un archivo CSV con la cabecera correspondiente
    with open(fileName, "w", encoding="utf-8") as f:
        f.write(f"{fieldName}\n")
        for num in randomNumbers:
            f.write(f"{num}\n")
    
    return randomNumbers

def generateRandomNumberFile(fileName):
    capture(5, "imagen")
    result = hashImages()
    fieldName = os.path.splitext(os.path.basename(fileName))[0]
    return generateRandomNumberSet(result, 406, fileName=fileName, fieldName=fieldName)

def combine_csv(file_names: list, output_filename: str = "combined.csv"):
    files_data = []
    for name in file_names:
        with open(name, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            files_data.append(lines)
            
    with open(output_filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in zip(*files_data):
            writer.writerow(row)

if __name__ == "__main__":
    generateRandomNumberFile("porcentajeACargarU.csv")
    generateRandomNumberFile("cargaInicialU.csv")
    generateRandomNumberFile("tipoAutonomiaU.csv")
    combine_csv(["porcentajeACargarU.csv", "cargaInicialU.csv", "tipoAutonomiaU.csv"], "numeros_generados.csv")