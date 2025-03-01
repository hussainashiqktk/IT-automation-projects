# Load helper functions
. "$PSScriptRoot\utils.ps1"

# Setup logging
$logPath = "$PSScriptRoot\..\logs\user_sync.log"
function Write-Log {
    param ($Message, $Level = "INFO")
    "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) - $Level - $Message" | Out-File -FilePath $logPath -Append
    Write-Host "$Level - $Message"  # Also output to console for subprocess capture
}

# Load config
Write-Log "Script started from: $PSScriptRoot"
$config = Get-Content -Path "$PSScriptRoot\..\config\config.ini" | ConvertFrom-StringData
$csvPath = $config.csv_path
if (-not (Test-Path $csvPath)) {
    Write-Log "CSV file not found at: $csvPath" "ERROR"
    exit 1
}
Write-Log "Using CSV path: $csvPath"

# Import CSV and process each row
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