# Quick Start Guide

Get up and running with Instagram to YouTube automation in under 10 minutes.

## Prerequisites

- **Python 3.8+** installed
- **Google Chrome** browser
- **Instagram account** for authentication
- **Google account** for Sheets API

## Step-by-Step Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-username/instagram-youtube-automation.git
cd instagram-youtube-automation

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Google Sheets API Setup

#### Option A: Quick Setup (Recommended)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account and download `credentials.json`
5. Place `credentials.json` in the project root

#### Option B: Detailed Setup
Follow the complete guide: [Google Sheets Setup](google_sheets_setup.md)

### 3. Configure the Project

```bash
# Copy configuration template
copy config_template.py config.py
```

Edit `config.py` with your settings:

```python
# Required: Instagram URLs to scrape
INSTAGRAM_URLS = [
    "https://www.instagram.com/your_target_account/",
    "https://www.instagram.com/another_account/"
]

# Required: Your Google Sheets ID
SPREADSHEET_ID = "1abcd1234efgh5678-your-sheet-id-here"

# Optional: Customize scraping behavior
DAYS_TO_SCRAPE = 7           # Last 7 days
MAX_REELS_PER_ACCOUNT = 20   # Limit reels per account
USE_FAST_MODE = True         # Headless mode
```

**How to get Google Sheets ID:**
1. Create a new Google Sheet
2. Share it with the email from your `credentials.json` (give Editor access)
3. Copy the ID from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`

### 4. Setup Instagram Login

```bash
# Run the login helper
login_to_instagram.bat
```

This will:
1. Open Chrome with a dedicated profile
2. Navigate to Instagram
3. **You manually log in** to your Instagram account
4. **Close the browser** when done - your session is saved

### 5. Run Your First Scrape

```bash
# Basic run
python run_scraper.py

# Or with options
python run_scraper.py --fast --days 3 --limit 10
```

## What Happens Next

1. **Chrome opens** (or runs headless in fast mode)
2. **Loads your saved Instagram session**
3. **Navigates to each account** in your URL list
4. **Scrolls and collects reel links** from the last N days
5. **Saves to Google Sheets** with proper formatting
6. **Creates local backup** in JSON format
7. **Shows summary** of collected reels

## Verify Success

### Check Google Sheets
Your sheet should have these columns filled:
- **Date**: Reel posting date
- **Instagram Username**: Account handle
- **Link**: Direct reel URL
- **Reel ID**: Unique identifier
- **Status**: Dropdown (defaults to "Not Processed")
- **YT Posted Date**: Empty (for n8n workflow)

### Check Logs
Look for:
```
2024-12-19 10:30:15 - INFO - Starting Instagram scraper...
2024-12-19 10:30:20 - INFO - Logged into Chrome profile successfully
2024-12-19 10:30:25 - INFO - Processing: https://www.instagram.com/account1/
2024-12-19 10:30:45 - INFO - Found 15 new reels from last 7 days
2024-12-19 10:30:50 - INFO - Saved 15 reels to Google Sheets
2024-12-19 10:30:55 - INFO - Scraping completed successfully!
```

## Common Quick Fixes

| Problem | Quick Solution |
|---------|----------------|
| "Chrome won't start" | Install Chrome, check PATH |
| "No credentials.json" | Download from Google Cloud Console |
| "Sheet permission denied" | Share sheet with service account email |
| "Instagram login failed" | Re-run `login_to_instagram.bat` |
| "No reels found" | Check account privacy settings |

## Next Steps

- **Automation**: Set up [n8n Integration](n8n_integration.md) for YouTube uploads
- **Customization**: Read [Configuration Guide](configuration.md) for advanced options
- **Troubleshooting**: Check [Troubleshooting Guide](troubleshooting.md) for detailed solutions
- **Scheduling**: Use Windows Task Scheduler or cron for regular runs

## Command Reference

```bash
# Basic usage
python run_scraper.py

# Fast mode (headless)
python run_scraper.py --fast

# Limit time range
python run_scraper.py --days 3

# Limit reels per account
python run_scraper.py --limit 10

# Verbose logging
python run_scraper.py --verbose

# Skip Google Sheets upload (local only)
python run_scraper.py --no-upload

# Help
python run_scraper.py --help
```

---

**🎉 Congratulations!** You're now collecting Instagram reels automatically. 

Need help? Check the [Troubleshooting Guide](troubleshooting.md) or create an issue on GitHub.
