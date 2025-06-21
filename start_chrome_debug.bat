@echo off
setlocal

title Start Chrome for Scraper

echo =================================================================
echo  Starting Chrome with Remote Debugging for Scraper
echo =================================================================
echo.
echo  This script will start Google Chrome with a remote debugging
echo  port open, which allows the scraper to connect to it.
echo.
echo  IMPORTANT: For this to work, you MUST close all other
echo  Google Chrome windows before you continue.
echo.
pause

set "CHROME_EXE="
set "USER_DATA_DIR=%LOCALAPPDATA%\Google\Chrome\User Data"

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

if not exist "%USER_DATA_DIR%" (
    echo.
    echo  ERROR: Could not find the default Chrome profile directory at:
    echo  %USER_DATA_DIR%
    echo.
    echo  If your profile is in a different location, please edit this script.
    echo.
    pause
    exit /b
)


echo.
echo  Found Chrome at: "%CHROME_EXE%"
echo  Launching Chrome with remote debugging on port 9223...
echo  Using profile: Default
echo.

:: This will launch chrome with your default user profile
start "Chrome-Debug" "%CHROME_EXE%" --remote-debugging-port=9223 --user-data-dir="%USER_DATA_DIR%" --profile-directory="Default"

echo  Chrome has been launched. You can now run the scraper script.
echo  You can minimize this window.
echo.

endlocal
