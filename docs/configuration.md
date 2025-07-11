# Configuration Guide

Complete guide to configuring the Instagram to YouTube automation tool for optimal performance and customization.

## Configuration File Overview

The main configuration is stored in `config.py`, which you create from `config_template.py`. This file contains all the settings that control how the scraper behaves.

## Basic Configuration

### Required Settings

```python
# Instagram URLs to scrape (REQUIRED)
INSTAGRAM_URLS = [
    "https://www.instagram.com/account1/",
    "https://www.instagram.com/account2/",
    "https://www.instagram.com/account3/"
]

# Google Sheets configuration (REQUIRED)
GOOGLE_SHEETS_ID = "1abcd1234efgh5678ijklmnop-your-sheet-id"
CREDENTIALS_FILE = "credentials.json"  # Google API credentials

# Scraping limits and performance
TARGET_LINKS = 50                    # Number of reels per URL (0 = unlimited)
DAYS_LIMIT = 30                      # Only collect reels from last N days
```

### Basic Scraping Settings

```python
# Performance and timing
SCROLL_DELAY = 0.5                   # Delay between scrolls (seconds)
IMPLICIT_WAIT = 5                    # Browser element wait time (seconds)
PAGE_LOAD_TIMEOUT = 20               # Maximum page load time (seconds)
HEADLESS = False                     # False = visible browser, True = hidden
FAST_MODE = True                     # Enable performance optimizations

# Collection behavior
MAX_SCROLLS = 15                     # Maximum page scrolls per Instagram URL
BATCH_SIZE = 25                      # Save to Google Sheets every N links

# Processing options
EXTRACT_DESCRIPTIONS = True          # Extract and format reel descriptions
UPLOAD_TO_GOOGLE_DRIVE = False       # Enable Google Drive video uploads
ENABLE_CONCURRENT_PROCESSING = True  # Use parallel processing for speed
```

## Advanced Configuration

### Parallel Processing Configuration

```python
# Advanced Parallel Processing Settings
MAX_SCRAPING_WORKERS = 4             # Concurrent threads for link processing
MAX_DOWNLOAD_WORKERS = 3             # Concurrent download threads  
MAX_UPLOAD_WORKERS = 2               # Concurrent upload threads (be conservative)
MAX_DESCRIPTION_WORKERS = 5          # Concurrent description extraction threads
BATCH_PROCESSING_SIZE = 20           # Items per batch for parallel operations
WORKER_TIMEOUT = 60                  # Timeout per worker task (seconds)

# Download Configuration
DOWNLOAD_DIRECTORY = "downloaded_reels"  # Local storage directory
DOWNLOAD_TIMEOUT = 30                # Download timeout per file (seconds)
RETRY_FAILED_DOWNLOADS = 2           # Number of retry attempts for failures
DELETE_LOCAL_AFTER_UPLOAD = True     # Clean up local files post-upload
```

### Google Drive Integration

```python
# Google Drive settings
UPLOAD_TO_GOOGLE_DRIVE = False       # Set to True to enable video uploads
DRIVE_FOLDER_ID = ""                 # Google Drive folder ID (empty = root)
DRIVE_CREDENTIALS_FILE = "credentials.json"  # Service account credentials

# Advanced Google Drive settings
USE_SHARED_DRIVE = False             # Set to True if using Google Workspace Shared Drive
SHARED_DRIVE_ID = ""                 # Required if USE_SHARED_DRIVE = True
UPLOAD_TIMEOUT = 300                 # Upload timeout in seconds (5 minutes)
UPLOAD_RETRY_ATTEMPTS = 3            # Number of retry attempts for failed uploads
USE_RESUMABLE_UPLOAD = True          # Enable resumable uploads for large files
UPLOAD_CHUNK_SIZE = 262144           # Upload chunk size (256KB)
```

**Important Notes:**
- **Service Account Limitation**: Service accounts don't have storage quota and cannot upload to their own Drive
- **Shared Drive Solution**: Use Google Workspace Shared Drives for service account uploads
- **Personal Drive Alternative**: Share a personal folder with your service account email (Editor permissions)
- **OAuth Alternative**: Use user authentication instead of service accounts for personal Drive access

### Chrome Browser Settings

```python
# Chrome profile and behavior
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
BROWSER_DEBUG_PORT = 9222            # Chrome debug port for troubleshooting

# Browser optimization
ENABLE_IMAGES = False      # Load images (False = faster) - if supported
ENABLE_JAVASCRIPT = True   # Enable JS (required for Instagram)
```

### Scrolling and Collection Behavior

```python
# Scrolling configuration
SCROLL_PAUSE_TIME = 2      # Seconds between scrolls
SCROLL_ATTEMPTS = 3        # Retry failed scrolls
FAST_SCROLL_COUNT = 5      # Number of fast initial scrolls

# Content detection
REEL_LINK_PATTERN = r'/reel/[A-Za-z0-9_-]+'  # Regex for reel URLs
USERNAME_EXTRACTION = True  # Extract username from URLs
DATE_EXTRACTION = True      # Try to extract posting dates
```

### Logging and Debugging

```python
# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "instagram_scraper.log"
LOG_TO_CONSOLE = True
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Debug options
SAVE_SCREENSHOTS = False   # Save screenshots on errors
DEBUG_MODE = False         # Enable detailed debugging
PRESERVE_BROWSER = False   # Keep browser open after completion
```

### Backup and Storage

```python
# Local backup settings
ENABLE_BACKUP = True
BACKUP_FILE = "instagram_reels_backup.json"
BACKUP_FORMAT = "json"  # json, csv
BACKUP_FREQUENCY = "daily"  # always, daily, weekly

# Data processing
REMOVE_DUPLICATES = True
SORT_BY_DATE = True
INCLUDE_METADATA = True
```

## Environment-Specific Configurations

### Windows Configuration

```python
# Windows-specific settings
CHROME_PROFILE_PATH = r".\instagram_profile"
CHROME_BINARY_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Windows batch files
LOGIN_SCRIPT = "login_to_instagram.bat"
```

### Linux/Mac Configuration

```python
# Unix-specific settings
CHROME_PROFILE_PATH = "./instagram_profile"
CHROME_BINARY_PATH = "/usr/bin/google-chrome"  # or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Unix shell scripts (if using)
LOGIN_SCRIPT = "login_to_instagram.sh"
```

### Docker Configuration

```python
# Docker/containerized environment
HEADLESS_MODE = True  # Always headless in containers
CHROME_PROFILE_PATH = "/app/profile"
CHROME_BINARY_PATH = "/usr/bin/google-chrome"

# Container-specific options
ENABLE_SHARDING = True  # Disable Chrome's process isolation
NO_SANDBOX = True       # Required in most containers
DISABLE_DEV_SHM = True  # Use /tmp instead of /dev/shm
```

## Performance Optimization

### High-Performance Settings

```python
# Optimized for speed
USE_FAST_MODE = True
HEADLESS_MODE = True
ENABLE_IMAGES = False
BATCH_SIZE = 50
MAX_SCROLLS = 10
SCROLL_PAUSE_TIME = 1

# Chrome performance flags
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-features=VizDisplayCompositor",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",  # Only if Instagram works without it
]
```

### Stability-Focused Settings

```python
# Optimized for reliability
USE_FAST_MODE = False
HEADLESS_MODE = False
ENABLE_IMAGES = True
BATCH_SIZE = 10
MAX_SCROLLS = 20
SCROLL_PAUSE_TIME = 3
PAGE_LOAD_TIMEOUT = 60
ELEMENT_TIMEOUT = 30

# Error handling
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5
SAVE_SCREENSHOTS = True
```

## Google Sheets Configuration

### Basic Sheets Settings

```python
# Sheet structure
SPREADSHEET_ID = "your_sheet_id"
WORKSHEET_NAME = "Instagram Reels"
CREATE_WORKSHEET = True  # Create if doesn't exist

# Column configuration
COLUMNS = [
    "Date",
    "Instagram Username", 
    "Link",
    "Reel ID",
    "Status",
    "YT Posted Date"
]

# Data validation
ENABLE_DROPDOWN = True
STATUS_OPTIONS = [
    "Not Processed",
    "Downloaded", 
    "Uploaded to YT",
    "Failed",
    "Skipped"
]
```

### Advanced Sheets Features

```python
# Formatting
FREEZE_HEADER_ROW = True
AUTO_RESIZE_COLUMNS = True
APPLY_FILTERS = True

# Data processing
CHECK_DUPLICATES = True
UPDATE_EXISTING = False  # True to update existing entries
SORT_BY_DATE_DESC = True

# Batch operations
BATCH_UPDATE_SIZE = 100
USE_BATCH_REQUESTS = True
```

## Command Line Overrides

You can override configuration settings using command line arguments:

```bash
# Override days to scrape
python run_scraper.py --days 7

# Override max reels per account
python run_scraper.py --limit 20

# Enable fast mode
python run_scraper.py --fast

# Use custom config file
python run_scraper.py --config my_custom_config.py

# Override specific settings
python run_scraper.py --headless --no-images --max-scrolls 5
```

## Multiple Configuration Profiles

### Profile-Based Configuration

Create multiple config files for different scenarios:

```python
# config_fast.py - Speed optimized
USE_FAST_MODE = True
DAYS_TO_SCRAPE = 3
MAX_REELS_PER_ACCOUNT = 10

# config_thorough.py - Comprehensive scraping
USE_FAST_MODE = False
DAYS_TO_SCRAPE = 90
MAX_REELS_PER_ACCOUNT = 500

# config_testing.py - For testing
DAYS_TO_SCRAPE = 1
MAX_REELS_PER_ACCOUNT = 2
SAVE_SCREENSHOTS = True
DEBUG_MODE = True
```

Use with:
```bash
python run_scraper.py --config config_fast.py
python run_scraper.py --config config_thorough.py
python run_scraper.py --config config_testing.py
```

## Configuration Validation

The tool automatically validates your configuration:

### Required Settings Check
- `INSTAGRAM_URLS` must be a non-empty list
- `SPREADSHEET_ID` must be provided
- `credentials.json` must exist

### Value Validation
- Days must be >= 0
- Limits must be >= 0
- Timeouts must be > 0
- Paths must be valid

### Warning Conditions
- Very high scroll counts (may be slow)
- Very short timeouts (may cause failures)
- Missing optional files

## Troubleshooting Configuration

### Common Configuration Issues

| Issue | Solution |
|-------|----------|
| Chrome won't start | Check `CHROME_BINARY_PATH` |
| Profile errors | Clear `CHROME_PROFILE_PATH` directory |
| Slow performance | Enable `USE_FAST_MODE` |
| Memory issues | Reduce `MAX_SCROLLS` and `BATCH_SIZE` |
| Sheets errors | Verify `SPREADSHEET_ID` and permissions |

### Debug Configuration

```python
# Enable all debugging
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
SAVE_SCREENSHOTS = True
PRESERVE_BROWSER = True
LOG_TO_CONSOLE = True

# Slow down for observation
SCROLL_PAUSE_TIME = 5
PAGE_LOAD_TIMEOUT = 120
ELEMENT_TIMEOUT = 60
```

## Best Practices

### Production Configuration

```python
# Reliable production settings
USE_FAST_MODE = True
HEADLESS_MODE = True
ENABLE_BACKUP = True
LOG_LEVEL = "INFO"
RETRY_ATTEMPTS = 3
BATCH_SIZE = 25
MAX_SCROLLS = 15
```

### Development Configuration

```python
# Development-friendly settings
USE_FAST_MODE = False
HEADLESS_MODE = False
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
SAVE_SCREENSHOTS = True
PRESERVE_BROWSER = True
```

---

For specific use cases, see:
- [Quick Start Guide](quick_start.md) for basic setup
- [Advanced Usage](advanced_usage.md) for power user features
- [Troubleshooting](troubleshooting.md) for problem resolution
