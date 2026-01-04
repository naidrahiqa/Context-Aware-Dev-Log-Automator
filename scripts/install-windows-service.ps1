# DevPulse Windows Service Installer
# Requires NSSM (Non-Sucking Service Manager)
# Install NSSM: choco install nssm OR download from https://nssm.cc/

param(
    [Parameter(Mandatory=$true)]
    [string]$DevPulsePath,
    
    [Parameter(Mandatory=$true)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$Provider = "groq",
    
    [Parameter(Mandatory=$false)]
    [string]$PrivacyMode = "false"
)

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ Error: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check if NSSM is installed
$nssmPath = Get-Command nssm -ErrorAction SilentlyContinue

if (-not $nssmPath) {
    Write-Host "❌ Error: NSSM is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install NSSM using one of these methods:" -ForegroundColor Yellow
    Write-Host "  1. Using Chocolatey: choco install nssm" -ForegroundColor Cyan
    Write-Host "  2. Download from: https://nssm.cc/download" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DevPulse Windows Service Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if DevPulse exists
if (-not (Test-Path $DevPulsePath)) {
    Write-Host "❌ Error: DevPulse executable not found at: $DevPulsePath" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found DevPulse at: $DevPulsePath" -ForegroundColor Green

# Stop and remove existing service if it exists
$existingService = Get-Service "DevPulse" -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host ""
    Write-Host "⚠️  Existing DevPulse service found. Removing..." -ForegroundColor Yellow
    nssm stop DevPulse
    nssm remove DevPulse confirm
}

# Install the service
Write-Host ""
Write-Host "Installing DevPulse service..." -ForegroundColor Cyan

nssm install DevPulse $DevPulsePath "start" "--daemon"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to install service" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Service installed" -ForegroundColor Green

# Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Cyan

nssm set DevPulse AppEnvironmentExtra "DEVPULSE_API_KEY=$ApiKey" "DEVPULSE_AI_PROVIDER=$Provider" "DEVPULSE_PRIVACY_MODE=$PrivacyMode"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to set environment variables" -ForegroundColor Red
    nssm remove DevPulse confirm
    exit 1
}

Write-Host "✓ Environment variables set" -ForegroundColor Green

# Set service description
nssm set DevPulse Description "DevPulse - Automated development activity tracker and log generator"
nssm set DevPulse DisplayName "DevPulse Tracker"

# Configure restart policy
nssm set DevPulse AppStopMethodConsole 10000
nssm set DevPulse AppExit Default Restart

# Set startup type to automatic
nssm set DevPulse Start SERVICE_AUTO_START

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Service Commands:" -ForegroundColor Yellow
Write-Host "  Start:   nssm start DevPulse" -ForegroundColor Cyan
Write-Host "  Stop:    nssm stop DevPulse" -ForegroundColor Cyan
Write-Host "  Restart: nssm restart DevPulse" -ForegroundColor Cyan
Write-Host "  Status:  nssm status DevPulse" -ForegroundColor Cyan
Write-Host "  Remove:  nssm remove DevPulse confirm" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to start the service now
$startNow = Read-Host "Start DevPulse service now? (Y/n)"

if ($startNow -eq "" -or $startNow -eq "Y" -or $startNow -eq "y") {
    Write-Host ""
    Write-Host "Starting DevPulse service..." -ForegroundColor Cyan
    nssm start DevPulse
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ DevPulse service started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "DevPulse is now running in the background 🚀" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start service. Check logs with: nssm status DevPulse" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "Service installed but not started." -ForegroundColor Yellow
    Write-Host "Run 'nssm start DevPulse' when ready." -ForegroundColor Yellow
}

Write-Host ""
