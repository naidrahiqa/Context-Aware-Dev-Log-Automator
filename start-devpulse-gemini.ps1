# DevPulse with Gemini API - Quick Launcher
# Run this script to set environment variables and start DevPulse

# Set Gemini API configuration
$env:DEVPULSE_API_KEY="AIzaSyDdqFTHRHSascogHReFQBEId98FllgEgWE"
$env:DEVPULSE_AI_PROVIDER="litellm"
$env:DEVPULSE_MODEL="gemini/gemini-1.5-flash"
$env:DEVPULSE_PRIVACY_MODE="false"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " DevPulse with Google Gemini API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Show configuration
devpulse config

Write-Host ""
Write-Host "Environment variables set!" -ForegroundColor Green
Write-Host "You can now use DevPulse commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  devpulse track <path>    - Track a directory" -ForegroundColor Cyan
Write-Host "  devpulse start           - Start monitoring" -ForegroundColor Cyan
Write-Host "  devpulse log --today     - Generate summary" -ForegroundColor Cyan
Write-Host "  devpulse --help          - View all commands" -ForegroundColor Cyan
Write-Host ""
