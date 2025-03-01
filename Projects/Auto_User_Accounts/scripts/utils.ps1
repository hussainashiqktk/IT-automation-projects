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