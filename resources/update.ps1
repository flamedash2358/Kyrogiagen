if ($args[0] -ne "internal") {
    Write-Output "This script is only for internal use, by our auto-updater. Exiting..."
    exit
}

Write-Output "Waiting for clangen to close..."
$clangen = Get-Process clangen -ErrorAction SilentlyContinue
if ($clangen) {
    $clangen.WaitForExit()
}
Write-Output "Clangen closed, continuing..."


Write-Output "Moving update files to the correct location..."


# move to ../

Set-Location ../

# delete old files
Write-Output "Deleting old files..."
Remove-Item -Recurse -Force $args[1]

Write-Output "Moving new files..."
Move-Item -Path "./clangen_update" -Destination $args[1]

# Write args[2] to update file
Write-Output "Writing update file..."
Set-Location $args[1]
Set-Content -Path "auto-updated" -Value $args[2]

Write-Output "Update complete!"

Write-Output "Restarting clangen..."

Start-Process Clangen.exe