Set-Variable -Name "cwd" -Value (Get-Location)
$env:PYTHONPATH += "$cwd\tasklist"