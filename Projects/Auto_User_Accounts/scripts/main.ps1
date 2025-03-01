# Load helper functions
. "$PSScriptRoot\utils.ps1"

# Log function outputs to console (Python will handle file logging)
function Write-Log {
    param ($Message, $Level = "INFO")
    Write-Host "$Level - $Message"
}

# Load config
Write-Log "Script started from: $PSScriptRoot"
$configPath = "$PSScriptRoot\..\config\config.ini"
if (-not (Test-Path $configPath)) {
    Write-Log "Config file not found at: $configPath" "ERROR"
    exit 1
}
$config = Get-Content -Path $configPath | Where-Object { $_ -match '=' } | ConvertFrom-StringData
$csvPath = $config.csv_path
if (-not $csvPath) {
    Write-Log "CSV path not defined in config.ini" "ERROR"
    exit 1
}
if (-not (Test-Path $csvPath)) {
    Write-Log "CSV file not found at: $csvPath" "ERROR"
    exit 1
}
Write-Log "Using CSV path: $csvPath"

# Import CSV and process each row
try {
    $users = Import-Csv -Path $csvPath
    Write-Log "Found $($users.Count) users in CSV"
    if ($users.Count -eq 0) {
        Write-Log "No users to process (CSV might be empty or malformed)" "WARNING"
    }

    foreach ($user in $users) {
        $username = $user.Username
        $action = $user.Action
        $fullName = $user.FullName
        $password = $user.Password
        Write-Log "Processing user: $username with action: $action"

        switch ($action) {
            "CREATE" {
                try {
                    New-LocalUserAccount -Username $username -FullName $fullName -Password $password
                    Write-Log "Created local user: $username"
                } catch {
                    Write-Log "Error creating ${username}: $($_.Exception.Message)" "ERROR"
                }
            }
            "MODIFY" {
                try {
                    Update-LocalUserAccount -Username $username -FullName $fullName -Password $password
                    Write-Log "Modified local user: $username"
                } catch {
                    Write-Log "Error modifying ${username}: $($_.Exception.Message)" "ERROR"
                }
            }
            "DELETE" {
                try {
                    Remove-LocalUserAccount -Username $username
                    Write-Log "Deleted local user: $username"
                } catch {
                    Write-Log "Error deleting ${username}: $($_.Exception.Message)" "ERROR"
                }
            }
            default {
                Write-Log "Invalid action for ${username}: $action" "ERROR"
            }
        }
    }
} catch {
    Write-Log "Error processing CSV: $($_.Exception.Message)" "ERROR"
}
Write-Log "User sync process completed."