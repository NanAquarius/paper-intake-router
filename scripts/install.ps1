$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not $env:PYTHON_BIN) { $env:PYTHON_BIN = 'python' }
if (-not $env:VENV_DIR) { $env:VENV_DIR = '.venv' }
if (-not $env:REQ_FILE) { $env:REQ_FILE = 'requirements-minimal.txt' }

& $env:PYTHON_BIN -m venv $env:VENV_DIR
& "$env:VENV_DIR\Scripts\python.exe" -m pip install --upgrade pip

if (Test-Path $env:REQ_FILE) {
  & "$env:VENV_DIR\Scripts\pip.exe" install -r $env:REQ_FILE
}

Write-Host ''
Write-Host '[paper-intake-router] environment ready'
Write-Host "activate with: .\\$env:VENV_DIR\\Scripts\\Activate.ps1"
