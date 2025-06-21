@echo off
setlocal

title Login to Instagram for Scraper

echo =================================================================
echo  Instagram Login Helper
echo =================================================================
echo.
echo  This script will open a Chrome window where you can log in to Instagram.
echo  Once you log in, the credentials will be saved in a special profile used
echo  by the scraper.
echo.
echo  IMPORTANT: Please close all Chrome windows before proceeding to ensure
echo  a clean login session.
echo.
echo  After logging in, you can close the browser and run the scraper directly.
echo.
pause

echo.
echo  Closing any existing Chrome processes...
taskkill /f /im chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

set "PROFILE_DIR=%~dp0instagram_profile"
mkdir "%PROFILE_DIR%" 2>nul

set "CHROME_EXE="

:: Try to find Chrome in default locations
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_EXE=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_EXE=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_EXE=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
)

if not defined CHROME_EXE (
    echo.
    echo  ERROR: Could not find chrome.exe.
    echo  Please edit this file and add the correct path to your
    echo  Google Chrome installation.
    echo.
    pause
    exit /b
)

echo.
echo  Found Chrome at: "%CHROME_EXE%"
echo  Opening Chrome with a dedicated profile for Instagram...
echo  Profile directory: %PROFILE_DIR%
echo.
echo  Please log in to Instagram when the browser opens.
echo  After logging in, you can close the browser and run the scraper.
echo.

::
:: Start Chrome with the dedicated profile and open Instagram
:: Use the same flags as the scraper for compatibility
start "Chrome-Login" "%CHROME_EXE%" --user-data-dir="%PROFILE_DIR%" --no-first-run  --disable-dev-shm-usage --disable-blink-features=AutomationControlled --disable-extensions --disable-notifications --disable-gpu --disable-infobars --disable-web-security --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" https://www.instagram.com/

echo  Chrome has been launched. Please log in to Instagram.
echo  After logging in, you can close the browser and run the scraper with:
echo.
echo    python run_scraper.py
echo.
echo  You do NOT need to run start_chrome_debug.bat anymore.
echo  The scraper will use this dedicated profile automatically.
echo.

endlocal
