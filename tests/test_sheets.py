#!/usr/bin/env python3
"""
Test Google Sheets Connection
Simple test to debug the Google Sheets setup issue.
"""

import os
import sys
import traceback

def test_google_sheets():
    """Test Google Sheets connection independently."""
    print("🔍 Testing Google Sheets Connection...")
    
    try:
        # Import required modules
        print("📦 Importing required modules...")
        import gspread
        from google.oauth2.service_account import Credentials
        import config
        
        print("✅ Modules imported successfully")
        
        # Check if credentials file exists
        print(f"🔑 Checking credentials file: {config.CREDENTIALS_FILE}")
        if not os.path.exists(config.CREDENTIALS_FILE):
            print(f"❌ Credentials file not found: {config.CREDENTIALS_FILE}")
            return False
        print("✅ Credentials file exists")
        
        # Define scope
        print("🔧 Setting up OAuth scope...")
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        print("✅ Scope defined")
        
        # Load credentials
        print("🔑 Loading service account credentials...")
        try:
            creds = Credentials.from_service_account_file(config.CREDENTIALS_FILE, scopes=scope)
            print(f"✅ Credentials loaded for: {creds.service_account_email}")
        except Exception as cred_error:
            print(f"❌ Failed to load credentials: {cred_error}")
            print(f"Error type: {type(cred_error).__name__}")
            return False
        
        # Authorize client
        print("🔗 Authorizing Google Sheets client...")
        try:
            client = gspread.authorize(creds)
            print("✅ Client authorized successfully")
        except Exception as auth_error:
            print(f"❌ Failed to authorize client: {auth_error}")
            print(f"Error type: {type(auth_error).__name__}")
            return False
          # Test opening the spreadsheet
        print(f"📊 Attempting to open spreadsheet: {config.GOOGLE_SHEETS_ID}")
        try:
            spreadsheet = client.open_by_key(config.GOOGLE_SHEETS_ID)
            print(f"✅ Successfully opened: {spreadsheet.title}")
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"❌ Spreadsheet not found with ID: {config.GOOGLE_SHEETS_ID}")
            print("💡 Possible issues:")
            print(f"   - Sheet ID is incorrect")
            print(f"   - Sheet not shared with: {creds.service_account_email}")
            print(f"   - Service account doesn't have access")
            return False
        except Exception as sheet_error:
            print(f"❌ Failed to open spreadsheet: {sheet_error}")
            print(f"Error type: {type(sheet_error).__name__}")
            if "Permission" in str(sheet_error) or hasattr(sheet_error, 'response'):
                print("💡 This looks like a permission error!")
                print(f"🔑 Make sure to share the Google Sheet with: {creds.service_account_email}")
                print("📋 Steps to fix:")
                print("   1. Open your Google Sheet")
                print("   2. Click 'Share' button")
                print(f"   3. Add this email: {creds.service_account_email}")
                print("   4. Give 'Editor' permissions")
            print(f"Full error details: {traceback.format_exc()}")
            return False
        
        # Test accessing the first sheet
        print("📋 Testing sheet access...")
        try:
            sheet = spreadsheet.sheet1
            print(f"✅ Accessed sheet: {sheet.title}")
        except Exception as access_error:
            print(f"❌ Failed to access sheet: {access_error}")
            return False
        
        # Test reading data
        print("📖 Testing read access...")
        try:
            headers = sheet.row_values(1)
            print(f"✅ Read headers: {headers}")
        except Exception as read_error:
            print(f"❌ Failed to read from sheet: {read_error}")
            return False
        
        # Test writing data (optional)
        print("✏️  Testing write access...")
        try:
            if not headers or headers != ['Timestamp', 'Reel URL', 'Reel ID', 'Status']:
                sheet.clear()
                sheet.append_row(['Timestamp', 'Reel URL', 'Reel ID', 'Status'])
                print("✅ Headers set successfully")
            else:
                print("✅ Headers already correct")
        except Exception as write_error:
            print(f"❌ Failed to write to sheet: {write_error}")
            return False
        
        print("\n🎉 All Google Sheets tests passed!")
        return True
        
    except ImportError as import_error:
        print(f"❌ Import error: {import_error}")
        print("💡 Try: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Main test function."""
    print("🧪 Google Sheets Connection Test")
    print("=" * 40)
    
    # Check if config exists
    if not os.path.exists('config.py'):
        print("❌ config.py not found. Please create it from config_template.py")
        return
    
    # Run the test
    success = test_google_sheets()
    
    if success:
        print("\n✅ Google Sheets connection is working!")
        print("🚀 You can now run the main scraper")
    else:
        print("\n❌ Google Sheets connection failed")
        print("🔧 Please fix the issues above before running the scraper")

if __name__ == "__main__":
    main()
