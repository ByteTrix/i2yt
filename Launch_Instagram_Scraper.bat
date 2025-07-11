@echo off
REM Instagram Reel Scraper - Terminal Launcher
REM This batch file opens a new terminal window and runs the PowerShell script

REM Set the title for the command prompt window
title Instagram Reel Scraper

REM Change to the script directory
cd /d "%~dp0"

start wt -p "PowerShell" --title "Instagram Reel Scraper" pwsh -NoExit -ExecutionPolicy Bypass -File "d:\Kodo\i2yt\run_scraper.ps1"

REM Keep the batch file window open briefly to show any errors
timeout /t 2 /nobreak >nul
exit
