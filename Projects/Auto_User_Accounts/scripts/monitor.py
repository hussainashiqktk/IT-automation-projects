import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import logging
import configparser

# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)  # Creates logs/ if it doesn’t exist
log_file = os.path.join(log_dir, 'user_sync.log')

# Setup logging
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'))
csv_path = config['SETTINGS']['csv_path']

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('users.csv'):
            logging.info(f"Detected update to CSV file: {event.src_path}")
            try:
                # Trigger PowerShell script (relative path from scripts/)
                result = subprocess.run(["powershell.exe", "-File", "main.ps1"], 
                                      capture_output=True, text=True, check=True)
                logging.info(f"PowerShell script executed successfully: {result.stdout}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to execute PowerShell script: {e.stderr}")

if __name__ == "__main__":
    logging.info("Starting local user sync monitoring...")
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.join(os.path.dirname(__file__), '..', 'input'), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
        observer.stop()
    observer.join()