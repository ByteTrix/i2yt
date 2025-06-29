#!/usr/bin/env python3
"""
Instagram Reel Processing Runner
Provides different execution modes for the Instagram reel processing workflow
"""

import sys
import logging
import argparse
from datetime import datetime
from instagram_scraper import InstagramReelScraper

# Remove logging configuration - let instagram_scraper handle it
# The instagram_scraper module will configure logging properly
logger = logging.getLogger(__name__)

def run_scraping_only():
    """Run only Instagram scraping (collect links and save to sheets)"""
    try:
        start_time = datetime.now()
        logger.info("🔍 Starting scraping workflow")

        scraper = InstagramReelScraper()
        scraped_links = scraper.run_scraping()
        
        elapsed = datetime.now() - start_time
        logger.info(f"✅ Scraping completed! {len(scraped_links)} reels in {elapsed.total_seconds():.1f}s")
        return scraped_links
        
    except Exception as e:
        logger.error(f"Error in scraping-only mode: {str(e)}")
        return []

def run_descriptions_only():
    """Run only description extraction for existing reels"""
    try:
        logger.info("Running descriptions-only mode")
        from main_processor import run_descriptions_only as process_descriptions
        
        process_descriptions()
        logger.info("Description extraction completed")
        
    except Exception as e:
        logger.error(f"Error in descriptions-only mode: {str(e)}")

def run_uploads_only():
    """Run only Google Drive uploads for pending reels"""
    try:
        logger.info("Running uploads-only mode")
        from main_processor import run_uploads_only as process_uploads
        
        process_uploads()
        logger.info("Upload processing completed")
        
    except Exception as e:
        logger.error(f"Error in uploads-only mode: {str(e)}")

def run_full_workflow():
    """Run complete workflow: scraping + descriptions + uploads"""
    try:
        start_time = datetime.now()
        logger.info("🚀 Starting full workflow")
        
        scraper = InstagramReelScraper()
        scraper.run_full_workflow()
        
        elapsed = datetime.now() - start_time
        logger.info(f"✅ Full workflow completed in {elapsed.total_seconds():.1f}s")
        
    except Exception as e:
        logger.error(f"Error in full workflow mode: {str(e)}")

def run_processing_only():
    """Run only processing (descriptions + uploads) for existing data"""
    try:
        logger.info("Running processing-only mode (no new scraping)")
        from main_processor import InstagramProcessor
        
        processor = InstagramProcessor()
        processor.run_full_workflow()
        
        logger.info("Processing workflow completed")
        
    except Exception as e:
        logger.error(f"Error in processing-only mode: {str(e)}")

def show_status():
    """Show current status of the system"""
    try:
        logger.info("Checking system status...")
        from google_sheets_manager import GoogleSheetsManager
        import config
        
        sheets_manager = GoogleSheetsManager()
        
        # Get status counts
        pending_rows = sheets_manager.get_rows_by_status("pending")
        processing_rows = sheets_manager.get_rows_by_status("processing")
        
        # Get URLs without descriptions
        urls_without_desc = sheets_manager.get_urls_without_descriptions()
        
        # System status summary
        logger.info(f"System status - Pending uploads: {len(pending_rows)}, Processing: {len(processing_rows)}, Missing descriptions: {len(urls_without_desc)}")
        
        # Configuration summary
        desc_status = "ENABLED" if config.EXTRACT_DESCRIPTIONS else "DISABLED"
        upload_status = "ENABLED" if config.UPLOAD_TO_GOOGLE_DRIVE else "DISABLED"
        parallel_status = "ENABLED" if config.ENABLE_CONCURRENT_PROCESSING else "DISABLED"
        
        logger.info(f"Configuration - Descriptions: {desc_status}, Uploads: {upload_status}, Parallel: {parallel_status}")
        logger.info(f"Target URLs: {len(config.INSTAGRAM_URLS)}, Workers: {getattr(config, 'MAX_SCRAPING_WORKERS', 4)} scraping, {getattr(config, 'MAX_UPLOAD_WORKERS', 2)} upload, {getattr(config, 'MAX_DESCRIPTION_WORKERS', 5)} description")
        
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Instagram Reel Processing Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py                    # Run full workflow
  python run_scraper.py --mode scraping    # Only scrape Instagram
  python run_scraper.py --mode descriptions # Only extract descriptions
  python run_scraper.py --mode uploads     # Only upload to Drive
  python run_scraper.py --mode processing  # Only process existing data
  python run_scraper.py --status           # Show system status
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'scraping', 'descriptions', 'uploads', 'processing'],
        default='full',
        help='Execution mode (default: full)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit'
    )
    
    args = parser.parse_args()
    
    # Show status if requested
    if args.status:
        show_status()
        return
    
    # Execute based on mode
    if args.mode == 'full':
        run_full_workflow()
    elif args.mode == 'scraping':
        run_scraping_only()
    elif args.mode == 'descriptions':
        run_descriptions_only()
    elif args.mode == 'uploads':
        run_uploads_only()
    elif args.mode == 'processing':
        run_processing_only()

if __name__ == "__main__":
    main()
