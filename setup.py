#!/usr/bin/env python3
"""
Setup script for Instagram Reel Scraper
This script helps set up the environment and dependencies.
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def install_requirements():
    """Install required Python packages."""
    print("📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_config():
    """Set up configuration file."""
    config_file = Path("config.py")
    template_file = Path("config_template.py")
    
    if config_file.exists():
        print("📝 Configuration file already exists")
        return True
        
    if not template_file.exists():
        print("❌ Template file not found!")
        return False
        
    print("📝 Creating configuration file...")
    try:
        # Copy template to config.py
        with open(template_file, 'r') as src, open(config_file, 'w') as dst:
            content = src.read()
            dst.write(content)
        print("✅ Configuration file created from template")
        print("📌 Please edit config.py with your actual values!")
        return True
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
        return False

def create_sample_credentials():
    """Create a sample credentials.json file."""
    credentials_file = Path("credentials.json")
    
    if credentials_file.exists():
        print("🔑 Credentials file already exists")
        return True
        
    print("🔑 Creating sample credentials file...")
    sample_credentials = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_HERE\\n-----END PRIVATE KEY-----\\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    try:
        with open(credentials_file, 'w') as f:
            json.dump(sample_credentials, f, indent=2)
        print("✅ Sample credentials file created")
        print("📌 Please replace with your actual Google Service Account credentials!")
        return True
    except Exception as e:
        print(f"❌ Failed to create credentials file: {e}")
        return False

def check_chrome_driver():
    """Check if Chrome/Chromedriver is available."""
    print("🌐 Checking Chrome WebDriver...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Try to create a driver instance
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ Chrome WebDriver is working!")
        return True
    except Exception as e:
        print(f"⚠️  Chrome WebDriver issue: {e}")
        print("📌 You may need to install ChromeDriver:")
        print("   - Download from: https://chromedriver.chromium.org/")
        print("   - Or install via: pip install webdriver-manager")
        return False

def display_next_steps():
    """Display next steps for the user."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. Edit config.py with your actual values:")
    print("   - Instagram URL (target account)")
    print("   - Google Sheets ID")
    print("   - Credentials file path")
    print("\n2. Replace credentials.json with your Google Service Account file")
    print("   - Go to Google Cloud Console")
    print("   - Create a Service Account")
    print("   - Download the JSON credentials")
    print("   - Enable Google Sheets API")
    print("\n3. Create/prepare your Google Sheets:")
    print("   - Create a new Google Sheet")
    print("   - Share it with your service account email")
    print("   - Copy the Sheet ID from the URL")
    print("\n4. Run the scraper:")
    print("   python run_scraper.py")
    print("\n📚 For detailed instructions, check the README.md file")

def main():
    """Main setup function."""
    print("🚀 Instagram Reel Scraper Setup")
    print("="*50)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Setup configuration
    if not setup_config():
        success = False
    
    
    # Check Chrome driver
    if not check_chrome_driver():
        print("⚠️  Chrome WebDriver may need manual setup")
    
    if success:
        display_next_steps()
    else:
        print("❌ Setup completed with some issues. Please fix them before running the scraper.")

if __name__ == "__main__":
    main()
