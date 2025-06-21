# Instagram Reel Scraper

An automated Python script that opens a browser, navigates to Instagram, collects reel links, and stores them in Google Sheets.

## Features

✅ **Automated Browser Control**: Uses Selenium to control Chrome browser  
✅ **Instagram Navigation**: Automatically navigates to Instagram profiles and reels  
✅ **Smart Scrolling**: Scrolls through content to collect maximum reel links  
✅ **Google Sheets Integration**: Stores collected links directly in Google Sheets  
✅ **Duplicate Prevention**: Avoids storing duplicate links  
✅ **Error Handling**: Robust error handling and logging  
✅ **Backup System**: Local backup in case of Google Sheets failures  
✅ **Configurable**: Easy configuration through config file  

## Quick Start

### 1. Install Dependencies

Run the setup script to install all dependencies:

```bash
python setup.py
```

Or manually install:

```bash
pip install -r requirements.txt
```

### 2. Configuration

1. Copy the configuration template:
   ```bash
   cp config_template.py config.py
   ```

2. Edit `config.py` with your values:
   ```python
   INSTAGRAM_URL = "https://www.instagram.com/your_target_account/"
   GOOGLE_SHEETS_ID = "your_google_sheets_id_here"
   CREDENTIALS_FILE = "credentials.json"
   ```

### 3. Google Sheets Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Sheets API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
   - Download the JSON credentials file

4. **Setup Google Sheet**:
   - Create a new Google Sheet
   - Copy the Sheet ID from the URL (between `/d/` and `/edit`)
   - Share the sheet with your service account email (from credentials file)
   - Give "Editor" permissions

5. **Update Configuration**:
   - Replace `credentials.json` with your downloaded file
   - Update `GOOGLE_SHEETS_ID` in `config.py`

### 4. Run the Scraper

```bash
python run_scraper.py
```

## Configuration Options

Edit `config.py` to customize the scraper behavior:

```python
# Instagram Configuration
INSTAGRAM_URL = "https://www.instagram.com/target_account/"

# Google Sheets Configuration  
GOOGLE_SHEETS_ID = "your_sheets_id"
CREDENTIALS_FILE = "credentials.json"

# Scraping Configuration
MAX_SCROLLS = 15          # Number of scrolls to perform
SCROLL_DELAY = 2.0        # Delay between scrolls (seconds)
IMPLICIT_WAIT = 10        # Selenium wait time
PAGE_LOAD_TIMEOUT = 30    # Page load timeout
HEADLESS = False          # True for headless browser
```

## File Structure

```
├── instagram_reel_scraper.py    # Main scraper class
├── run_scraper.py              # Simple runner script
├── setup.py                    # Setup and installation script
├── config_template.py          # Configuration template
├── config.py                   # Your configuration (create from template)
├── credentials.json            # Google Service Account credentials
├── requirements.txt            # Python dependencies
├── SCRAPER_README.md          # This file
└── instagram_scraper.log      # Log file (created when running)
```

## How It Works

### 1. Browser Automation
- Opens Chrome browser with anti-detection settings
- Navigates to specified Instagram URL
- Handles popups and login prompts
- Finds and clicks on reels section

### 2. Link Collection
- Scrolls through the page systematically
- Collects all visible reel links
- Extracts reel IDs from URLs
- Removes duplicates

### 3. Data Storage
- Connects to Google Sheets using service account
- Checks for existing links to avoid duplicates
- Stores new links with timestamps
- Creates local backup if Google Sheets fails

### 4. Google Sheets Format

The script creates a sheet with these columns:
- **Timestamp**: When the link was collected
- **Reel URL**: Full Instagram reel URL
- **Reel ID**: Extracted reel identifier
- **Status**: Collection status

## Troubleshooting

### Chrome WebDriver Issues

If you get WebDriver errors:

1. **Install ChromeDriver manually**:
   - Download from [ChromeDriver](https://chromedriver.chromium.org/)
   - Extract to a folder in your PATH

2. **Use webdriver-manager** (automatic):
   ```bash
   pip install webdriver-manager
   ```
   
   Then update the scraper to use:
   ```python
   from webdriver_manager.chrome import ChromeDriverManager
   driver = webdriver.Chrome(ChromeDriverManager().install())
   ```

### Google Sheets Errors

**Permission Denied**:
- Ensure the sheet is shared with your service account email
- Check that the service account has "Editor" permissions

**API Not Enabled**:
- Go to Google Cloud Console
- Enable Google Sheets API for your project

**Invalid Credentials**:
- Verify the credentials.json file is correct
- Ensure the file path in config.py is correct

### Instagram Access Issues

**Rate Limiting**:
- Increase `SCROLL_DELAY` in config.py
- Reduce `MAX_SCROLLS` value
- Use `HEADLESS = True` to be less detectable

**Login Required**:
- Some Instagram profiles require login
- Consider using Instagram cookies if needed

## Advanced Usage

### Running in Headless Mode

For server deployment or background running:

```python
HEADLESS = True  # in config.py
```

### Custom Selectors

If Instagram changes their HTML structure, you can modify the selectors in `instagram_reel_scraper.py`:

```python
# Update these selectors in collect_visible_reel_links()
selectors = [
    "a[href*='/reel/']",
    "a[href*='/p/']",
    # Add new selectors here
]
```

### Batch Processing

To scrape multiple accounts:

```python
accounts = [
    "https://www.instagram.com/account1/",
    "https://www.instagram.com/account2/", 
    "https://www.instagram.com/account3/"
]

for url in accounts:
    config.instagram_url = url
    scraper = InstagramReelScraper(config)
    scraper.run()
```

## Logging

The scraper creates detailed logs in `instagram_scraper.log`:

- INFO: General progress updates
- WARNING: Non-critical issues
- ERROR: Critical errors that stop execution
- DEBUG: Detailed debugging information

## Legal Notice

⚠️ **Important**: This scraper is for educational purposes. Please ensure you comply with:

- Instagram's Terms of Service
- Rate limiting and respectful scraping
- Data privacy regulations
- Copyright and intellectual property laws

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational purposes. Use responsibly and in compliance with applicable terms of service.
