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
                Write-Log "Invalid action for $username : $action" "ERROR"
            }
        }
    } catch {
        Write-Log "Error processing $username : $_" "ERROR"
    }
}
Write-Log "User sync process completed."