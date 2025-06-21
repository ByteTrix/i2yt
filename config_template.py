# Configuration file for Instagram Reel Scraper
# Copy this file to config.py and update with your actual values

# Instagram Configuration
INSTAGRAM_URL = "https://www.instagram.com/your_target_account/"  # Replace with target Instagram URL
# List of Instagram URLs to scrape - add as many as you need
INSTAGRAM_URLS = [
    "https://www.instagram.com/composedmindset/",
    "https://www.instagram.com/ipposmindset/",
    "https://www.instagram.com/tatakae.wrld/"
]
# Google Sheets Configuration
GOOGLE_SHEETS_ID = "your_google_sheets_id_here"  # Replace with your Google Sheets ID
CREDENTIALS_FILE = "credentials.json"  # Path to your Google Service Account credentials file
# Scraping Configuration
MAX_SCROLLS = 15  # Maximum number of scrolls to perform
TARGET_LINKS = 100  # Target number of links to collect (set to 0 for unlimited)
SCROLL_DELAY = 0.5  # Reduced from 2.0 to 0.5 seconds for faster scrolling
BATCH_SIZE = 25  # Save to Google Sheets every 25 new links
IMPLICIT_WAIT = 5  # Reduced from 10 to 5 seconds
PAGE_LOAD_TIMEOUT = 20  # Reduced from 30 to 20 seconds
HEADLESS = False  # Set to True to run browser in headless mode
FAST_MODE = True  # Enable fast mode with image blocking for better performance

# Advanced Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Browser Configuration
USE_EXISTING_BROWSER = True  # Try to connect to existing browser session
BROWSER_DEBUG_PORT = 9222    # Port for remote debugging