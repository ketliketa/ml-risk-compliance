# PowerShell script to start both backend and frontend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ML Project - Backend & Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start backend in a new window
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
$backendPath = Join-Path $scriptDir "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; `$env:PYTHONPATH = (Get-Location).Path; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
$frontendPath = Join-Path $scriptDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backend: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Servers are running in separate windows." -ForegroundColor Green
Write-Host "Close those windows to stop the servers." -ForegroundColor Yellow
