$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonLauncher = Join-Path $projectRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonLauncher)) { throw 'Run setup first.' }
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'SWITCH Workbench.lnk'
if (Test-Path -LiteralPath $shortcutPath) { throw "Shortcut already exists: $shortcutPath" }
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonLauncher
$shortcut.Arguments = '"' + (Join-Path $projectRoot 'scripts\launch.py') + '"'
$shortcut.WorkingDirectory = $projectRoot
$shortcut.Description = 'Start SWITCH Workbench and open your local research workspace'
$shortcut.IconLocation = $pythonLauncher + ',0'
$shortcut.Save()
Write-Output $shortcutPath
