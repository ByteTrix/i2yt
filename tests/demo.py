#!/usr/bin/env python3
"""
Quick Start Demo for Instagram Reel Scraper
A simplified script to help you get started quickly.
"""

import os
import sys
from pathlib import Path

def check_setup():
    """Check if basic setup is complete."""
    print("🔍 Checking setup...")
    
    # Check if config file exists
    if not os.path.exists('config.py'):
        print("❌ config.py not found. Please run setup.py first.")
        return False
    
    # Check if credentials file exists (basic check)
    try:
        import config
        if not os.path.exists(config.CREDENTIALS_FILE):
            print(f"❌ Credentials file '{config.CREDENTIALS_FILE}' not found.")
            print("📝 Please download your Google Service Account credentials.")
            return False
    except ImportError:
        print("❌ Error importing config.py")
        return False
    except AttributeError as e:
        print(f"❌ Missing configuration: {e}")
        return False
    
    print("✅ Basic setup check passed!")
    return True

def demo_browser_test():
    """Demo: Test if browser automation works."""
    print("\n🌐 Testing browser automation...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Setup Chrome options
        options = Options()
        options.add_argument("--headless")  # Run in background for demo
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        print("🚀 Starting Chrome WebDriver...")
        driver = webdriver.Chrome(options=options)
        
        print("📱 Navigating to Instagram...")
        driver.get("https://www.instagram.com")
        
        print(f"✅ Successfully loaded: {driver.title}")
        driver.quit()
        
        print("✅ Browser automation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        print("💡 Tip: Make sure Chrome and ChromeDriver are installed")
        return False

def demo_google_sheets_test():
    """Demo: Test Google Sheets connection."""
    print("\n📊 Testing Google Sheets connection...")
    
    try:
        import config
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Define scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        print("🔑 Loading credentials...")
        creds = Credentials.from_service_account_file(config.CREDENTIALS_FILE, scopes=scope)
        
        print("🔗 Connecting to Google Sheets...")
        client = gspread.authorize(creds)
        
        print("📋 Opening spreadsheet...")
        spreadsheet = client.open_by_key(config.GOOGLE_SHEETS_ID)
        sheet = spreadsheet.sheet1
        
        print(f"✅ Successfully connected to: {spreadsheet.title}")
        print(f"📄 Using sheet: {sheet.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets test failed: {e}")
        print("💡 Tips:")
        print("   - Check your credentials file")
        print("   - Verify Google Sheets ID")
        print("   - Ensure sheet is shared with service account")
        return False

def demo_simple_run():
    """Run a simple demo of the scraper."""
    print("\n🎯 Running simple scraper demo...")
    
    try:
        import config
        from instagram_reel_scraper import InstagramReelScraper, Config
        
        # Create config with limited scrolling for demo
        scraper_config = Config(
            instagram_url=config.INSTAGRAM_URL,
            google_sheets_id=config.GOOGLE_SHEETS_ID,
            credentials_file=config.CREDENTIALS_FILE,
            max_scrolls=2,  # Limited for demo
            scroll_delay=1.0,
            headless=True  # Run in background
        )
        
        print("🤖 Starting Instagram scraper...")
        scraper = InstagramReelScraper(scraper_config)
        scraper.run()
        
        print("✅ Demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Main demo function."""
    print("🎬 Instagram Reel Scraper - Quick Demo")
    print("=" * 50)
    
    # Check setup
    if not check_setup():
        print("\n❌ Setup incomplete. Please run setup.py first.")
        return
    
    # Test browser
    browser_ok = demo_browser_test()
    
    # Test Google Sheets
    sheets_ok = demo_google_sheets_test()
    
    if browser_ok and sheets_ok:
        print("\n🎉 All tests passed! Ready to run full scraper.")
        
        # Ask user if they want to run demo
        response = input("\n❓ Run a quick demo scrape? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            demo_simple_run()
        else:
            print("✅ Demo skipped. You can run the full scraper with: python run_scraper.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues before running the scraper.")

if __name__ == "__main__":
    main()
