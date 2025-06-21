# 🤖 Instagram Reel Scraper - Complete Setup Guide

I've created a comprehensive Instagram automation script that will:
- ✅ Open a browser automatically
- ✅ Navigate to Instagram profiles
- ✅ Find and collect reel links
- ✅ Store them in Google Sheets
- ✅ Handle duplicates automatically

## 📁 Files Created

### Main Scripts
- `instagram_reel_scraper.py` - Main scraper class with all functionality
- `run_scraper.py` - Simple runner script
- `setup.py` - Automated setup and installation
- `demo.py` - Quick test and demo script

### Configuration
- `config_template.py` - Template configuration file
- `requirements.txt` - Python dependencies
- `run_scraper.bat` - Windows batch file for easy execution

### Documentation
- `SCRAPER_README.md` - Detailed documentation
- `README.md` - Your existing project documentation

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
python setup.py
```

### Step 2: Configure Settings
1. Copy configuration template:
   ```bash
   copy config_template.py config.py
   ```

2. Edit `config.py` with your values:
   ```python
   INSTAGRAM_URL = "https://www.instagram.com/target_account/"
   GOOGLE_SHEETS_ID = "your_actual_sheets_id"
   CREDENTIALS_FILE = "credentials.json"
   ```

### Step 3: Setup Google Sheets
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Google Sheets API
3. Create Service Account → Download JSON credentials
4. Replace `credentials.json` with your file
5. Create Google Sheet → Share with service account email

## 🎯 Running the Scraper

### Easy Way (Windows)
Double-click `run_scraper.bat`

### Command Line
```bash
python run_scraper.py
```

### Test First
```bash
python demo.py
```

## ⚙️ Configuration Options

Edit `config.py` to customize:

```python
# Target Instagram account
INSTAGRAM_URL = "https://www.instagram.com/username/"

# How much to scroll (more = more links)
MAX_SCROLLS = 15

# Speed (higher = slower but more reliable)
SCROLL_DELAY = 2.0

# Run without browser window
HEADLESS = False  # Set to True for background mode
```

## 📊 Google Sheets Output

The script creates a sheet with columns:
- **Timestamp** - When link was collected
- **Reel URL** - Full Instagram reel URL
- **Reel ID** - Extracted reel identifier  
- **Status** - Collection status

## 🔧 Troubleshooting

### Chrome/WebDriver Issues
- Install Chrome browser
- Download ChromeDriver from [here](https://chromedriver.chromium.org/)
- Or install automatically: `pip install webdriver-manager`

### Google Sheets Errors
- Check credentials file is correct
- Verify sheet is shared with service account
- Ensure Google Sheets API is enabled

### Rate Limiting
- Increase `SCROLL_DELAY` in config
- Reduce `MAX_SCROLLS` 
- Use `HEADLESS = True`

## 🎯 Features

- **Smart Scrolling** - Automatically scrolls to find more content
- **Duplicate Prevention** - Won't save the same link twice
- **Error Recovery** - Handles popups and errors gracefully
- **Backup System** - Saves local backup if Google Sheets fails
- **Configurable** - Easy to customize for different accounts
- **Logging** - Detailed logs for debugging

## 🔒 Legal & Ethics

⚠️ **Important**: This tool is for educational purposes. Please:
- Respect Instagram's Terms of Service
- Don't overload their servers (use appropriate delays)
- Respect content creators' rights
- Follow data privacy laws

## 💡 Pro Tips

1. **Start Small**: Test with `MAX_SCROLLS = 3` first
2. **Use Headless**: Set `HEADLESS = True` for background running
3. **Check Logs**: Look at `instagram_scraper.log` for issues
4. **Backup Data**: The script creates local backups automatically
5. **Multiple Accounts**: Change `INSTAGRAM_URL` to scrape different profiles

## 🆘 Need Help?

1. Run `python demo.py` to test your setup
2. Check `instagram_scraper.log` for error details
3. Read `SCRAPER_README.md` for detailed documentation
4. Verify all configuration values are correct

## 🎉 Ready to Use!

Your Instagram reel scraper is ready! The automation will:
1. Open Chrome browser
2. Navigate to your target Instagram account
3. Scroll through reels automatically
4. Extract all reel links
5. Save them to your Google Sheet
6. Show progress and results

**Run it now**: `python run_scraper.py`

---
*Built with ❤️ for your Instagram to YouTube automation workflow*
