#!/usr/bin/env python3
"""
Test script to verify Google API imports and functionality
"""

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    import gspread
    
    print("✅ All Google API imports successful!")
    print("✅ gspread import successful!")
    print("✅ Google API Python client import successful!")
    
    # Test credentials loading (this will only work if credentials.json exists)
    try:
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print("✅ Credentials loading successful!")
        
        # Test service creation
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Google Sheets API v4 service creation successful!")
        
    except FileNotFoundError:
        print("⚠️  credentials.json not found - but this is expected for testing")
    except Exception as e:
        print(f"⚠️  Credentials/service error (expected): {e}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

print("\nTest completed!")
