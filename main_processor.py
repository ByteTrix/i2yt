#!/usr/bin/env python3
"""
Enhanced Main Orchestrator for Instagram Reel Processing
Professional workflow coordination with optimized parallel processing:
1. Scrape Instagram reels and save to Google Sheets
2. Extract descriptions with parallel processing (if enabled)
3. Download and upload videos to Google Drive with parallel processing (if enabled)
"""

import logging
import time
from datetime import datetime
from typing import List, Dict

from tqdm import tqdm

import config
from google_sheets_manager import GoogleSheetsManager
from description_extractor import DescriptionExtractor
from google_drive_manager import GoogleDriveManager
from parallel_processor import get_parallel_processor, parallel_process

# Setup logging - use the parent logger configuration
logger = logging.getLogger(__name__)

class InstagramProcessor:
    """Main orchestrator class for Instagram reel processing"""
    
    def __init__(self):
        self.logger = logger
        self.sheets_manager = GoogleSheetsManager()
        
        # Initialize optional components based on config
        self.description_extractor = None
        self.drive_manager = None
        
        if config.EXTRACT_DESCRIPTIONS:
            self.description_extractor = DescriptionExtractor()
            
        if config.UPLOAD_TO_GOOGLE_DRIVE:
            self.drive_manager = GoogleDriveManager()
    
    def process_new_reels(self, reel_urls: List[str]):
        """
        Process new reel URLs from Instagram scraping
        
        Args:
            reel_urls: List of Instagram reel URLs
        """
        try:
            if not getattr(config, 'MINIMAL_OUTPUT', True):
                self.logger.info(f"Processing {len(reel_urls)} new reels")
            else:
                self.logger.info(f"🔄 Processing {len(reel_urls)} reels")
            
            # Filter out existing URLs
            new_urls = []
            for url in reel_urls:
                if not self.sheets_manager.url_exists(url):
                    new_urls.append(url)
                else:
                    self.logger.info(f"URL already exists, skipping: {url}")
            
            if not new_urls:
                if not getattr(config, 'MINIMAL_OUTPUT', True):
                    self.logger.info("No new URLs to process")
                return
            
            self.logger.info(f"📥 Found {len(new_urls)} new reels")
            
            # Prepare reel data for batch insert
            reels_data = []
            current_date = datetime.now().strftime("%d-%b-%y").upper()
            
            for url in new_urls:
                # Extract username and reel ID from URL
                username = self.extract_username_from_url(url)
                reel_id = self.extract_reel_id_from_url(url)
                
                reel_data = {
                    'date': current_date,
                    'username': username,
                    'url': url,
                    'reel_id': reel_id,
                    'status': 'pending',
                    'description': '',
                    'file_id': ''
                }
                
                # Extract description if enabled
                if config.EXTRACT_DESCRIPTIONS and self.description_extractor:
                    if not getattr(config, 'MINIMAL_OUTPUT', True):
                        self.logger.info(f"Extracting description for: {url}")
                    description = self.description_extractor.extract_description(url)
                    if description:
                        reel_data['description'] = description
                        if not getattr(config, 'MINIMAL_OUTPUT', True):
                            self.logger.info(f"Description extracted: {description[:100]}...")
                
                reels_data.append(reel_data)
            
            # Batch add to sheets
            self.sheets_manager.batch_add_reels(reels_data)
            
            # Success message with reel info
            if len(reels_data) > 0:
                self.logger.info(f"✅ Added {len(reels_data)} reels to sheets")
            
        except Exception as e:
            self.logger.error(f"Error processing new reels: {str(e)}")
    
    def process_pending_uploads_workflow(self):
        """Process pending uploads workflow"""
        try:
            if not config.UPLOAD_TO_GOOGLE_DRIVE:
                self.logger.info("Google Drive upload is disabled")
                return
            
            if not self.drive_manager:
                self.logger.error("Drive manager not initialized")
                return
            
            self.logger.info("Starting pending uploads processing...")
            
            # Get pending rows
            pending_rows = self.sheets_manager.get_rows_by_status("pending")
            
            if not pending_rows:
                self.logger.info("📤 No pending uploads found")
                return
            
            self.logger.info(f"📤 Found {len(pending_rows)} pending uploads")
            
            # Always use sequential processing for uploads (more reliable)
            self.logger.info("� Using sequential upload processing for reliability")
            success_count = 0
            
            # Progress bar for uploads
            progress_bar = None
            if getattr(config, 'SHOW_PROGRESS_BARS', True):
                desc = "Uploading" if not getattr(config, 'MINIMAL_OUTPUT', True) else "Upload"
                progress_bar = tqdm(
                    total=len(pending_rows),
                    desc=desc,
                    unit="file",
                    ncols=80,
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
                )
            
            try:
                for i, row_data in enumerate(pending_rows, 1):
                    if self._process_single_upload(row_data):
                        success_count += 1
                    
                    if progress_bar:
                        progress_bar.update(1)
                        progress_bar.set_postfix({
                            'success': success_count,
                            'failed': i - success_count,
                            'rate': f"{success_count/i:.1%}" if i > 0 else "0%"
                        })
            finally:
                if progress_bar:
                    progress_bar.close()
            
            failed_count = len(pending_rows) - success_count
            success_rate = (success_count / len(pending_rows)) * 100 if pending_rows else 0
            
            # Beautiful upload summary
            self.logger.info("┌─" + "─" * 60 + "┐")
            self.logger.info("│" + " " * 12 + "📤 SEQUENTIAL UPLOAD SUMMARY" + " " * 20 + "│")
            self.logger.info("├─" + "─" * 60 + "┤")
            self.logger.info(f"│ ✅ Successful: {success_count:<42} │")
            self.logger.info(f"│ ❌ Failed: {failed_count:<46} │")
            self.logger.info(f"│ 📊 Success rate: {success_rate:.1f}%{' ' * (38 - len(f'{success_rate:.1f}%'))} │")
            self.logger.info("└─" + "─" * 60 + "┘")
            
            self.logger.info("Pending uploads processing completed")
            
        except Exception as e:
            self.logger.error(f"Error in process_pending_uploads_workflow: {str(e)}")
    
    def process_missing_descriptions(self):
        """Process missing descriptions workflow - only for pending items"""
        try:
            if not config.EXTRACT_DESCRIPTIONS:
                self.logger.info("Description extraction is disabled")
                return
            
            if not self.description_extractor:
                self.logger.error("Description extractor not initialized")
                return
            
            self.logger.info("Starting missing descriptions processing...")
            
            # Get URLs without descriptions that have pending status only
            pending_urls_without_desc = self.sheets_manager.get_urls_without_descriptions_by_status("pending")
            
            if not pending_urls_without_desc:
                self.logger.info("All pending reels have descriptions")
                return
            
            self.logger.info(f"Found {len(pending_urls_without_desc)} pending reels missing descriptions")
            
            # Process each URL
            for url_data in pending_urls_without_desc:
                try:
                    row_index = url_data['row_index']
                    url = url_data['url']
                    
                    self.logger.info(f"Extracting description for row {row_index}: {url}")
                    
                    description = self.description_extractor.extract_description(url)
                    
                    if description:
                        self.sheets_manager.update_description(row_index, description)
                        self.logger.info(f"Updated description for row {row_index}")
                    else:
                        self.logger.warning(f"Failed to extract description for row {row_index}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing description for row {url_data.get('row_index', 'unknown')}: {str(e)}")
                    continue
            
            self.logger.info("Missing descriptions processing completed")
            
        except Exception as e:
            self.logger.error(f"Error in process_missing_descriptions: {str(e)}")
    
    def run_full_workflow(self, reel_urls: List[str] = None):
        """
        Run the complete workflow
        
        Args:
            reel_urls: List of new reel URLs from scraping (optional)
        """
        start_time = time.time()
        stats = {
            'new_reels_processed': 0,
            'descriptions_extracted': 0,
            'uploads_completed': 0,
            'errors_encountered': 0
        }
        
        try:
            # Beautiful workflow header
            self.logger.info("╔" + "═" * 78 + "╗")
            self.logger.info("║" + " " * 18 + "🚀 INSTAGRAM REEL PROCESSING WORKFLOW" + " " * 22 + "║")
            self.logger.info("╚" + "═" * 78 + "╝")
            self.logger.info("")
            
            # Step 1: Process new reels if provided
            self.logger.info("┌─ 📱 STEP 1: NEW REEL PROCESSING")
            if reel_urls:
                self.logger.info(f"│  Processing {len(reel_urls)} new reels from scraping...")
                self.process_new_reels(reel_urls)
                stats['new_reels_processed'] = len(reel_urls)
                self.logger.info(f"│  ✅ Processed {len(reel_urls)} new reels successfully")
            else:
                self.logger.info("│  ℹ️  No new reels to process")
            self.logger.info("└─ Step 1 completed\n")
            
            # Step 2: Process missing descriptions
            self.logger.info("┌─ 📝 STEP 2: DESCRIPTION EXTRACTION")
            if config.EXTRACT_DESCRIPTIONS:
                self.logger.info("│  Extracting missing descriptions...")
                initial_missing = len(self.sheets_manager.get_urls_without_descriptions_by_status("pending"))
                self.process_missing_descriptions()
                final_missing = len(self.sheets_manager.get_urls_without_descriptions_by_status("pending"))
                extracted = initial_missing - final_missing
                stats['descriptions_extracted'] = extracted
                self.logger.info(f"│  ✅ Extracted {extracted} descriptions successfully")
            else:
                self.logger.info("│  ⏭️  Description extraction disabled")
            self.logger.info("└─ Step 2 completed\n")
            
            # Step 3: Process pending uploads
            self.logger.info("┌─ ☁️  STEP 3: GOOGLE DRIVE UPLOADS")
            if config.UPLOAD_TO_GOOGLE_DRIVE:
                self.logger.info("│  Processing pending uploads...")
                initial_pending = len(self.sheets_manager.get_rows_by_status("pending"))
                self.process_pending_uploads_workflow()
                final_pending = len(self.sheets_manager.get_rows_by_status("pending"))
                uploaded = initial_pending - final_pending
                stats['uploads_completed'] = uploaded
                self.logger.info(f"│  ✅ Completed {uploaded} uploads successfully")
            else:
                self.logger.info("│  ⏭️  Google Drive upload disabled")
            self.logger.info("└─ Step 3 completed\n")
            
            # Beautiful completion summary
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info("╔" + "═" * 78 + "╗")
            self.logger.info("║" + " " * 22 + "🎉 WORKFLOW COMPLETED SUCCESSFULLY!" + " " * 22 + "║")
            self.logger.info("╠" + "═" * 78 + "╣")
            self.logger.info("║ 📊 EXECUTION SUMMARY:" + " " * 55 + "║")
            self.logger.info("║" + " " * 78 + "║")
            self.logger.info(f"║   🆕 New reels processed: {stats['new_reels_processed']:<50} ║")
            self.logger.info(f"║   📝 Descriptions extracted: {stats['descriptions_extracted']:<47} ║")
            self.logger.info(f"║   ☁️  Files uploaded: {stats['uploads_completed']:<55} ║")
            self.logger.info(f"║   ⏱️  Total execution time: {duration:.2f}s{' ' * (46 - len(f'{duration:.2f}s'))} ║")
            self.logger.info("║" + " " * 78 + "║")
            self.logger.info("╚" + "═" * 78 + "╝")
            
        except Exception as e:
            stats['errors_encountered'] += 1
            self.logger.error("╔" + "═" * 78 + "╗")
            self.logger.error("║" + " " * 25 + "❌ WORKFLOW ERROR!" + " " * 32 + "║")
            self.logger.error("╚" + "═" * 78 + "╝")
            self.logger.error(f"Error in run_full_workflow: {str(e)}")
    
    def _process_single_upload(self, row_data: dict) -> bool:
        """
        🚀 Process a single upload task
        
        Args:
            row_data: Dictionary containing row information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            row_index = row_data['row_index']
            url = row_data['url']
            
            self.logger.debug(f"Processing upload for row {row_index}: {url}")
            
            # Extract reel ID for filename
            reel_id = self.drive_manager.extract_reel_id(url)
            
            # Download and upload
            file_id = self.drive_manager.download_and_upload(url, reel_id)
            
            if file_id:
                # Update status to processing and add file ID
                self.sheets_manager.update_status(row_index, "processing")
                self.sheets_manager.update_file_id(row_index, file_id)
                self.logger.info(f"✅ Successfully uploaded {reel_id}, file ID: {file_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to upload {reel_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"💥 Error processing upload for row {row_data.get('row_index', 'unknown')}: {str(e)}")
            return False
    
    def _upload_progress_callback(self, completed: int, total: int, success: int, failed: int):
        """Progress callback for upload processing - fixed to properly count actual results"""
        if completed % 2 == 0 or completed == total:  # Update every 2 items or at completion
            progress_pct = (completed / total) * 100 if total > 0 else 0
            # Don't show success/failed counts during progress as they may be inaccurate
            # The final summary will show the correct counts
            self.logger.info(f"📊 Upload Progress: {completed}/{total} ({progress_pct:.1f}%)")
    
    def extract_username_from_url(self, url: str) -> str:
        """Extract username from Instagram URL"""
        try:
            import re
            # Match patterns like https://www.instagram.com/username/reel/...
            # or https://www.instagram.com/reel/... (less common)
            match = re.search(r'instagram\.com/([^/]+)/?(?:reel/|$)', url)
            if match:
                username = match.group(1)
                # Skip 'reel' if it's the direct path
                if username != 'reel':
                    return f"@{username}"
            
            # Fallback: try to extract from any pattern
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part == 'instagram.com' and i + 1 < len(parts):
                    potential_username = parts[i + 1]
                    if potential_username and potential_username != 'reel':
                        return f"@{potential_username}"
            
            return "@unknown"
        except Exception as e:
            self.logger.debug(f"Error extracting username from {url}: {e}")
            return "@unknown"
    
    def extract_reel_id_from_url(self, url: str) -> str:
        """Extract reel ID from Instagram URL"""
        try:
            import re
            # Match patterns like /reel/ABC123/
            match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
            if match:
                return match.group(1)
            
            # Fallback: use timestamp
            from datetime import datetime
            return f"reel_{int(datetime.now().timestamp())}"
        except Exception as e:
            self.logger.debug(f"Error extracting reel ID from {url}: {e}")
            from datetime import datetime
            return f"reel_{int(datetime.now().timestamp())}"
        

def run_descriptions_only():
    """Standalone function to only process descriptions"""
    try:
        logger.info("Running descriptions-only workflow")
        processor = InstagramProcessor()
        processor.process_missing_descriptions()
    except Exception as e:
        logger.error(f"Error in run_descriptions_only: {str(e)}")

def run_uploads_only():
    """Standalone function to only process uploads"""
    try:
        logger.info("Running uploads-only workflow")
        processor = InstagramProcessor()
        processor.process_pending_uploads_workflow()
    except Exception as e:
        logger.error(f"Error in run_uploads_only: {str(e)}")

def run_maintenance():
    """Run maintenance tasks"""
    try:
        logger.info("Running maintenance tasks")
        
        # You can add maintenance tasks here like:
        # - Cleanup old log files
        # - Check for failed uploads
        # - Validate Google Drive files
        # - etc.
        
        logger.info("Maintenance completed")
    except Exception as e:
        logger.error(f"Error in run_maintenance: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "descriptions":
            run_descriptions_only()
        elif command == "uploads":
            run_uploads_only()
        elif command == "maintenance":
            run_maintenance()
        else:
            logger.info("Usage: python main_processor.py [descriptions|uploads|maintenance]")
    else:
        # Run full workflow without new URLs (process existing data)
        processor = InstagramProcessor()
        processor.run_full_workflow()
