# Google Sheets Setup Guide

Complete guide to setting up Google Sheets API for the Instagram to YouTube automation tool.

## Overview

The automation tool uses Google Sheets API to store and manage scraped Instagram reel data. This guide will walk you through setting up the necessary API credentials and configuring your Google Sheet.

## Prerequisites

- **Google Account** (Gmail, Google Workspace, etc.)
- **Google Chrome** browser (for easier navigation)
- **Basic understanding** of Google Cloud Console

## Step-by-Step Setup

### Phase 1: Google Cloud Project Setup

#### 1. Create or Select a Project

1. **Navigate** to [Google Cloud Console](https://console.cloud.google.com/)
2. **Sign in** with your Google account
3. **Create a new project** or select an existing one:
   - Click the project dropdown (top left)
   - Click "New Project"
   - Enter project name: `Instagram YouTube Automation`
   - Click "Create"

#### 2. Enable Required APIs

1. **Navigate** to "APIs & Services" > "Library"
2. **Search and enable** the following APIs:
   - **Google Sheets API**
   - **Google Drive API**

For each API:
1. Click on the API name
2. Click "Enable"
3. Wait for activation (usually instant)

### Phase 2: Service Account Creation

#### 1. Create Service Account

1. **Navigate** to "APIs & Services" > "Credentials"
2. **Click** "Create Credentials" > "Service Account"
3. **Fill in details**:
   - **Service account name**: `instagram-scraper-service`
   - **Service account ID**: `instagram-scraper-service` (auto-filled)
   - **Description**: `Service account for Instagram reel scraping automation`
4. **Click** "Create and Continue"

#### 2. Grant Permissions (Optional)

- **Skip this step** for basic usage
- **Click** "Continue" (no roles needed for this use case)
- **Click** "Done"

#### 3. Generate Credentials

1. **Find your service account** in the credentials list
2. **Click on the service account email**
3. **Navigate** to the "Keys" tab
4. **Click** "Add Key" > "Create new key"
5. **Select** "JSON" format
6. **Click** "Create"
7. **Download** the JSON file
8. **Rename** it to `credentials.json`
9. **Move** it to your project root directory

### Phase 3: Google Sheet Setup

#### 1. Create Your Google Sheet

1. **Go to** [Google Sheets](https://sheets.google.com)
2. **Click** "Create" > "Blank spreadsheet"
3. **Rename** the sheet to something meaningful: `Instagram Reels Database`
4. **Note the Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
   ```

#### 2. Share Sheet with Service Account

1. **Click** "Share" button (top right)
2. **Enter the service account email** from your `credentials.json`:
   ```
   instagram-scraper-service@your-project-id.iam.gserviceaccount.com
   ```
3. **Set permission** to "Editor"
4. **Uncheck** "Notify people" (it's a service account)
5. **Click** "Share"

#### 3. Configure Sheet Structure (Optional)

The tool will automatically create headers, but you can set them up manually:

| Column A | Column B | Column C | Column D | Column E | Column F |
|----------|----------|----------|----------|----------|----------|
| Date | Instagram Username | Link | Reel ID | Status | YT Posted Date |

### Phase 4: Configuration Integration

#### 1. Update Configuration File

Edit your `config.py` file:

```python
# Google Sheets configuration
SPREADSHEET_ID = "1abc123def456ghi789jkl-your-actual-sheet-id"
WORKSHEET_NAME = "Sheet1"  # Or your custom sheet name
CREDENTIALS_FILE = "credentials.json"

# Optional: Customize column names
COLUMN_NAMES = {
    'date': 'Date',
    'username': 'Instagram Username', 
    'link': 'Link',
    'reel_id': 'Reel ID',
    'status': 'Status',
    'yt_date': 'YT Posted Date'
}
```

#### 2. Test the Connection

Run the test script to verify everything works:

```bash
# Test Google Sheets connection
python tests/test_google_api.py

# Test sheet writing
python tests/test_sheets.py
```

Expected output:
```
✓ Credentials loaded successfully
✓ Google Sheets API connection established
✓ Spreadsheet accessible
✓ Write permissions confirmed
✓ Test data written and read successfully
```

## Advanced Configuration

### Multiple Worksheets

If you want to organize data across multiple sheets:

```python
# Configuration for multiple worksheets
WORKSHEETS = {
    'main': 'Instagram Reels',
    'archive': 'Processed Reels',
    'errors': 'Failed Reels'
}

# Use different sheets for different purposes
MAIN_WORKSHEET = "Instagram Reels"
ARCHIVE_WORKSHEET = "Processed Reels"
ERROR_WORKSHEET = "Failed Reels"
```

### Custom Column Configuration

```python
# Customize column structure
CUSTOM_COLUMNS = [
    {'name': 'Date', 'type': 'date'},
    {'name': 'Account', 'type': 'text'},
    {'name': 'Reel URL', 'type': 'url'},
    {'name': 'Reel ID', 'type': 'text'},
    {'name': 'Status', 'type': 'dropdown'},
    {'name': 'YouTube Date', 'type': 'date'},
    {'name': 'Views', 'type': 'number'},
    {'name': 'Notes', 'type': 'text'}
]

# Status dropdown options
STATUS_OPTIONS = [
    "Not Processed",
    "Downloaded",
    "Uploaded to YT", 
    "Failed",
    "Skipped",
    "Manual Review"
]
```

### Formatting and Validation

```python
# Sheet formatting options
SHEET_FORMATTING = {
    'freeze_header': True,
    'auto_resize': True,
    'apply_filters': True,
    'bold_headers': True,
    'date_format': 'dd-mmm-yyyy',
    'url_format': True
}

# Data validation
DATA_VALIDATION = {
    'status_dropdown': True,
    'date_validation': True,
    'url_validation': True,
    'required_fields': ['Date', 'Link', 'Reel ID']
}
```

## Security and Best Practices

### Credential Security

1. **Never commit** `credentials.json` to version control
2. **Add to .gitignore**:
   ```gitignore
   credentials.json
   config.py
   *.log
   ```
3. **Use environment variables** in production:
   ```python
   import os
   import json
   
   # Load credentials from environment
   if os.getenv('GOOGLE_CREDENTIALS'):
       credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
   else:
       with open('credentials.json') as f:
           credentials_info = json.load(f)
   ```

### Access Control

1. **Limit service account permissions**:
   - Only grant access to specific sheets
   - Use read-only access where possible
   - Regularly audit permissions

2. **Monitor usage**:
   - Check Google Cloud Console for API usage
   - Set up billing alerts
   - Monitor for unusual activity

### Backup Strategy

```python
# Enable automatic backups
BACKUP_CONFIG = {
    'enable_local_backup': True,
    'backup_format': 'json',
    'backup_frequency': 'daily',
    'backup_location': './backups/',
    'max_backup_files': 30
}
```

## Troubleshooting

### Common Setup Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Credentials not found" | Missing credentials.json | Download from Google Cloud Console |
| "Permission denied" | Sheet not shared | Share with service account email |
| "API not enabled" | Missing API activation | Enable Sheets & Drive APIs |
| "Invalid spreadsheet ID" | Wrong ID format | Copy from sheet URL |
| "Quota exceeded" | Too many requests | Add delays, check quotas |

### API Quotas and Limits

**Google Sheets API Limits:**
- **100 requests per 100 seconds per user**
- **300 requests per 60 seconds**
- **Batch requests**: Up to 100 operations

**Optimization strategies:**
```python
# Batch operations
BATCH_SIZE = 50  # Write multiple rows at once
USE_BATCH_UPDATE = True

# Rate limiting
REQUEST_DELAY = 1  # Seconds between requests
RESPECT_QUOTAS = True

# Efficient data handling
UPDATE_ONLY_NEW = True  # Skip existing data
USE_APPEND_ONLY = True  # Don't scan existing rows
```

### Debug Mode

Enable detailed debugging:

```python
# Debug configuration
DEBUG_SHEETS = True
LOG_API_CALLS = True
SAVE_API_RESPONSES = True
VERBOSE_ERRORS = True
```

### Testing Your Setup

Create a test script:

```python
# test_complete_setup.py
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def test_complete_setup():
    try:
        # Test 1: Load credentials
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        print("✓ Credentials file loaded")
        
        # Test 2: Create service
        credentials = Credentials.from_service_account_file('credentials.json')
        service = build('sheets', 'v4', credentials=credentials)
        print("✓ Google Sheets service created")
        
        # Test 3: Access spreadsheet
        sheet_id = "YOUR_SPREADSHEET_ID_HERE"
        result = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        print(f"✓ Spreadsheet accessed: {result['properties']['title']}")
        
        # Test 4: Write test data
        test_data = [['Test Date', 'Test User', 'Test Link', 'Test ID', 'Test Status']]
        body = {'values': test_data}
        
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range='A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        print("✓ Test data written successfully")
        
        print("\n🎉 Complete setup test passed!")
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")

if __name__ == "__main__":
    test_complete_setup()
```

## Production Deployment

### Environment Variables

For production deployment:

```bash
# Set environment variables
export GOOGLE_CREDENTIALS='{"type": "service_account", ...}'
export SPREADSHEET_ID="your_sheet_id"
export WORKSHEET_NAME="Instagram Reels"
```

### Docker Configuration

```dockerfile
# Dockerfile snippet
COPY credentials.json /app/
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Setup Google Credentials
  env:
    GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
  run: echo "$GOOGLE_CREDENTIALS" > credentials.json
```

---

**Next Steps:**
- [Configuration Guide](configuration.md) - Customize scraper behavior
- [Quick Start Guide](quick_start.md) - Run your first scrape
- [Troubleshooting](troubleshooting.md) - Solve common issues
