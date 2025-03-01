import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import logging
import configparser

# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'user_sync.log')

# Setup logging
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'))
csv_path = config['SETTINGS']['csv_path']
script_dir = os.path.dirname(__file__)

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('users.csv'):
            logging.info(f"Detected update to CSV file: {event.src_path}")
            try:
                # Run PowerShell with explicit path and execution policy bypass
                ps_command = [
                    "powershell.exe",
                    "-ExecutionPolicy", "Bypass",
                    "-File", os.path.join(script_dir, "main.ps1")
                ]
                result = subprocess.run(ps_command, capture_output=True, text=True, check=True)
                logging.info(f"PowerShell output: {result.stdout}")
                if result.stderr:
                    logging.error(f"PowerShell errors: {result.stderr}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to execute PowerShell: {e.stderr}")

if __name__ == "__main__":
    logging.info(f"Starting local user sync monitoring... CSV path: {csv_path}")
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.join(script_dir, '..', 'input'), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
        observer.stop()
    observer.join()