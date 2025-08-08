#!/usr/bin/env python3
"""
Google Drive Manager Module
Handles video downloads and uploads to Google Drive
"""

import os
import logging
import subprocess
import json
import shutil
import time
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import io
from pathlib import Path

# Google Drive imports
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from tqdm import tqdm
from googleapiclient.errors import HttpError
import requests

import config

# Setup logging - use the parent logger configuration
logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Handles video downloads and uploads to Google Drive"""
    
    def __init__(self):
        self.logger = logger
        self.service = None
        self.drive_folder_id = config.DRIVE_FOLDER_ID
        self.credentials_file = config.DRIVE_CREDENTIALS_FILE
        self.delete_local = config.DELETE_LOCAL_AFTER_UPLOAD
        
        # Ensure download directory is absolute path
        if os.path.isabs(config.DOWNLOAD_DIRECTORY):
            self.download_dir = config.DOWNLOAD_DIRECTORY
        else:
            self.download_dir = os.path.join(os.getcwd(), config.DOWNLOAD_DIRECTORY)
            
        self.ensure_ytdlp_installed()
        self.setup_drive_service()
        self.ensure_download_directory()
    
    def ensure_ytdlp_installed(self):
        """Ensure yt-dlp is installed"""
        try:
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
            self.logger.info("yt-dlp is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.info("Installing yt-dlp...")
            subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
    
    def setup_drive_service(self):
        """Setup Google Drive API service with OAuth2 authentication"""
        try:
            # Define the scope - include both Drive and Sheets for unified authentication
            scopes = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            
            creds = None
            token_file = 'token.pickle'
            
            # Load existing token if it exists
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # Try to refresh the token
                    try:
                        creds.refresh(Request())
                        self.logger.info("Google Drive token refreshed successfully")
                    except Exception as e:
                        self.logger.warning(f"Token refresh failed: {e}. Requesting new authorization.")
                        creds = None
                
                if not creds:
                    # Check if credentials file exists and is valid OAuth2 credentials
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"OAuth2 credentials file not found: {self.credentials_file}\n"
                            "Please create OAuth2 credentials from Google Cloud Console:\n"
                            "1. Go to https://console.cloud.google.com/\n"
                            "2. Enable the Google Drive API\n"
                            "3. Create OAuth2 credentials (not service account)\n"
                            "4. Download the credentials as 'credentials.json'"
                        )
                    
                    # Start OAuth2 flow with proper redirect URI handling
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, scopes)
                        
                        # Try to run with a specific port first, fallback to no browser if needed
                        try:
                            self.logger.info("🔐 Starting OAuth2 authorization flow...")
                            self.logger.info("📱 A web browser will open for Google sign-in")
                            creds = flow.run_local_server(port=8080, open_browser=True)
                            self.logger.info("✅ Google Drive OAuth2 authorization completed")
                        except Exception as browser_error:
                            self.logger.warning(f"⚠️  Browser flow failed: {browser_error}")
                            self.logger.info("🔗 Trying console-based authentication...")
                            creds = flow.run_console()
                            self.logger.info("✅ Console-based OAuth2 authorization completed")
                    except Exception as oauth_error:
                        if "redirect_uri_mismatch" in str(oauth_error):
                            raise Exception(
                                "❌ OAuth2 Redirect URI Mismatch Error!\n\n"
                                "🔧 SOLUTION: You need to add the correct redirect URI to your OAuth2 credentials.\n\n"
                                "📋 Steps to fix:\n"
                                "1. Go to Google Cloud Console: https://console.cloud.google.com/\n"
                                "2. Navigate to 'APIs & Services' > 'Credentials'\n"
                                "3. Find your OAuth 2.0 Client ID and click the edit button (pencil icon)\n"
                                "4. In 'Authorized redirect URIs', add these URIs:\n"
                                "   - http://localhost:8080/\n"
                                "   - http://127.0.0.1:8080/\n"
                                "   - urn:ietf:wg:oauth:2.0:oob\n"
                                "5. Click 'Save'\n"
                                "6. Wait a few minutes for the changes to propagate\n"
                                "7. Run the script again\n\n"
                                f"Original error: {oauth_error}"
                            )
                        else:
                            raise oauth_error
                
                # Save the credentials for the next run
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                    self.logger.info("Google Drive token saved for future use")
            
            # Build service with OAuth2 credentials
            self.service = build('drive', 'v3', credentials=creds, cache_discovery=False)
            
            self.logger.info("Google Drive service initialized successfully with OAuth2")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Google Drive service: {str(e)}")
            raise
    
    def ensure_download_directory(self):
        """Ensure download directory exists"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            self.logger.info(f"Created download directory: {self.download_dir}")
    
    def extract_reel_id(self, url: str) -> str:
        """Extract reel ID from Instagram URL for filename"""
        try:
            # Extract reel ID from URL patterns like:
            # https://www.instagram.com/reel/ABC123/
            import re
            match = re.search(r'/(?:reel)/([A-Za-z0-9_-]+)', url)
            if match:
                return match.group(1)
            else:
                # Fallback: use timestamp
                return f"reel_{int(datetime.now().timestamp())}"
        except:
            return f"reel_{int(datetime.now().timestamp())}"
    
    def download_video(self, url: str, reel_id: str = None) -> Optional[str]:
        """
        Download video using yt-dlp with maximum quality
        
        Args:
            url: Instagram reel URL
            reel_id: Reel ID for filename (optional)
            
        Returns:
            Path to downloaded file or None if download fails
        """
        try:
            if not reel_id:
                reel_id = self.extract_reel_id(url)
            
            # Create unique output path to avoid parallel processing conflicts
            timestamp = int(time.time() * 1000)  # Millisecond precision
            safe_reel_id = f"{reel_id}_{timestamp}"
            output_path = os.path.join(self.download_dir, f"{safe_reel_id}.%(ext)s")
            
            if not getattr(config, 'MINIMAL_OUTPUT', True):
                self.logger.info(f"🎬 Starting video download from: {url}")
            else:
                self.logger.info(f"⬇️ Downloading: {reel_id}")
            self.logger.debug(f"📁 Download directory: {self.download_dir}")
            self.logger.debug(f"📝 Output path template: {output_path}")
            self.logger.debug(f"🆔 Reel ID: {reel_id}")
            
            # Ensure download directory exists
            os.makedirs(self.download_dir, exist_ok=True)
            self.logger.debug(f"✅ Download directory ensured: {self.download_dir}")
            
            # Check if cookies.txt exists
            cookies_file = os.path.join(os.path.dirname(__file__), 'cookies.txt')
            if os.path.exists(cookies_file):
                cookies_size = os.path.getsize(cookies_file)
                self.logger.debug(f"🍪 Found cookies.txt ({cookies_size:,} bytes)")
            else:
                self.logger.warning("⚠️  cookies.txt not found - download may fail due to authentication")
            
            # yt-dlp command with maximum quality settings
            cmd = [
                'yt-dlp',
                url,
                '-o', output_path,
                '--format', 'best[ext=mp4]/best',  # Best quality mp4, fallback to best available
                '--merge-output-format', 'mp4',
                '--recode-video', 'mp4',
                '--no-warnings',
                '--no-playlist',
                '--embed-metadata',   # Embed metadata
                '--add-metadata',     # Add metadata
            ]
            
            # Use cookies.txt for authentication if it exists
            if os.path.exists(cookies_file):
                cmd.extend(['--cookies', cookies_file])
                self.logger.debug(f"🔐 Using cookies from: {cookies_file}")
            
            self.logger.debug(f"🔧 Full yt-dlp command: {' '.join(cmd)}")
            if not getattr(config, 'MINIMAL_OUTPUT', True):
                self.logger.info(f"⚡ Executing yt-dlp download...")
            
            # Execute the download
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.DOWNLOAD_TIMEOUT
            )
            
            self.logger.debug(f"� yt-dlp return code: {result.returncode}")
            
            # Log output with proper formatting
            if result.stdout.strip():
                self.logger.debug(f"� yt-dlp stdout:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.logger.debug(f"    {line}")
                        
            if result.stderr.strip():
                if result.returncode == 0:
                    self.logger.debug(f"� yt-dlp stderr (info):")
                else:
                    self.logger.error(f"❌ yt-dlp stderr (error):")
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        if result.returncode == 0:
                            self.logger.debug(f"    {line}")
                        else:
                            self.logger.error(f"    {line}")
            
            if result.returncode == 0:
                self.logger.info(f"✅ yt-dlp download completed successfully")
                
                # Find the actual downloaded file
                self.logger.debug(f"🔍 Searching for downloaded files in: {self.download_dir}")
                downloaded_files = []
                
                # List all files in download directory for debugging
                try:
                    all_files = os.listdir(self.download_dir)
                    self.logger.debug(f"📂 All files in download directory ({len(all_files)} total):")
                    for file in all_files:
                        file_path = os.path.join(self.download_dir, file)
                        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                        self.logger.debug(f"    📄 {file} ({file_size:,} bytes)")
                        
                        # Look for files matching the base reel_id (ignoring timestamp suffix)
                        if file.startswith(reel_id) and file.endswith('.mp4'):
                            downloaded_files.append(file)
                            self.logger.info(f"✅ Found matching video file: {file}")
                            
                except Exception as e:
                    self.logger.error(f"❌ Cannot list download directory: {e}")
                    return None
                
                if downloaded_files:
                    final_path = os.path.join(self.download_dir, downloaded_files[0])
                    final_size = os.path.getsize(final_path)
                    self.logger.info(f"🎉 Download successful!")
                    self.logger.info(f"📁 File path: {final_path}")
                    self.logger.info(f"📏 File size: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
                    return final_path
                else:
                    self.logger.error("❌ Download completed but no matching file found")
                    return None
            else:
                self.logger.error(f"❌ Download failed with return code: {result.returncode}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ Download timeout ({config.DOWNLOAD_TIMEOUT}s) for: {url}")
            return None
        except Exception as e:
            self.logger.error(f"💥 Error downloading video from {url}: {str(e)}")
            return None
    
    def upload_file_to_drive(self, file_path: str, filename: str = None) -> Optional[str]:
        """
        Upload file to Google Drive
        
        Args:
            file_path: Path to local file
            filename: Custom filename (optional)
            
        Returns:
            File ID if upload successful, None otherwise
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"❌ File does not exist: {file_path}")
                return None
            
            if not filename:
                filename = os.path.basename(file_path)
            
            file_size = os.path.getsize(file_path)
            if not getattr(config, 'MINIMAL_OUTPUT', True):
                self.logger.info(f"☁️  Starting Google Drive upload")
            else:
                self.logger.info(f"⬆️ Uploading: {os.path.basename(file_path)}")
            self.logger.debug(f"📁 Local file: {file_path}")
            self.logger.debug(f"📝 Drive filename: {filename}")
            self.logger.debug(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            self.logger.debug(f"📂 Target folder ID: {self.drive_folder_id}")
            
            # File metadata
            file_metadata = {
                'name': filename,
            }
            
            # Add to specific folder if specified
            if self.drive_folder_id:
                file_metadata['parents'] = [self.drive_folder_id]
                self.logger.debug(f"📂 Will upload to folder: {self.drive_folder_id}")
            else:
                self.logger.debug(f"📂 Will upload to root directory")
            
            # Create media upload with smaller chunks for better reliability
            self.logger.debug(f"🔧 Creating media upload with 256KB chunks for reliability...")
            media = MediaFileUpload(
                file_path,
                resumable=True,
                chunksize=256*1024  # 256KB chunks for better reliability over network
            )
            
            # Upload file with tqdm progress bar and retry logic
            self.logger.debug(f"📤 Starting upload request...")
            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size'
            )
            
            file_info = None
            pbar = None
            max_retries = 3
            retry_count = 0
            
            # Initialize progress bar if enabled
            if getattr(config, 'SHOW_PROGRESS_BARS', True):
                desc = "Uploading" if getattr(config, 'MINIMAL_OUTPUT', True) else f"Uploading {filename}"
                pbar = tqdm(
                    total=100,
                    desc=desc,
                    unit="%",
                    ncols=80,
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}% [{elapsed}<{remaining}]'
                )
            
            try:
                self.logger.debug(f"🔄 Starting chunked upload...")
                while file_info is None and retry_count <= max_retries:
                    try:
                        status, file_info = request.next_chunk()
                        if status and pbar:
                            progress = int(status.progress() * 100)
                            # Update progress bar properly
                            pbar.n = progress
                            pbar.set_postfix({'status': 'uploading'})
                            pbar.refresh()
                    except Exception as chunk_error:
                        # Handle SSL/network errors with retry logic
                        error_str = str(chunk_error).lower()
                        if any(term in error_str for term in ["ssl", "cipher", "decryption", "network", "timeout"]):
                            retry_count += 1
                            if retry_count <= max_retries:
                                self.logger.warning(f"⚠️  SSL/Network error (attempt {retry_count}/{max_retries}), retrying...")
                                if pbar:
                                    pbar.set_postfix({'status': f'retry {retry_count}'})
                                    pbar.refresh()
                                time.sleep(retry_count * 2)  # Exponential backoff
                                continue
                            else:
                                self.logger.error(f"❌ Max retries exceeded for SSL/Network errors")
                                raise chunk_error
                        else:
                            raise chunk_error
            finally:
                if pbar:
                    pbar.n = 100
                    pbar.set_postfix({'status': 'complete'})
                    pbar.refresh()
                    pbar.close()
            
            if file_info:
                uploaded_size = file_info.get('size', 'Unknown')
                if uploaded_size != 'Unknown':
                    size_mb = int(uploaded_size) / (1024 * 1024)
                    size_text = f"{size_mb:.2f} MB"
                else:
                    size_text = "Unknown size"
                
                # Beautiful success message
                # Success message - always show but adjust format for minimal output
                if getattr(config, 'MINIMAL_OUTPUT', True):
                    self.logger.info(f"✅ Uploaded: {file_info['name']} ({size_text})")
                else:
                    self.logger.info("┌─" + "─" * 60 + "┐")
                    self.logger.info("│" + " " * 20 + "🎉 UPLOAD SUCCESSFUL!" + " " * 19 + "│")
                    self.logger.info("├─" + "─" * 60 + "┤")
                    self.logger.info(f"│ ☁️  File ID: {file_info['id']:<45} │")
                    self.logger.info(f"│ 📝 Filename: {file_info['name']:<45} │")
                    self.logger.info(f"│ 📏 Size: {size_text:<49} │")
                    self.logger.info("└─" + "─" * 60 + "┘")
                return file_info['id']
            else:
                self.logger.error("❌ Upload failed - no file info returned")
                return None
                
        except HttpError as e:
            error_message = str(e)
            self.logger.error(f"❌ Google Drive API error: {error_message}")
            
            # Special handling for storage quota error
            if "Service Accounts do not have storage quota" in error_message:
                self.logger.error("🚨 STORAGE QUOTA ERROR DETECTED!")
                self.logger.error("📋 This error means you're using service account credentials,")
                self.logger.error("   but service accounts don't have storage quota.")
                self.logger.error("💡 SOLUTION: The application has been updated to use OAuth2.")
                self.logger.error("   Delete 'token.pickle' if it exists and run again.")
                self.logger.error("   You'll be prompted to sign in with your Google account.")
            elif "storageQuotaExceeded" in error_message:
                self.logger.error("💾 Your Google Drive storage is full!")
                self.logger.error("💡 Please free up space in your Google Drive and try again.")
            
            return None
        except Exception as e:
            self.logger.error(f"💥 Error uploading file {file_path}: {str(e)}")
            return None
    
    def download_and_upload(self, url: str, reel_id: str = None) -> Optional[str]:
        """
        Download video locally and upload to Google Drive
        
        Args:
            url: Instagram reel URL
            reel_id: Reel ID for filename
            
        Returns:
            File ID if upload successful, None otherwise
        """
        local_file = None
        
        try:
            if not reel_id:
                reel_id = self.extract_reel_id(url)
            
            filename = f"{reel_id}.mp4"
            
            self.logger.info(f"🔄 Starting download and upload workflow")
            self.logger.debug(f"🔗 URL: {url}")
            self.logger.debug(f"🆔 Reel ID: {reel_id}")
            self.logger.debug(f"📝 Filename: {filename}")
            
            # Download locally then upload
            self.logger.info("📥 Downloading locally then uploading...")
            local_file = self.download_video(url, reel_id)
            
            if not local_file:
                self.logger.error("❌ Local download failed")
                return None
            
            self.logger.debug(f"✅ Local download successful: {local_file}")
            
            # Upload to Drive
            self.logger.info("📤 Starting upload to Google Drive...")
            file_id = self.upload_file_to_drive(local_file, filename)
            
            if file_id:
                self.logger.info(f"✅ Full workflow successful! File ID: {file_id}")
                
                # Clean up local file if requested
                if self.delete_local and local_file:
                    try:
                        # Wait a bit for file handles to close
                        time.sleep(0.5)
                        if os.path.exists(local_file):
                            os.unlink(local_file)
                            self.logger.debug(f"🗑️  Deleted local file: {local_file}")
                    except Exception as cleanup_error:
                        self.logger.warning(f"⚠️  Failed to delete local file: {cleanup_error}")
            else:
                self.logger.error("❌ Upload to Google Drive failed")
            
            return file_id
            
        except Exception as e:
            self.logger.error(f"💥 Error in download_and_upload for {url}: {str(e)}")
            return None
        finally:
            # Ensure cleanup even if upload fails
            if local_file and os.path.exists(local_file) and self.delete_local:
                try:
                    # Wait for any file handles to be released
                    time.sleep(1)
                    os.unlink(local_file)
                    self.logger.debug(f"🗑️  Final cleanup of local file: {local_file}")
                except Exception as final_cleanup_error:
                    self.logger.warning(f"⚠️  Final cleanup failed: {final_cleanup_error}")
    
    def cleanup_downloaded_files(self, successful_uploads: List[str] = None, force_cleanup: bool = False):
        """
        Clean up downloaded files after successful uploads or force cleanup all files.
        
        Args:
            successful_uploads: List of reel IDs that were successfully uploaded
            force_cleanup: If True, clean up all downloaded files regardless of upload status
        """
        try:
            if not os.path.exists(self.download_dir):
                self.logger.debug("📂 Download directory doesn't exist, nothing to clean")
                return
            
            files_cleaned = 0
            files_failed = 0
            
            # Get all files in download directory
            try:
                all_files = os.listdir(self.download_dir)
                if not all_files:
                    self.logger.debug("📂 Download directory is empty")
                    return
                
                self.logger.info(f"🧹 Starting cleanup of downloaded files...")
                self.logger.debug(f"📂 Found {len(all_files)} files in download directory")
                
                for filename in all_files:
                    file_path = os.path.join(self.download_dir, filename)
                    
                    # Skip if not a video file
                    if not filename.endswith('.mp4'):
                        continue
                    
                    should_delete = force_cleanup
                    
                    # If we have a list of successful uploads, only delete those
                    if successful_uploads and not force_cleanup:
                        # Extract reel ID from filename (remove timestamp suffix)
                        reel_id = filename.split('_')[0].replace('.mp4', '')
                        should_delete = reel_id in successful_uploads
                    
                    if should_delete:
                        try:
                            # Multiple attempts with increasing delays
                            max_attempts = 5
                            for attempt in range(max_attempts):
                                try:
                                    # Force garbage collection to release any handles
                                    import gc
                                    gc.collect()
                                    
                                    # Wait progressively longer between attempts
                                    if attempt > 0:
                                        wait_time = attempt * 2
                                        self.logger.debug(f"🕐 Waiting {wait_time}s before cleanup attempt {attempt + 1}")
                                        time.sleep(wait_time)
                                    
                                    # Try to delete the file
                                    if os.path.exists(file_path):
                                        os.unlink(file_path)
                                        files_cleaned += 1
                                        self.logger.debug(f"🗑️  Cleaned: {filename}")
                                        break
                                    else:
                                        self.logger.debug(f"📄 File already deleted: {filename}")
                                        break
                                        
                                except PermissionError as pe:
                                    if attempt == max_attempts - 1:
                                        self.logger.warning(f"⚠️  Permission denied cleaning {filename} after {max_attempts} attempts")
                                        files_failed += 1
                                    else:
                                        self.logger.debug(f"🔒 Permission denied for {filename}, attempt {attempt + 1}")
                                        
                                except Exception as e:
                                    if attempt == max_attempts - 1:
                                        self.logger.warning(f"⚠️  Failed to clean {filename}: {e}")
                                        files_failed += 1
                                    else:
                                        self.logger.debug(f"❌ Error cleaning {filename}, attempt {attempt + 1}: {e}")
                        
                        except Exception as e:
                            self.logger.warning(f"⚠️  Error processing cleanup for {filename}: {e}")
                            files_failed += 1
                
                # Summary
                if files_cleaned > 0 or files_failed > 0:
                    status_icon = "✅" if files_failed == 0 else "⚠️"
                    self.logger.info(f"{status_icon} Cleanup complete: {files_cleaned} cleaned, {files_failed} failed")
                else:
                    self.logger.debug("📂 No files needed cleanup")
                    
            except Exception as e:
                self.logger.error(f"💥 Error during directory cleanup: {e}")
                
        except Exception as e:
            self.logger.error(f"💥 Error in cleanup_downloaded_files: {e}")

    def cleanup_all_downloads(self):
        """Force cleanup of all downloaded files (useful for batch cleanup)"""
        self.cleanup_downloaded_files(force_cleanup=True)


if __name__ == "__main__":
    # Allow running this module standalone for testing
    logger.info("This module should be used via main_processor.py")
    logger.info("For Google Drive uploads, use: python main_processor.py uploads")
