# AMAZON SNIPER - instalacion en Windows (PowerShell, usuario normal)
# Ejecutar desde la carpeta amazon-sniper:  powershell -ExecutionPolicy Bypass -File deploy\windows\install.ps1
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path "$PSScriptRoot\..\..").Path
Write-Host "Instalando en $Root"

python -m venv "$Root\.venv"
& "$Root\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "$Root\.venv\Scripts\python.exe" -m pip install -r "$Root\engine\requirements.txt"
Push-Location "$Root\web"; npm ci; npm run build; Pop-Location

$py = "$Root\.venv\Scripts\pythonw.exe"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 999 `
  -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 0) -StartWhenAvailable
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Motor: 'supervise' ya reinicia el proceso si falla; la tarea lo relanza si el propio supervisor cae.
$engine = New-ScheduledTaskAction -Execute $py -Argument "-m sniper supervise" -WorkingDirectory "$Root\engine"
Register-ScheduledTask -TaskName "AmazonSniperEngine" -Action $engine -Trigger $trigger -Settings $settings -Force | Out-Null

$web = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c npm run start" -WorkingDirectory "$Root\web"
Register-ScheduledTask -TaskName "AmazonSniperWeb" -Action $web -Trigger $trigger -Settings $settings -Force | Out-Null

Start-ScheduledTask -TaskName "AmazonSniperEngine"
Start-ScheduledTask -TaskName "AmazonSniperWeb"
Write-Host "Listo. Panel: http://127.0.0.1:3210  (diagnostico: .venv\Scripts\python -m sniper doctor  desde engine\)"
