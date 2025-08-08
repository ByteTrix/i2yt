#!/usr/bin/env python3
"""
OAuth2 Setup Script for Google Drive
This script helps set up OAuth2 authentication for Google Drive access.
"""

import os
import sys
import json

def check_credentials_file():
    """Check if credentials.json exists and is OAuth2 format"""
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        # Check if it's OAuth2 credentials (has 'installed' or 'web' key)
        if 'installed' in creds or 'web' in creds:
            print("✅ OAuth2 credentials.json found and valid")
            return True
        elif 'type' in creds and creds['type'] == 'service_account':
            print("❌ Found service account credentials, but OAuth2 credentials are needed")
            return False
        else:
            print("❌ credentials.json format not recognized")
            return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def print_setup_instructions():
    """Print instructions for setting up OAuth2 credentials"""
    print("\n" + "="*60)
    print("🔧 GOOGLE DRIVE OAUTH2 SETUP INSTRUCTIONS")
    print("="*60)
    print()
    print("You need to create OAuth2 credentials to fix the storage quota error.")
    print("Service accounts don't have storage quota, but OAuth2 uses your personal")
    print("Google Drive storage.")
    print()
    print("📋 STEPS TO CREATE OAUTH2 CREDENTIALS:")
    print()
    print("1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    print("2. Select your project (or create a new one)")
    print()
    print("3. Enable the Google Drive API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Drive API'")
    print("   - Click 'Enable'")
    print()
    print("4. Create OAuth2 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("   - Application type: 'Desktop application'")
    print("   - Name: 'Instagram Scraper Drive Access'")
    print("   - Click 'Create'")
    print()
    print("5. ⚠️  IMPORTANT: Configure Authorized redirect URIs:")
    print("   - After creating the credential, click the edit button (pencil icon)")
    print("   - In 'Authorized redirect URIs' section, add these THREE URIs:")
    print("     * http://localhost:8080/")
    print("     * http://127.0.0.1:8080/")
    print("     * urn:ietf:wg:oauth:2.0:oob")
    print("   - Click 'Save'")
    print()
    print("6. Download the credentials:")
    print("   - Click the download button next to your OAuth client")
    print("   - Save the file as 'credentials.json' in this directory")
    print("   - Replace the existing credentials.json file")
    print()
    print("7. Run your scraper again:")
    print("   - The first time you run it, a browser window will open")
    print("   - Sign in with your Google account")
    print("   - Grant permission to access Google Drive")
    print("   - Future runs will use the saved token")
    print()
    print("="*60)
    print("💡 TIP: Make sure you sign in with a Google account that has")
    print("enough Google Drive storage space for your videos!")
    print("="*60)
    print()
    print("🚨 IF YOU GET 'redirect_uri_mismatch' ERROR:")
    print("   Make sure you added ALL THREE redirect URIs in step 5!")
    print("="*60)

def main():
    print("🔍 Checking Google Drive credentials setup...")
    
    if check_credentials_file():
        print()
        print("✅ Your credentials.json is ready for OAuth2!")
        print("💡 When you run the scraper next time, it will open a browser")
        print("   for you to sign in to Google Drive.")
        return True
    else:
        print_setup_instructions()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
