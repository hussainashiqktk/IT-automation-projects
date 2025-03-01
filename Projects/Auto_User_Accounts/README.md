
### 1. Project Overview
This automation monitors a CSV file for changes and instantly creates, modifies, or deletes local user accounts on a Windows system based on the file’s contents, simulating a user management system without Active Directory. It’s perfect for standalone systems or small-scale IT setups where local accounts need quick, automated updates (e.g., lab computers or test environments). The tool eliminates manual user management tasks, ensuring real-time updates and logging all actions for auditing.

---

### 2. Tool/Technology Stack
- **PowerShell**: Native to Windows, ideal for managing local users with cmdlets like `New-LocalUser`.
- **Python**: Handles CSV file monitoring and parsing using `watchdog` for real-time detection.
- **CSV File**: Simple input format for user data, editable by anyone.
- **Windows OS**: Primary target for local user management; adaptable to Linux with Python and `os` commands.
- **Logging**: Built into both Python and PowerShell for detailed operation tracking.

Justification: PowerShell is efficient for Windows local user tasks, while Python ensures cross-platform file monitoring and logging consistency.

---

### 3. Project Structure
```
/LocalUserSync
├── /scripts
│   ├── main.ps1          # PowerShell script to manage local users
│   ├── monitor.py        # Python script to watch CSV file and trigger PowerShell
│   └── utils.ps1         # Helper functions for user operations
├── /config
│   └── config.ini        # Configuration file (CSV path, log settings)
├── /input
│   └── users.csv         # Input CSV file with user data
├── /logs
│   └── user_sync.log     # Log file for all operations
└── README.md             # Project documentation
```
- **`scripts/`**: Core logic for monitoring and user management.
- **`config/`**: Customizable settings (e.g., CSV path).
- **`input/`**: Holds the monitored CSV file.
- **`logs/`**: Stores detailed logs of all actions.
- **`README.md`**: Setup and usage instructions.

---

### 4. Full Code

#### `monitor.py` (Python script to watch CSV and trigger PowerShell)
```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import logging
import configparser

# Setup logging
logging.basicConfig(filename='logs/user_sync.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')
csv_path = config['SETTINGS']['csv_path']

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('users.csv'):
            logging.info(f"Detected update to CSV file: {event.src_path}")
            try:
                # Trigger PowerShell script
                result = subprocess.run(["powershell.exe", "-File", "scripts/main.ps1"], 
                                      capture_output=True, text=True, check=True)
                logging.info(f"PowerShell script executed successfully: {result.stdout}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to execute PowerShell script: {e.stderr}")

if __name__ == "__main__":
    logging.info("Starting local user sync monitoring...")
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path='input', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
        observer.stop()
    observer.join()
```

#### `main.ps1` (PowerShell script to manage local users)
```powershell
# Load helper functions
. "$PSScriptRoot\utils.ps1"

# Setup logging
$logPath = "..\logs\user_sync.log"
function Write-Log {
    param ($Message, $Level = "INFO")
    "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - $Level - $Message" | Out-File -FilePath $logPath -Append
}

# Load config
$config = Get-Content -Path "..\config\config.ini" | ConvertFrom-StringData
$csvPath = $config.csv_path
Write-Log "Starting user sync process with CSV: $csvPath"

# Import CSV and process each row
$users = Import-Csv -Path $csvPath
foreach ($user in $users) {
    $username = $user.Username
    $action = $user.Action
    $fullName = $user.FullName
    $password = $user.Password

    try {
        switch ($action) {
            "CREATE" {
                New-LocalUserAccount -Username $username -FullName $fullName -Password $password
                Write-Log "Created local user: $username"
            }
            "MODIFY" {
                Update-LocalUserAccount -Username $username -FullName $fullName -Password $password
                Write-Log "Modified local user: $username"
            }
            "DELETE" {
                Remove-LocalUserAccount -Username $username
                Write-Log "Deleted local user: $username"
            }
            default {
                Write-Log "Invalid action for $username: $action" "ERROR"
            }
        }
    } catch {
        Write-Log "Error processing $username: $_" "ERROR"
    }
}
Write-Log "User sync process completed."
```

#### `utils.ps1` (Helper functions for local user operations)
```powershell
function New-LocalUserAccount {
    param ($Username, $FullName, $Password)
    $securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
    New-LocalUser -Name $Username -FullName $FullName -Password $securePassword -AccountNeverExpires
}

function Update-LocalUserAccount {
    param ($Username, $FullName, $Password)
    if ($Password) {
        $securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
        Set-LocalUser -Name $Username -FullName $FullName -Password $securePassword
    } else {
        Set-LocalUser -Name $Username -FullName $FullName
    }
}

function Remove-LocalUserAccount {
    param ($Username)
    Remove-LocalUser -Name $Username
}
```

#### `config.ini` (Configuration file)
```ini
[SETTINGS]
csv_path = ..\input\users.csv
```

#### `input/users.csv` (Sample CSV structure)
```csv
Username,Action,FullName,Password
jdoe,CREATE,John Doe,Pass1234!
asmith,MODIFY,Alice Smith,NewPass567
bjones,DELETE,Bob Jones,
```

---

### 5. Setup Instructions
To set up, install Python 3.x and `watchdog` (`pip install watchdog`) on your Windows system. Download or create the `LocalUserSync` folder structure as outlined, placing all files in their respective directories. Edit `config.ini` if you move `users.csv` to a different path. Run PowerShell as an administrator (required for local user management), then start the monitor with `python scripts/monitor.py` from the project root. Test by editing `users.csv`—e.g., add a row—and verify changes via `net user` or the log file. Optionally, use Task Scheduler to run `monitor.py` at startup.

---

### 6. Usage Documentation
Update `input/users.csv` with user details (columns: `Username`, `Action`, `FullName`, `Password`)—e.g., `jdoe,CREATE,John Doe,Pass1234!`. Save the file, and the tool will instantly process it (e.g., create the user locally). Check `logs/user_sync.log` for a detailed history of actions. Customize the CSV path in `config.ini` or modify `main.ps1` to tweak user settings (e.g., add groups). Run `net user <username>` to confirm changes. Expect updates within seconds of saving the CSV.

---

### 7. Troubleshooting Guide
If users aren’t created, ensure PowerShell is run as admin—local user management requires elevated privileges. If `monitor.py` fails, verify `watchdog` is installed (`pip list`) and the CSV path is correct. For "user not found" errors during deletion, check if the user exists (`net user`). If logs don’t appear, confirm write permissions to the `logs/` folder.

---

### 8. Sample Output
**`logs/user_sync.log`:**
```
2025-03-01 10:15:23 - INFO - Starting local user sync monitoring...
2025-03-01 10:15:30 - INFO - Detected update to CSV file: input\users.csv
2025-03-01 10:15:30 - INFO - Starting user sync process with CSV: ..\input\users.csv
2025-03-01 10:15:31 - INFO - Created local user: jdoe
2025-03-01 10:15:32 - INFO - Modified local user: asmith
2025-03-01 10:15:33 - INFO - Deleted local user: bjones
2025-03-01 10:15:33 - INFO - User sync process completed.
```

---

### 9. Impact Statement
This automation reduces local user management from minutes of manual CLI/GUI work to instantaneous CSV-driven updates, minimizing errors and providing a full audit trail via logs.

---

### Linux Adaptation Notes
For Linux, replace `main.ps1` with a Python script using `os.system()` to call `useradd`, `usermod`, and `userdel`. Example: `os.system(f"useradd -c '{fullName}' -m {username} -p $(openssl passwd -1 {password})")`. Update `monitor.py` to call this script instead. Logging remains consistent across platforms.
