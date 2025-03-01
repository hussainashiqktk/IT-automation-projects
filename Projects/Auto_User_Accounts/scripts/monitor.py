
"""
This script monitors a directory for modifications to a specific CSV file ("users.csv")
and triggers a corresponding PowerShell script ("scripts/main.ps1") whenever a change 
is detected. The script uses the watchdog package to perform file system monitoring, 
subprocess to execute the PowerShell script, and logging for debugging and audit trails.

The main parts of the code are:
1. Imports and Setup:
   - Importing required modules: time for delay management, watchdog's Observer and 
     FileSystemEventHandler for monitoring file system events, subprocess for running 
     external commands, logging for logging events, and configparser for reading configurations.
   - Logging is configured to record events with timestamps and log levels into a log file.
2. Configuration:
   - Using configparser to load settings from a configuration file located at "config/config.ini".
   - Retrieving the CSV file path from the file for potential future use.
3. CSVHandler Class:
   - Inherits from FileSystemEventHandler to define custom handling for file modifications.
   - The on_modified() method checks if the modified file is "users.csv". If so, it logs 
     the detection, then attempts to run a PowerShell script using subprocess.run().
   - If the script executes successfully, the output is logged; otherwise, errors are logged.
4. Main Execution:
   - Sets up and starts an Observer that monitors the "input" directory (non-recursive).
   - Enters an infinite loop with time.sleep(1) to keep the script running.
   - Gracefully stops the observer on a KeyboardInterrupt (e.g., Ctrl+C) and logs the event.
"""

import time  # For managing delays
from watchdog.observers import Observer  # Observes filesystem changes
from watchdog.events import FileSystemEventHandler  # Handles events triggered by the observer
import subprocess  # Used to run external PowerShell scripts
import logging  # For event logging
import configparser  # For reading configuration files

# --- Setup Logging ---
# Configures logging to output log messages to a file, including timestamp, level, and message.
logging.basicConfig(filename='logs/user_sync.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Load Configuration ---
# Creates a ConfigParser instance and reads settings from 'config/config.ini'.
# Retrieves the CSV file path from the SETTINGS section.
config = configparser.ConfigParser()
config.read('config/config.ini')
csv_path = config['SETTINGS']['csv_path']

# --- Define Event Handler Class ---
# Inherits from FileSystemEventHandler and overrides the on_modified method.
class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        """
        Called when a file or directory is modified.
        Checks if the modified file ends with 'users.csv'.
        If yes, logs the update and attempts to trigger the associated PowerShell script.
        """
        if event.src_path.endswith('users.csv'):
            logging.info(f"Detected update to CSV file: {event.src_path}")
            try:
                # Trigger PowerShell script using subprocess.run()
                # The call includes parameters to capture output (stdout and stderr) in text mode.
                # 'check=True' raises an exception for non-zero exit statuses.
                result = subprocess.run(["powershell.exe", "-File", "scripts/main.ps1"], 
                                        capture_output=True, text=True, check=True)
                logging.info(f"PowerShell script executed successfully: {result.stdout}")
            except subprocess.CalledProcessError as e:
                # Logs any errors encountered during the PowerShell script execution.
                logging.error(f"Failed to execute PowerShell script: {e.stderr}")

# --- Main Script Execution ---
if __name__ == "__main__":
    # Log that the monitoring service is starting.
    logging.info("Starting local user sync monitoring...")

    # Create an instance of the CSVHandler.
    event_handler = CSVHandler()

    # Instantiate the Observer, which will watch for filesystem events.
    observer = Observer()

    # Schedule the observer to monitor the 'input' directory.
    # 'recursive=False' indicates that subdirectories are not monitored.
    observer.schedule(event_handler, path='input', recursive=False)

    # Start the observer thread.
    observer.start()

    try:
        # Keep the script running with an infinite loop; sleep for 1 second at every iteration.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # If the user stops the script with a KeyboardInterrupt (Ctrl+C), log the event.
        logging.info("Monitoring stopped by user.")
        # Stop the observer gracefully.
        observer.stop()
    
    # Wait for the thread to terminate after observer.stop() is called.
    observer.join()
