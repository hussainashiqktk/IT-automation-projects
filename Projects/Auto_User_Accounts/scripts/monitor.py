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
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

# Load and resolve config
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
logging.info(f"Reading config from: {config_path}")
if not os.path.exists(config_path):
    logging.error(f"Config file not found at: {config_path}")
    exit(1)
config.read(config_path)
try:
    relative_csv_path = config['SETTINGS']['csv_path']
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', relative_csv_path))
    logging.info(f"Resolved CSV path from '{relative_csv_path}' to: {csv_path}")
except KeyError:
    logging.error("Config file missing [SETTINGS] section or 'csv_path' key")
    exit(1)
if not os.path.exists(csv_path):
    logging.error(f"CSV file not found at: {csv_path}")
    exit(1)
script_dir = os.path.dirname(__file__)

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('users.csv'):
            logging.info(f"Detected update to CSV file: {event.src_path}")
            try:
                ps_command = [
                    "powershell.exe",
                    "-ExecutionPolicy", "Bypass",
                    "-File", os.path.join(script_dir, "main.ps1"),
                    "-CsvPath", csv_path
                ]
                result = subprocess.run(ps_command, capture_output=True, text=True, check=True)
                for line in result.stdout.splitlines():
                    if line.strip():
                        logging.info(f"PowerShell: {line.strip()}")
                if result.stderr:
                    for line in result.stderr.splitlines():
                        if line.strip():
                            logging.error(f"PowerShell error: {line.strip()}")
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
            time.sleep(30)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
        observer.stop()
    observer.join()