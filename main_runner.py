import threading
import subprocess

def run_bigbasket():
    print("Running BigBasket scraper...")
    subprocess.run(["python", "BigBasket/main.py"], cwd=".")

def run_otipy():
    print("Running Otipy scraper...")
    subprocess.run(["python", "Otipy/main.py"], cwd=".")

# Run the main functions in separate threads
bigbasket_thread = threading.Thread(target=run_bigbasket)
otipy_thread = threading.Thread(target=run_otipy)

bigbasket_thread.start()
otipy_thread.start()

# Wait for threads to finish
bigbasket_thread.join()
otipy_thread.join()

print("Both scrapers completed.")
