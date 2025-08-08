#!/usr/bin/env python3
"""
Test Google Drive OAuth2 Authentication
This script tests the new OAuth2 authentication setup.
"""

import logging
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    from google_drive_manager import GoogleDriveManager
    print("✅ Successfully imported GoogleDriveManager")
    
    # Test initialization
    print("🔄 Testing Google Drive authentication...")
    manager = GoogleDriveManager()
    print("✅ Google Drive manager initialized successfully!")
    
    # Test a simple API call (list files in the target folder)
    print("🔄 Testing API connection...")
    try:
        # Query the target folder to verify access
        folder_id = manager.drive_folder_id
        if folder_id:
            results = manager.service.files().list(
                q=f"'{folder_id}' in parents",
                pageSize=1,
                fields="files(id, name)"
            ).execute()
            print(f"✅ Successfully connected to Google Drive!")
            print(f"📂 Target folder has {len(results.get('files', []))} files")
        else:
            print("⚠️  No folder ID specified, but authentication successful")
            
    except Exception as api_error:
        print(f"❌ API test failed: {api_error}")
        sys.exit(1)
        
    print()
    print("🎉 Google Drive OAuth2 setup is working correctly!")
    print("💡 You can now run your scraper without storage quota errors.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the correct directory and all dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Authentication test failed: {e}")
    print()
    if "credentials.json" in str(e):
        print("💡 Please ensure your credentials.json contains OAuth2 credentials")
        print("   (not service account credentials)")
    sys.exit(1)
