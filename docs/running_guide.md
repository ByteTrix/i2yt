# Running the Instagram Scraper - Quick Reference

## Overview

The i2yt Instagram scraper provides multiple ways to run, depending on your platform and preferences. This guide covers all execution methods and their use cases.

## Execution Methods

### 1. Python Command Line (Cross-Platform)

**Best for**: Developers, automation, command-line users

#### Basic Commands
```bash
# Scrape Instagram links only (fastest)
python run_scraper.py

# Extract descriptions for existing links
python run_scraper.py descriptions

# Upload videos to Google Drive for pending links  
python run_scraper.py uploads

# Run complete workflow (scraping + descriptions + uploads)
python run_scraper.py full

# Show current status and statistics
python run_scraper.py status
```

#### Advanced Options
```bash
# Verbose output for debugging
python run_scraper.py --verbose

# Custom configuration file
python run_scraper.py --config custom_config.py

# Test configuration without running
python run_scraper.py --test-config
```

### 2. PowerShell Script (Windows)

**Best for**: Windows power users, interactive selection

#### Running the Script
```powershell
# Navigate to project directory
cd "C:\path\to\your\i2yt"

# Run the interactive script
.\run_scraper.ps1
```

#### Menu Options
The PowerShell script provides an interactive menu:

1. **🔗 Scrape Instagram Links** - Collect new reel URLs and save to Google Sheets
2. **📝 Extract Descriptions** - Process existing links to extract descriptions
3. **☁️ Upload to Google Drive** - Download and upload videos for pending links
4. **🚀 Run Complete Workflow** - Execute all steps in sequence
5. **📊 Check Google Sheets Status** - View current statistics and status
6. **🧹 Clean Downloaded Files** - Remove local video files
7. **🔧 Test Google Sheets Connection** - Verify API connectivity
8. **❌ Exit** - Close the application

### 3. Windows Batch Launcher (Windows)

**Best for**: End users, one-click operation, desktop shortcuts

#### Setup Required
1. **Edit the batch file** `Launch_Instagram_Scraper.bat`
2. **Update line 11** with your project path:
   ```batch
   start wt -p "PowerShell" --title "Instagram Reel Scraper" pwsh -NoExit -ExecutionPolicy Bypass -File "C:\your\path\to\i2yt\run_scraper.ps1"
   ```
3. **Save the file**

#### Running
- Double-click `Launch_Instagram_Scraper.bat`
- Creates a new Windows Terminal window
- Runs the PowerShell interactive menu

#### Creating Desktop Shortcut
1. Right-click `Launch_Instagram_Scraper.bat`
2. Select "Create shortcut"
3. Move shortcut to desktop
4. Optionally rename to "Instagram Scraper"

## Workflow Types

### Link Collection Only
- **Command**: `python run_scraper.py`
- **Purpose**: Fastest way to collect new Instagram reel URLs
- **Output**: New entries in Google Sheets with "pending" status
- **Time**: ~2-5 minutes per Instagram account

### Description Extraction
- **Command**: `python run_scraper.py descriptions`
- **Purpose**: Extract and format descriptions for existing reels
- **Requirements**: Instagram cookies (`cookies.txt`)
- **Output**: Fills description column in Google Sheets

### Google Drive Upload
- **Command**: `python run_scraper.py uploads`
- **Purpose**: Download videos and upload to Google Drive
- **Requirements**: `UPLOAD_TO_GOOGLE_DRIVE = True` in config
- **Output**: Videos uploaded, status updated to "completed"

### Complete Workflow
- **Command**: `python run_scraper.py full`
- **Purpose**: End-to-end processing (scraping → descriptions → uploads)
- **Time**: Varies based on number of reels and processing options

## Configuration Files

### Main Configuration: `config.py`
```python
# Essential settings
INSTAGRAM_URLS = ["https://www.instagram.com/account/"]
GOOGLE_SHEETS_ID = "your-sheet-id"
TARGET_LINKS = 50
DAYS_LIMIT = 30

# Processing options
EXTRACT_DESCRIPTIONS = True
UPLOAD_TO_GOOGLE_DRIVE = False
ENABLE_CONCURRENT_PROCESSING = True
```

### Google Credentials: `credentials.json`
- Download from Google Cloud Console
- Service account with Sheets and Drive API access
- Share your Google Sheet with the service account email

### Instagram Cookies: `cookies.txt` (Optional)
- Required for description extraction
- Export from browser using extension
- NetScape cookie format

## Error Handling and Logs

### Log Files
- **Primary log**: `instagram_scraper.log`
- **Location**: Project root directory
- **Content**: All operations, errors, and status updates

### Common Exit Codes
- **0**: Success
- **1**: Configuration error
- **2**: Authentication error  
- **3**: Google API error
- **4**: Instagram access error

### Debugging
```bash
# Enable verbose output
python run_scraper.py --verbose

# Test configuration
python run_scraper.py --test-config

# Check Google API connectivity
python tests/test_sheets.py
```

## Performance Tips

### Speed Optimization
1. **Enable headless mode**: `HEADLESS = True`
2. **Use concurrent processing**: `ENABLE_CONCURRENT_PROCESSING = True`
3. **Optimize worker counts**: Adjust `MAX_*_WORKERS` settings
4. **Limit collection**: Set reasonable `TARGET_LINKS` and `DAYS_LIMIT`

### Resource Management
1. **Clean up downloads**: Enable `DELETE_LOCAL_AFTER_UPLOAD = True`
2. **Monitor memory**: Large batches may require system resources
3. **Rate limiting**: Built-in delays prevent Instagram blocking

## Scheduling Automation

### Windows Task Scheduler
1. Create new task
2. Set trigger (daily, weekly)
3. Set action: `python "C:\path\to\i2yt\run_scraper.py"`
4. Configure conditions (only if online, etc.)

### Linux/Mac Cron
```bash
# Edit crontab
crontab -e

# Run daily at 9 AM
0 9 * * * cd /path/to/i2yt && python run_scraper.py

# Run descriptions extraction hourly
0 * * * * cd /path/to/i2yt && python run_scraper.py descriptions
```

## Integration with Other Tools

### n8n Workflow
- Use the provided `n8n_workflow.json` template
- Monitors Google Sheets for new reels
- Automates YouTube upload process

### API Integration
- Google Sheets acts as the data interface
- Status columns enable external workflow triggers
- Webhook integration possible via custom modifications

---

For detailed setup instructions, see [Quick Start Guide](quick_start.md)  
For configuration options, see [Configuration Guide](configuration.md)  
For troubleshooting, see [Troubleshooting Guide](troubleshooting.md)
