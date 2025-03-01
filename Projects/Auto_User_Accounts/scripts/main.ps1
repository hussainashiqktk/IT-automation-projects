param (
    [Parameter(Mandatory=$true)]
    [string]$CsvPath
)

# Load helper functions
. "$PSScriptRoot\utils.ps1"

# Log function outputs to console (Python handles file logging)
function Write-Log {
    param ($Message, $Level = "INFO")
    Write-Host "$Level - $Message"
}

# Start script
Write-Log "Script started from: $PSScriptRoot"
Write-Log "Using CSV path: $CsvPath"

if (-not (Test-Path $CsvPath)) {
    Write-Log "CSV file not found at: $CsvPath" "ERROR"
    exit 1
}

# Import CSV and process each row
try {
    $users = Import-Csv -Path $CsvPath
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