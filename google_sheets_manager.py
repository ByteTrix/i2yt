#!/usr/bin/env python3
"""
Google Sheets Manager Module
Handles all Google Sheets operations
"""

import logging
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
import random

# Google Sheets imports
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

# Setup logging - use the parent logger configuration
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for Google Sheets API calls"""
    
    def __init__(self, max_calls_per_minute=None):
        self.max_calls_per_minute = max_calls_per_minute or getattr(config, 'SHEETS_MAX_CALLS_PER_MINUTE', 50)
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if we're approaching rate limits"""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        # If we're approaching the limit, wait
        if len(self.calls) >= self.max_calls_per_minute - 5:  # Leave some buffer
            wait_time = 60 - (now - self.calls[0]) + random.uniform(1, 3)  # Add jitter
            logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            self.calls = []  # Reset after waiting
        
        # Record this call
        self.calls.append(now)

def retry_on_quota_error(max_retries=None, base_delay=None):
    """Decorator to retry API calls on quota exceeded errors"""
    max_retries = max_retries or getattr(config, 'SHEETS_RETRY_ATTEMPTS', 3)
    base_delay = base_delay or getattr(config, 'SHEETS_BASE_RETRY_DELAY', 2)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'quota exceeded' in error_msg or 'rate limit' in error_msg or '429' in error_msg:
                        if attempt < max_retries - 1:
                            # Exponential backoff with jitter
                            delay = base_delay * (2 ** attempt) + random.uniform(1, 3)
                            logger.warning(f"Quota exceeded, retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"Max retries reached for {func.__name__}: {e}")
                            return None
                    else:
                        # Re-raise non-quota errors immediately
                        raise e
            return None
        return wrapper
    return decorator

class GoogleSheetsManager:
    """Handles all Google Sheets operations with rate limiting and error handling"""
    
    def __init__(self):
        self.logger = logger
        self.sheets_id = config.GOOGLE_SHEETS_ID
        self.credentials_file = config.CREDENTIALS_FILE
        self.gc = None
        self.worksheet = None
        self.rate_limiter = RateLimiter()  # Use config defaults
        self._url_cache = set()  # Cache for existing URLs
        self._cache_loaded = False
        self.setup_sheets_client()
    
    def setup_sheets_client(self):
        """Setup Google Sheets client"""
        try:
            # Define the scope
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scopes
            )
            
            # Initialize gspread client
            self.gc = gspread.authorize(credentials)
            
            # Open the worksheet
            self.worksheet = self.gc.open_by_key(self.sheets_id).sheet1
            
            self.logger.info("Google Sheets client initialized successfully")
            
            # Ensure headers exist
            self.ensure_headers()
            
        except Exception as e:
            self.logger.error(f"Failed to setup Google Sheets client: {str(e)}")
            raise
    
    def ensure_headers(self):
        """Ensure the correct headers exist in the sheet"""
        try:
            # Define expected headers
            expected_headers = ["Date", "Username", "Link", "Reel ID", "Description", "Status", "YT Posted Date", "YT ID"]
            
            # Get current headers
            current_headers = self.worksheet.row_values(1)
            
            # Check if headers need to be updated
            if not current_headers or current_headers != expected_headers:
                self.logger.info("Updating sheet headers...")
                self.worksheet.update('A1:H1', [expected_headers])
                self.logger.info("Headers updated successfully")
                
                # Setup dropdown validation for Status column
                try:
                    self.setup_status_dropdown()
                except Exception as dropdown_error:
                    self.logger.warning(f"Could not setup status dropdown: {dropdown_error}")
            
        except Exception as e:
            self.logger.error(f"Error ensuring headers: {str(e)}")
    
    def setup_status_dropdown(self):
        """Setup dropdown validation for Status column with Pending/Processing/Completed options and colored formatting."""
        try:
            # Use Google Sheets API v4 to set up data validation
            from googleapiclient.discovery import build
            
            # Setup credentials for Sheets API v4
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Build the service
            service = build('sheets', 'v4', credentials=credentials)
            
            # Get sheet properties to find the sheet ID
            spreadsheet = service.spreadsheets().get(spreadsheetId=self.sheets_id).execute()
            sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']  # Use first sheet
            
            # Define the dropdown validation rule for the Status column (column F = index 5)
            validation_rule = {
                'setDataValidation': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 1,  # Start from row 2 (after header)
                        'endRowIndex': 1000,  # Apply to first 1000 rows
                        'startColumnIndex': 5,  # Column F (Status)
                        'endColumnIndex': 6  # End at column G
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [
                                {'userEnteredValue': 'pending'},
                                {'userEnteredValue': 'processing'},
                                {'userEnteredValue': 'completed'},
                                {'userEnteredValue': 'failed'}
                            ]
                        },
                        'showCustomUi': True,
                        'strict': True
                    }
                }
            }
            
            # Define conditional formatting rules for different statuses
            conditional_formatting_rules = [
                # Pending - Orange background
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{
                                'sheetId': sheet_id,
                                'startRowIndex': 1,
                                'endRowIndex': 1000,
                                'startColumnIndex': 5,
                                'endColumnIndex': 6
                            }],
                            'booleanRule': {
                                'condition': {
                                    'type': 'TEXT_EQ',
                                    'values': [{'userEnteredValue': 'pending'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.4},  # Orange
                                    'textFormat': {'bold': True, 'foregroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2}}
                                }
                            }
                        },
                        'index': 0
                    }
                },
                # Processing - Blue background
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{
                                'sheetId': sheet_id,
                                'startRowIndex': 1,
                                'endRowIndex': 1000,
                                'startColumnIndex': 5,
                                'endColumnIndex': 6
                            }],
                            'booleanRule': {
                                'condition': {
                                    'type': 'TEXT_EQ',
                                    'values': [{'userEnteredValue': 'processing'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 0.4, 'green': 0.7, 'blue': 1.0},  # Blue
                                    'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
                                }
                            }
                        },
                        'index': 1
                    }
                },
                # Completed - Green background
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{
                                'sheetId': sheet_id,
                                'startRowIndex': 1,
                                'endRowIndex': 1000,
                                'startColumnIndex': 5,
                                'endColumnIndex': 6
                            }],
                            'booleanRule': {
                                'condition': {
                                    'type': 'TEXT_EQ',
                                    'values': [{'userEnteredValue': 'completed'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 0.6, 'green': 0.9, 'blue': 0.6},  # Green
                                    'textFormat': {'bold': True, 'foregroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.2}}
                                }
                            }
                        },
                        'index': 2
                    }
                },
                # Failed - Red background
                {
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{
                                'sheetId': sheet_id,
                                'startRowIndex': 1,
                                'endRowIndex': 1000,
                                'startColumnIndex': 5,
                                'endColumnIndex': 6
                            }],
                            'booleanRule': {
                                'condition': {
                                    'type': 'TEXT_EQ',
                                    'values': [{'userEnteredValue': 'failed'}]
                                },
                                'format': {
                                    'backgroundColor': {'red': 1.0, 'green': 0.6, 'blue': 0.6},  # Red
                                    'textFormat': {'bold': True, 'foregroundColor': {'red': 0.6, 'green': 0.1, 'blue': 0.1}}
                                }
                            }
                        },
                        'index': 3
                    }
                }
            ]
            
            # Execute the batch update with validation and conditional formatting
            requests = [validation_rule] + conditional_formatting_rules
            body = {
                'requests': requests
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheets_id,
                body=body
            ).execute()
            
            self.logger.info("Successfully set up dropdown validation and colored formatting for Status column")
            self.logger.info("Colors: pending=orange, processing=blue, completed=green, failed=red")
            
        except Exception as e:
            self.logger.warning(f"Could not setup dropdown validation and formatting: {e}")
    
    @retry_on_quota_error(max_retries=3, base_delay=2)
    def get_all_data(self) -> List[List[str]]:
        """Get all data from the worksheet with rate limiting"""
        try:
            self.rate_limiter.wait_if_needed()
            return self.worksheet.get_all_values()
        except Exception as e:
            self.logger.error(f"Error getting all data: {str(e)}")
            return []
    
    def add_reel_data(self, date: str, username: str, url: str, reel_id: str, description: str = "", status: str = "pending", yt_posted_date: str = "", yt_id: str = ""):
        """
        Add a new reel entry to the sheet
        
        Args:
            date: Date when reel was found
            username: Instagram username
            url: Instagram reel URL
            reel_id: Unique reel identifier
            description: Video description (optional)
            status: Status (pending, processing, completed)
            yt_posted_date: YouTube upload date (optional)
            yt_id: YouTube video ID (optional)
        """
        try:
            # Find the next empty row
            all_values = self.get_all_data()
            next_row = len(all_values) + 1
            
            # Prepare row data: Date, Username, Link, Reel ID, Description, Status, YT Posted Date, YT ID
            row_data = [date, username, url, reel_id, description, status, yt_posted_date, yt_id]
            
            # Add the row
            self.worksheet.update(f'A{next_row}:H{next_row}', [row_data])
            
            self.logger.info(f"Added reel data at row {next_row}: {url}")
            
        except Exception as e:
            self.logger.error(f"Error adding reel data: {str(e)}")
    
    def update_cell(self, row: int, col: int, value: str):
        """
        Update a specific cell
        
        Args:
            row: Row number (1-indexed)
            col: Column number (1-indexed)
            value: New value
        """
        try:
            self.worksheet.update_cell(row, col, value)
            self.logger.info(f"Updated cell ({row}, {col}) with: {value}")
            
        except Exception as e:
            self.logger.error(f"Error updating cell ({row}, {col}): {str(e)}")
    
    def update_status(self, row: int, status: str):
        """
        Update status column (column F) for a specific row
        
        Args:
            row: Row number (1-indexed)
            status: New status
        """
        self.update_cell(row, 6, status)  # Status is now in column F
    
    def update_description(self, row: int, description: str):
        """
        Update description column (column E) for a specific row
        
        Args:
            row: Row number (1-indexed)
            description: Video description
        """
        self.update_cell(row, 5, description)  # Description is now in column E
    
    def update_yt_info(self, row: int, yt_posted_date: str = "", yt_id: str = ""):
        """
        Update YouTube information (columns G and H) for a specific row
        
        Args:
            row: Row number (1-indexed)
            yt_posted_date: YouTube posting date
            yt_id: YouTube video ID
        """
        if yt_posted_date:
            self.update_cell(row, 7, yt_posted_date)  # YT Posted Date is in column G
        if yt_id:
            self.update_cell(row, 8, yt_id)  # YT ID is in column H
    
    def update_file_id(self, row: int, file_id: str):
        """
        Update file_id column (deprecated - file ID should not be stored in sheets)
        This method is kept for backward compatibility but does nothing.
        
        Args:
            row: Row number (1-indexed)
            file_id: Google Drive file ID (ignored)
        """
        # Do nothing - file IDs should not be stored in the sheet
        self.logger.debug(f"File ID storage skipped for row {row} (file_id: {file_id})")
    
    def get_rows_by_status(self, status: str) -> List[Dict]:
        """
        Get all rows with a specific status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of dictionaries with row data
        """
        try:
            all_data = self.get_all_data()
            
            if not all_data:
                return []
            
            # Skip header row
            filtered_rows = []
            for i, row in enumerate(all_data[1:], start=2):
                if len(row) >= 6 and row[5].lower() == status.lower():  # Status is now in column F (index 5)
                    filtered_rows.append({
                        'row_index': i,
                        'date': row[0] if len(row) > 0 else "",
                        'username': row[1] if len(row) > 1 else "",
                        'url': row[2] if len(row) > 2 else "",
                        'reel_id': row[3] if len(row) > 3 else "",
                        'description': row[4] if len(row) > 4 else "",
                        'status': row[5] if len(row) > 5 else "",
                        'yt_posted_date': row[6] if len(row) > 6 else "",
                        'yt_id': row[7] if len(row) > 7 else ""
                    })
            
            return filtered_rows
            
        except Exception as e:
            self.logger.error(f"Error getting rows by status: {str(e)}")
            return []
    
    def _load_url_cache(self):
        """Load all existing URLs into cache to avoid repeated API calls"""
        if self._cache_loaded:
            return
            
        try:
            self.logger.info("Loading URL cache from Google Sheets...")
            all_data = self.get_all_data()
            
            if all_data:
                for row in all_data[1:]:  # Skip header
                    if len(row) > 2 and row[2]:  # URL is in column C (index 2)
                        self._url_cache.add(row[2])
                
                self.logger.info(f"Loaded {len(self._url_cache)} URLs into cache")
            
            self._cache_loaded = True
            
        except Exception as e:
            self.logger.error(f"Error loading URL cache: {str(e)}")

    def url_exists(self, url: str) -> bool:
        """
        Check if a URL already exists in the sheet using cache
        
        Args:
            url: URL to check
            
        Returns:
            True if URL exists, False otherwise
        """
        try:
            # Load cache if not already loaded
            if not self._cache_loaded:
                self._load_url_cache()
            
            return url in self._url_cache
            
        except Exception as e:
            self.logger.error(f"Error checking if URL exists: {str(e)}")
            return False
    
    @retry_on_quota_error(max_retries=3, base_delay=2)
    def batch_add_reels(self, reels_data: List[Dict]):
        """
        Add multiple reels in batch for better performance with rate limiting
        
        Args:
            reels_data: List of dictionaries with reel data
        """
        try:
            if not reels_data:
                return
            
            self.rate_limiter.wait_if_needed()
            
            # Get current data to find next row
            all_values = self.get_all_data()
            next_row = len(all_values) + 1
            
            # Prepare batch data
            batch_data = []
            for reel in reels_data:
                url = reel.get('url', '')
                row_data = [
                    reel.get('date', ''),
                    reel.get('username', ''),
                    url,
                    reel.get('reel_id', ''),
                    reel.get('description', ''),
                    reel.get('status', 'pending'),
                    reel.get('yt_posted_date', ''),
                    reel.get('yt_id', '')
                ]
                batch_data.append(row_data)
                
                # Update cache
                if url:
                    self._url_cache.add(url)
            
            # Calculate range
            end_row = next_row + len(batch_data) - 1
            range_name = f'A{next_row}:H{end_row}'
            
            self.rate_limiter.wait_if_needed()
            
            # Update in batch
            self.worksheet.update(range_name, batch_data)
            
            self.logger.info(f"Added {len(batch_data)} reels in batch")
            
        except Exception as e:
            self.logger.error(f"Error in batch add reels: {str(e)}")
    
    def get_pending_urls(self) -> List[str]:
        """Get all URLs with pending status"""
        try:
            pending_rows = self.get_rows_by_status("pending")
            return [row['url'] for row in pending_rows if row['url']]
            
        except Exception as e:
            self.logger.error(f"Error getting pending URLs: {str(e)}")
            return []
    
    def get_urls_without_descriptions(self) -> List[Dict]:
        """Get all URLs that don't have descriptions"""
        try:
            all_data = self.get_all_data()
            
            if not all_data:
                return []
            
            urls_without_desc = []
            for i, row in enumerate(all_data[1:], start=2):
                if len(row) >= 3:  # Has URL
                    url = row[2] if len(row) > 2 else ""  # URL is in column C (index 2)
                    description = row[4] if len(row) > 4 else ""  # Description is in column E (index 4)
                    
                    if url and not description:
                        urls_without_desc.append({
                            'row_index': i,
                            'url': url
                        })
            
            return urls_without_desc
            
        except Exception as e:
            self.logger.error(f"Error getting URLs without descriptions: {str(e)}")
            return []
    
    def get_urls_without_descriptions_by_status(self, status: str) -> List[Dict]:
        """Get URLs that don't have descriptions for a specific status"""
        try:
            all_data = self.get_all_data()
            
            if not all_data:
                return []
            
            urls_without_desc = []
            for i, row in enumerate(all_data[1:], start=2):
                if len(row) >= 6:  # Has URL and status
                    url = row[2] if len(row) > 2 else ""  # URL is in column C (index 2)
                    description = row[4] if len(row) > 4 else ""  # Description is in column E (index 4)
                    row_status = row[5] if len(row) > 5 else ""  # Status is in column F (index 5)
                    
                    if url and not description and row_status.lower() == status.lower():
                        urls_without_desc.append({
                            'row_index': i,
                            'url': url
                        })
            
            return urls_without_desc
            
        except Exception as e:
            self.logger.error(f"Error getting URLs without descriptions by status: {str(e)}")
            return []


# Utility functions for standalone use
def add_single_reel(url: str, description: str = ""):
    """Add a single reel to sheets (utility function)"""
    try:
        sheets_manager = GoogleSheetsManager()
        current_date = datetime.now().strftime("%d-%b-%y").upper()
        sheets_manager.add_reel_data(current_date, url, "pending", description)
        logger.info(f"Added reel: {url}")
    except Exception as e:
        logger.error(f"Error adding single reel: {str(e)}")

def get_pending_count():
    """Get count of pending reels"""
    try:
        sheets_manager = GoogleSheetsManager()
        pending_rows = sheets_manager.get_rows_by_status("pending")
        return len(pending_rows)
    except Exception as e:
        logger.error(f"Error getting pending count: {str(e)}")
        return 0


if __name__ == "__main__":
    # Test the sheets manager
    try:
        sheets_manager = GoogleSheetsManager()
        logger.info("Google Sheets Manager test successful")
        
        # Test getting pending count
        count = get_pending_count()
        logger.info(f"Pending reels count: {count}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
