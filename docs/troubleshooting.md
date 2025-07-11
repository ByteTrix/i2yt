# Troubleshooting Guide

Comprehensive troubleshooting guide for the Instagram to YouTube automation tool.

## Quick Diagnosis

Run the built-in diagnostic tool first:

```bash
# Run diagnostics
python tests/test_google_api.py
python tests/test_sheets.py

# Check configuration
python run_scraper.py --test-config

# Verbose run for debugging
python run_scraper.py --verbose --debug
```

## Common Issues by Category

### 0. Windows Launcher Issues

#### Batch File Path Errors

**Problem**: "The system cannot find the file specified" when running `Launch_Instagram_Scraper.bat`
```
[error 2147942402 (0x80070002) when launching `".\run_scraper.ps1"`]
The system cannot find the file specified.
```

**Solutions**:

1. **Update the Batch File Path**:
   - Open `Launch_Instagram_Scraper.bat` in a text editor
   - Find line 11 with the hardcoded path:
     ```batch
     start wt -p "PowerShell" --title "Instagram Reel Scraper" pwsh -NoExit -ExecutionPolicy Bypass -File "d:\Kodo\i2yt\run_scraper.ps1"
     ```
   - Replace `"d:\Kodo\i2yt\run_scraper.ps1"` with your actual project path:
     ```batch
     start wt -p "PowerShell" --title "Instagram Reel Scraper" pwsh -NoExit -ExecutionPolicy Bypass -File "C:\Users\YourName\Documents\i2yt\run_scraper.ps1"
     ```

2. **Alternative: Use Relative Path**:
   - Place the batch file in your project directory
   - Use this command instead:
     ```batch
     start wt -p "PowerShell" --title "Instagram Reel Scraper" pwsh -NoExit -ExecutionPolicy Bypass -Command "Set-Location '%~dp0'; .\run_scraper.ps1"
     ```

#### PowerShell Execution Policy Issues

**Problem**: PowerShell script blocked by execution policy
```
cannot be loaded because running scripts is disabled on this system
```

**Solutions**:
```powershell
# Temporarily allow script execution (Administrator PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass (safer)
pwsh -ExecutionPolicy Bypass -File ".\run_scraper.ps1"
```

#### Windows Terminal Not Found

**Problem**: `wt` command not recognized
```
'wt' is not recognized as an internal or external command
```

**Solutions**:
1. **Install Windows Terminal**:
   ```powershell
   # Via Microsoft Store
   # Search for "Windows Terminal" and install
   
   # Via winget
   winget install Microsoft.WindowsTerminal
   ```

2. **Alternative: Use regular PowerShell**:
   - Modify the batch file to use regular PowerShell:
     ```batch
     start powershell -NoExit -ExecutionPolicy Bypass -File "C:\your\path\to\run_scraper.ps1"
     ```

### 1. Installation and Setup Issues

#### Python Dependencies

**Problem**: `ModuleNotFoundError` or import errors
```
ModuleNotFoundError: No module named 'selenium'
```

**Solutions**:
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Use virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Update pip
python -m pip install --upgrade pip
```

#### Chrome Installation Issues

**Problem**: Chrome binary not found
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solutions**:
```bash
# Windows: Install Chrome
winget install Google.Chrome

# Linux: Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install google-chrome-stable

# Mac: Install Chrome
brew install --cask google-chrome
```

**Manual Path Configuration**:
```python
# In config.py
CHROME_BINARY_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Windows
CHROME_BINARY_PATH = "/usr/bin/google-chrome"  # Linux
CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Mac
```

### 2. Authentication and Login Issues

#### Instagram Login Problems

**Problem**: Can't log into Instagram
```
Login failed: Please check your credentials
```

**Solutions**:

1. **Clear Profile and Re-login**:
   ```bash
   # Remove existing profile
   rmdir /s instagram_profile  # Windows
   rm -rf instagram_profile    # Linux/Mac
   
   # Re-run login
   login_to_instagram.bat
   ```

2. **Manual Profile Setup**:
   ```bash
   # Use the login helper script
   login_to_instagram.bat
   
   # Or start Chrome manually with profile
   # Navigate to instagram.com
   # Log in manually
   # Close browser
   ```

3. **Check Account Status**:
   - Verify account isn't suspended
   - Check for 2FA requirements
   - Ensure account isn't rate-limited

#### Two-Factor Authentication (2FA)

**Problem**: 2FA blocking automation
```
Two-factor authentication required
```

**Solutions**:

1. **App Passwords** (if available):
   - Generate app-specific password
   - Use instead of main password

2. **Trusted Device Setup**:
   ```bash
   # Login manually first
   login_to_instagram.bat
   # Complete 2FA process
   # Mark device as trusted
   ```

3. **Disable 2FA** (temporarily, not recommended):
   - Only for dedicated automation accounts
   - Re-enable after profile setup

### 3. Google Sheets API Issues

#### Credentials Problems

**Problem**: Authentication failed
```
google.auth.exceptions.DefaultCredentialsError: File credentials.json was not found
```

**Solutions**:

1. **Check File Location**:
   ```bash
   # Verify file exists
   dir credentials.json  # Windows
   ls -la credentials.json  # Linux/Mac
   ```

2. **Regenerate Credentials**:
   - Go to Google Cloud Console
   - Create new service account key
   - Download fresh credentials.json

3. **Verify File Format**:
   ```python
   # Test credentials loading
   import json
   with open('credentials.json', 'r') as f:
       creds = json.load(f)
   print("Service account email:", creds['client_email'])
   ```

#### Permission Errors

**Problem**: Access denied to spreadsheet
```
googleapiclient.errors.HttpError: 403 The caller does not have permission
```

**Solutions**:

1. **Share Spreadsheet**:
   - Open Google Sheet
   - Click "Share"
   - Add service account email (from credentials.json)
   - Set permission to "Editor"

2. **Check Spreadsheet ID**:
   ```python
   # Verify ID format
   SPREADSHEET_ID = "1abc123def456ghi789jkl0mnop"  # Should be long string
   ```

3. **Test API Access**:
   ```python
   # Quick test script
   from googleapiclient.discovery import build
   from google.oauth2.service_account import Credentials
   
   credentials = Credentials.from_service_account_file('credentials.json')
   service = build('sheets', 'v4', credentials=credentials)
   
   # Test read access
   result = service.spreadsheets().get(spreadsheetId='YOUR_ID').execute()
   print("Sheet title:", result['properties']['title'])
   ```

#### Quota Exceeded

**Problem**: API quota limits reached
```
googleapiclient.errors.HttpError: 429 Quota exceeded
```

**Solutions**:

1. **Add Rate Limiting**:
   ```python
   # In config.py
   REQUEST_DELAY = 2  # Seconds between requests
   BATCH_SIZE = 10    # Smaller batches
   USE_EXPONENTIAL_BACKOFF = True
   ```

2. **Optimize Batch Operations**:
   ```python
   # Use batch updates instead of individual writes
   ENABLE_BATCH_UPDATES = True
   BATCH_UPDATE_SIZE = 50
   ```

3. **Monitor Quotas**:
   - Check Google Cloud Console quota usage
   - Request quota increase if needed

### 4. Google Drive API Issues

#### Service Account Storage Quota Error

**Problem**: Service accounts don't have storage quota
```
HttpError 403: Service Accounts do not have storage quota. Leverage shared drives 
(https://developers.google.com/workspace/drive/api/guides/about-shareddrives), 
or use OAuth delegation instead.
```

**Root Cause**: Service accounts cannot upload files to their own Google Drive because they don't have allocated storage space.

**Solutions**:

1. **Use Shared Drive (Recommended)**:
   ```python
   # In config.py
   USE_SHARED_DRIVE = True
   SHARED_DRIVE_ID = "your_shared_drive_id"  # Get this from shared drive URL
   DRIVE_FOLDER_ID = "folder_id_in_shared_drive"
   ```
   
   Setup steps:
   - Create a Shared Drive (Google Workspace accounts only)
   - Add your service account as a member with "Content Manager" role
   - Create a folder in the shared drive for uploads
   - Use the folder ID in your config

2. **Share Regular Drive Folder with Service Account**:
   ```python
   # In config.py
   USE_SHARED_DRIVE = False
   DRIVE_FOLDER_ID = "your_personal_folder_id"
   ```
   
   Setup steps:
   - Create a folder in your personal Google Drive
   - Right-click → Share
   - Add your service account email with "Editor" permissions
   - Use this folder ID in your config

3. **Use OAuth (User Authentication)**:
   ```python
   # In config.py
   USE_OAUTH_INSTEAD_OF_SERVICE_ACCOUNT = True
   OAUTH_CREDENTIALS_FILE = "oauth_credentials.json"
   ```
   
   This requires user interaction for initial authentication but provides access to user's storage quota.

4. **Disable Google Drive Upload (Temporary)**:
   ```python
   # In config.py
   UPLOAD_TO_GOOGLE_DRIVE = False
   # Files will be downloaded locally only
   ```

#### Folder Not Found Error

**Problem**: Cannot access specified folder
```
HttpError 404: File not found
```

**Solutions**:

1. **Verify Folder ID**:
   - Copy folder ID from Google Drive URL
   - Ensure folder is shared with service account
   - Test folder access with direct API call

2. **Check Permissions**:
   - Service account needs "Editor" or "Content Manager" role
   - Folder must be explicitly shared, inheritance isn't always sufficient

#### Upload Timeout Issues

**Problem**: Large file uploads failing
```
socket.timeout: The read operation timed out
```

**Solutions**:

1. **Increase Timeouts**:
   ```python
   # In config.py
   UPLOAD_TIMEOUT = 300  # 5 minutes for large files
   UPLOAD_RETRY_ATTEMPTS = 3
   RESUMABLE_UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB chunks
   ```

2. **Enable Resumable Uploads**:
   ```python
   USE_RESUMABLE_UPLOAD = True
   UPLOAD_CHUNK_SIZE = 262144  # 256KB chunks for better reliability
   ```

### 5. Browser and Selenium Issues

#### Browser Crashes

**Problem**: Chrome crashes during scraping
```
selenium.common.exceptions.WebDriverException: chrome not reachable
```

**Solutions**:

1. **Increase Memory**:
   ```python
   # In config.py
   CHROME_OPTIONS = [
       "--no-sandbox",
       "--disable-dev-shm-usage",
       "--disable-gpu",
       "--memory-pressure-off"
   ]
   ```

2. **Reduce Resource Usage**:
   ```python
   ENABLE_IMAGES = False
   USE_FAST_MODE = True
   MAX_SCROLLS = 10  # Reduce from default
   ```

3. **Enable Headless Mode**:
   ```python
   HEADLESS_MODE = True
   USE_FAST_MODE = True
   ```

#### Element Not Found Errors

**Problem**: Can't find Instagram elements
```
selenium.common.exceptions.NoSuchElementException: Unable to locate element
```

**Solutions**:

1. **Increase Timeouts**:
   ```python
   # In config.py
   PAGE_LOAD_TIMEOUT = 60
   ELEMENT_TIMEOUT = 30
   SCROLL_PAUSE_TIME = 3
   ```

2. **Update Element Selectors**:
   ```python
   # Check for Instagram layout changes
   # Update selectors in scraper code
   REEL_SELECTOR = 'a[href*="/reel/"]'  # Current selector
   ```

3. **Wait for Page Load**:
   ```python
   # Add explicit waits
   WAIT_FOR_CONTENT = True
   CONTENT_LOAD_TIMEOUT = 15
   ```

#### Profile Corruption

**Problem**: Chrome profile gets corrupted
```
Profile appears to be in use by another process
```

**Solutions**:

1. **Clear Profile**:
   ```bash
   # Kill Chrome processes
   taskkill /f /im chrome.exe  # Windows
   pkill chrome                # Linux/Mac
   
   # Remove profile
   rmdir /s instagram_profile  # Windows
   rm -rf instagram_profile    # Linux/Mac
   ```

2. **Use Temporary Profiles**:
   ```python
   # In config.py
   USE_TEMP_PROFILE = True
   CLEAN_PROFILE_ON_EXIT = True
   ```

### 6. Performance Issues

#### Slow Scraping

**Problem**: Scraping takes too long
```
INFO: Scraping taking longer than expected
```

**Solutions**:

1. **Enable Fast Mode**:
   ```python
   # In config.py
   USE_FAST_MODE = True
   HEADLESS_MODE = True
   ENABLE_IMAGES = False
   ```

2. **Optimize Scrolling**:
   ```python
   SCROLL_PAUSE_TIME = 1  # Faster scrolling
   MAX_SCROLLS = 10       # Fewer scrolls
   FAST_SCROLL_COUNT = 8  # More initial fast scrolls
   ```

3. **Reduce Load**:
   ```python
   MAX_REELS_PER_ACCOUNT = 20  # Limit collection
   DAYS_TO_SCRAPE = 7          # Recent only
   ```

#### Memory Issues

**Problem**: High memory usage or crashes
```
MemoryError: Unable to allocate memory
```

**Solutions**:

1. **Process in Batches**:
   ```python
   BATCH_SIZE = 10
   PROCESS_ACCOUNTS_INDIVIDUALLY = True
   ```

2. **Clear Memory**:
   ```python
   RESTART_BROWSER_FREQUENCY = 50  # Restart every N reels
   GARBAGE_COLLECT_FREQUENCY = 25
   ```

3. **Reduce Chrome Memory**:
   ```python
   CHROME_OPTIONS = [
       "--memory-pressure-off",
       "--max_old_space_size=2048",
       "--disable-background-mode"
   ]
   ```

## Debug Mode and Logging

### Enable Comprehensive Debugging

```python
# In config.py
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
SAVE_SCREENSHOTS = True
PRESERVE_BROWSER = True
LOG_TO_CONSOLE = True
VERBOSE_ERRORS = True

# Detailed logging
LOG_API_CALLS = True
LOG_BROWSER_ACTIONS = True
LOG_DATA_PROCESSING = True
```

### Log Analysis

Check log files for patterns:

```bash
# Search for errors
findstr "ERROR" instagram_scraper.log  # Windows
grep "ERROR" instagram_scraper.log     # Linux/Mac

# Check specific issues
findstr "timeout" instagram_scraper.log
grep -i "permission" instagram_scraper.log
```

### Screenshot Debugging

When enabled, screenshots are saved to help debug issues:
- `error_screenshot_*.png` - Screenshots when errors occur
- `page_screenshot_*.png` - Screenshots during processing

## Environment-Specific Issues

### Windows Issues

**Problem**: Path and encoding issues
```
UnicodeDecodeError: 'charmap' codec can't decode
```

**Solutions**:
```python
# Set UTF-8 encoding
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Use raw strings for paths
CHROME_PROFILE_PATH = r".\instagram_profile"
```

### Linux/Docker Issues

**Problem**: Display and permissions
```
selenium.common.exceptions.WebDriverException: unknown error: Chrome failed to start
```

**Solutions**:
```bash
# Install dependencies
apt-get update && apt-get install -y \
    chromium-browser \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3

# Use headless mode
HEADLESS_MODE = True
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--remote-debugging-port=9222"
]
```

### MacOS Issues

**Problem**: Security restrictions
```
chrome cannot be opened because the developer cannot be verified
```

**Solutions**:
```bash
# Allow Chrome in Security settings
# Or use Homebrew version
brew install --cask google-chrome

# Set correct path
CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

## Recovery Procedures

### Complete Reset

If everything fails, start fresh:

```bash
# 1. Backup important data
copy instagram_scraper.log backup_log.txt
copy config.py backup_config.py

# 2. Clean installation
rmdir /s instagram_profile
del credentials.json
pip uninstall -r requirements.txt -y

# 3. Reinstall
pip install -r requirements.txt

# 4. Reconfigure
copy config_template.py config.py
# Edit config.py with your settings

# 5. New credentials
# Download fresh credentials.json from Google Cloud

# 6. Fresh login
login_to_instagram.bat
```

### Partial Recovery

For specific issues:

```bash
# Browser issues only
rmdir /s instagram_profile
login_to_instagram.bat

# API issues only
del credentials.json
# Download new credentials.json

# Configuration issues only
copy config_template.py config.py
# Reconfigure settings
```

## Getting Help

### Before Asking for Help

1. **Run diagnostics**:
   ```bash
   python tests/test_google_api.py
   python tests/test_sheets.py
   python run_scraper.py --test-config
   ```

2. **Check logs**:
   ```bash
   tail -50 instagram_scraper.log
   ```

3. **Try safe mode**:
   ```bash
   python run_scraper.py --safe-mode --verbose
   ```

### What to Include in Bug Reports

- **Operating System** and version
- **Python version** (`python --version`)
- **Chrome version** (`chrome --version`)
- **Error message** (full traceback)
- **Log file** (last 50 lines)
- **Configuration** (without sensitive data)
- **Steps to reproduce**

### Support Channels

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For general questions
- **Documentation**: Check all docs/ files first
- **Community**: Join community forums or Discord

---

**Still having issues?** Create a detailed issue report on GitHub with the information above.
