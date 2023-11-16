import threading
import subprocess

def run_bigbasket():
    print("Running BigBasket scraper...")
    subprocess.run(["python", "BigBasket/main.py"], cwd=".")

def run_otipy():
    print("Running Otipy scraper...")
    subprocess.run(["python", "Otipy/main.py"], cwd=".")

bigbasket_thread = threading.Thread(target=run_bigbasket)
otipy_thread = threading.Thread(target=run_otipy)

bigbasket_thread.start()
otipy_thread.start()

bigbasket_thread.join()
otipy_thread.join()

print("Both scrapers completed.")
