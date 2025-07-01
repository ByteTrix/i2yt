@echo off
title Instagram Reel Scraper

:: Change to script directory
cd /d "%~dp0"

:: Launch PowerShell script
echo Starting Instagram Reel Scraper...
echo.
powershell.exe -ExecutionPolicy Bypass -File "run_scraper.ps1"

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause >nul
)
