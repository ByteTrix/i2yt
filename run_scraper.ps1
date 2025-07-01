# Simple Instagram Reel Scraper Launcher
# Easy-to-use PowerShell script to run the Instagram scraper

# Set window title and clear screen
$Host.UI.RawUI.WindowTitle = "Instagram Reel Scraper"
Clear-Host

#region Helper Functions

function Invoke-PythonScript {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Script,
        
        [Parameter(Mandatory=$false)]
        [string]$ErrorMessage = "Python script execution failed"
    )
    
    try {
        # Create a properly escaped Python script
        $escapedScript = $Script -replace '"', '\"' -replace '`', '``'
        
        # Use python -c with proper quoting
        $result = Invoke-Expression "python -c `"$escapedScript`"" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            return $result
        } else {
            Write-Host "$ErrorMessage (Exit code: $LASTEXITCODE)" -ForegroundColor Red
            if ($result) {
                Write-Host "Details: $result" -ForegroundColor Yellow
            }
            return $null
        }
    }
    catch {
        Write-Host "$ErrorMessage : $_" -ForegroundColor Red
        return $null
    }
}

function Get-ConfigDisplay {
    try {
        # Use a simpler approach with python -c and here-string
        python -c @"
import config
try:
    print('📊 Instagram URLs: {} configured'.format(len(config.INSTAGRAM_URLS)))
    print('🎯 Target links per URL: {}'.format(config.TARGET_LINKS))
    print('📅 Days limit: {} days'.format(config.DAYS_LIMIT))
    print('👻 Headless mode: {}'.format(config.HEADLESS))
    print('⚡ Fast mode: {}'.format(config.FAST_MODE))
    print('📦 Batch size: {}'.format(config.BATCH_SIZE))
    print('🔄 Max scrolls: {}'.format(config.MAX_SCROLLS))
    print('⏱️  Scroll delay: {}s'.format(config.SCROLL_DELAY))
    print()
    print('📱 Configured URLs:')
    for i, url in enumerate(config.INSTAGRAM_URLS, 1):
        print('  {}. {}'.format(i, url))
    print()
    print('📈 Google Sheets Rate Limiting:')
    print('  Max calls/minute: {}'.format(config.SHEETS_MAX_CALLS_PER_MINUTE))
    print('  Retry attempts: {}'.format(config.SHEETS_RETRY_ATTEMPTS))
    print('  Base retry delay: {}s'.format(config.SHEETS_BASE_RETRY_DELAY))
except Exception as e:
    print('Error reading configuration: {}'.format(e))
"@
    }
    catch {
        Write-Host "Failed to read configuration: $_" -ForegroundColor Red
        return $null
    }
}

function Invoke-ProcessMissingDescriptions {
    try {
        python -c @"
from main_processor import InstagramProcessor
try:
    print('Starting description extraction...')
    processor = InstagramProcessor()
    processor.process_missing_descriptions()
    print('Description extraction completed successfully!')
except Exception as e:
    print('Error during description extraction: {}'.format(e))
    import traceback
    traceback.print_exc()
"@
    }
    catch {
        Write-Host "Failed to extract missing descriptions: $_" -ForegroundColor Red
        return $null
    }
}

function Invoke-ProcessPendingUploads {
    try {
        python -c @"
from main_processor import InstagramProcessor
try:
    print('Starting upload process...')
    processor = InstagramProcessor()
    processor.process_pending_uploads()
    print('Upload process completed successfully!')
except Exception as e:
    print('Error during upload process: {}'.format(e))
    import traceback
    traceback.print_exc()
"@
    }
    catch {
        Write-Host "Failed to process pending uploads: $_" -ForegroundColor Red
        return $null
    }
}

function Invoke-FullWorkflow {
    try {
        python -c @"
from main_processor import InstagramProcessor
try:
    print('Starting full workflow...')
    processor = InstagramProcessor()
    processor.run_full_workflow()
    print('Full workflow completed successfully!')
except Exception as e:
    print('Error during full workflow: {}'.format(e))
    import traceback
    traceback.print_exc()
"@
    }
    catch {
        Write-Host "Failed to run full workflow: $_" -ForegroundColor Red
        return $null
    }
}

function Get-GoogleSheetsStatus {
    try {
        python -c @"
from google_sheets_manager import GoogleSheetsManager
import traceback

try:
    sheets = GoogleSheetsManager()
    all_data = sheets.get_all_data()
    
    if all_data:
        total_rows = len(all_data) - 1  # Exclude header
        print('📊 Total reels in sheet: {}'.format(total_rows))
        
        # Count by status
        status_counts = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'other': 0}
        
        for row in all_data[1:]:  # Skip header
            if len(row) > 5:  # Status is in column 6 (index 5)
                status = row[5].lower() if row[5] else 'pending'
                if status in status_counts:
                    status_counts[status] += 1
                else:
                    status_counts['other'] += 1
        
        print()
        print('📈 Status breakdown:')
        print('  🟡 Pending: {}'.format(status_counts['pending']))
        print('  🔵 Processing: {}'.format(status_counts['processing']))
        print('  🟢 Completed: {}'.format(status_counts['completed']))
        print('  🔴 Failed: {}'.format(status_counts['failed']))
        if status_counts['other'] > 0:
            print('  ⚪ Other: {}'.format(status_counts['other']))
        
        # Recent entries
        print()
        print('📅 Recent entries (last 5):')
        recent_rows = all_data[-5:] if len(all_data) > 5 else all_data[1:]
        for i, row in enumerate(recent_rows, 1):
            if len(row) > 3:
                date = row[0] if len(row) > 0 else 'N/A'
                username = row[1] if len(row) > 1 else 'N/A'
                reel_id = row[3] if len(row) > 3 else 'N/A'
                status = row[5] if len(row) > 5 else 'pending'
                print('  {}. {} | {} | {} | {}'.format(i, date, username, reel_id, status))
    else:
        print('⚠️  No data found in Google Sheets')
        
except Exception as e:
    print('❌ Error accessing Google Sheets: {}'.format(e))
    if 'quota' in str(e).lower():
        print('💡 Tip: Wait a few minutes for quota to reset')
"@
    }
    catch {
        Write-Host "Failed to check Google Sheets status: $_" -ForegroundColor Red
        return $null
    }
}

function Test-GoogleSheetsConnection {
    try {
        python -c @"
from google_sheets_manager import GoogleSheetsManager
import time

print('🔗 Connecting to Google Sheets...')
start_time = time.time()

try:
    sheets = GoogleSheetsManager()
    connection_time = time.time() - start_time
    print('✅ Connection successful! ({:.2f}s)'.format(connection_time))
    
    print('📊 Testing data retrieval...')
    all_data = sheets.get_all_data()
    
    if all_data:
        print('✅ Data retrieval successful! ({} rows)'.format(len(all_data)))
        print('📋 Headers: {}'.format(all_data[0] if all_data else 'No headers found'))
        print('🗂️  Cache status: {} URLs cached'.format(len(sheets._url_cache)))
    else:
        print('⚠️  No data retrieved (sheet might be empty)')
    
    print('✅ All tests passed!')
    
except Exception as e:
    print('❌ Test failed: {}'.format(e))
    if 'quota' in str(e).lower():
        print('💡 This is likely a temporary quota limit. Wait and try again.')
    elif 'permission' in str(e).lower():
        print('💡 Check that credentials.json has proper permissions.')
    elif 'not found' in str(e).lower():
        print('💡 Check that the Google Sheets ID in config.py is correct.')
"@
    }
    catch {
        Write-Host "Failed to test Google Sheets connection: $_" -ForegroundColor Red
        return $null
    }
}

function Remove-DownloadedFiles {
    $cleanedItems = @()
    
    # Clean downloaded_reels directory
    if (Test-Path "downloaded_reels") {
        try {
            $fileCount = (Get-ChildItem "downloaded_reels" -Recurse -File).Count
            Remove-Item "downloaded_reels" -Recurse -Force
            $cleanedItems += "downloaded_reels directory ($fileCount files)"
        }
        catch {
            Write-Host "Warning: Could not remove some files in downloaded_reels" -ForegroundColor Yellow
        }
    }
    
    # Clean orphaned MP4 files
    $mp4Files = Get-ChildItem -Filter "*.mp4" -ErrorAction SilentlyContinue
    if ($mp4Files.Count -gt 0) {
        try {
            $mp4Files | Remove-Item -Force
            $cleanedItems += "$($mp4Files.Count) orphaned MP4 files"
        }
        catch {
            Write-Host "Warning: Could not remove some MP4 files" -ForegroundColor Yellow
        }
    }
    
    # Clean backup JSON files
    $jsonFiles = Get-ChildItem -Filter "reel_links_backup_*.json" -ErrorAction SilentlyContinue
    if ($jsonFiles.Count -gt 0) {
        try {
            $jsonFiles | Remove-Item -Force
            $cleanedItems += "$($jsonFiles.Count) backup JSON files"
        }
        catch {
            Write-Host "Warning: Could not remove some JSON files" -ForegroundColor Yellow
        }
    }
    
    return $cleanedItems
}

#endregion

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "    Instagram Reel Scraper Tool" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check required files
Write-Host "Checking required files..." -ForegroundColor Yellow
$requiredFiles = @("run_scraper.py", "config.py", "requirements.txt", "main_processor.py", "google_sheets_manager.py")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "Found: $file" -ForegroundColor Green
    } else {
        Write-Host "Missing: $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: Missing required files. Cannot continue." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "All checks passed!" -ForegroundColor Green
Write-Host ""

# Simple menu
do {
    Write-Host "Select what you want to do:" -ForegroundColor White
    Write-Host ""
    Write-Host "🔄 SCRAPING OPTIONS:" -ForegroundColor Cyan
    Write-Host "  1. Start Instagram Scraper (Full Mode)" -ForegroundColor Green
    Write-Host "  2. Start Instagram Scraper (Fast Mode)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 PROCESSING OPTIONS:" -ForegroundColor Cyan
    Write-Host "  3. Extract Missing Descriptions Only" -ForegroundColor Blue
    Write-Host "  4. Upload Pending Videos to Google Drive" -ForegroundColor Magenta
    Write-Host "  5. Run Full Processing Workflow (No Scraping)" -ForegroundColor White
    Write-Host ""
    Write-Host "⚙️  MANAGEMENT OPTIONS:" -ForegroundColor Cyan
    Write-Host "  6. View Configuration" -ForegroundColor Blue
    Write-Host "  7. View Google Sheets Status" -ForegroundColor Green
    Write-Host "  8. Clean Downloaded Files" -ForegroundColor Red
    Write-Host "  9. Test Google Sheets Connection" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  0. Exit" -ForegroundColor Gray
    Write-Host ""

    $choice = Read-Host "Enter your choice (0-9)"

    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "Starting Instagram Scraper (Full Mode)..." -ForegroundColor Green
            Write-Host "This will scrape with full date checking enabled." -ForegroundColor White
            Write-Host ""
            python run_scraper.py
            Write-Host ""
            Write-Host "Scraper finished!" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }

        "2" {
            Write-Host ""
            Write-Host "Starting Instagram Scraper (Fast Mode)..." -ForegroundColor Yellow
            Write-Host "This will skip date checking for faster scraping." -ForegroundColor White
            Write-Host ""
            $env:SKIP_DATE_CHECKING = "True"
            python run_scraper.py
            Remove-Item Env:SKIP_DATE_CHECKING -ErrorAction SilentlyContinue
            Write-Host ""
            Write-Host "Scraper finished!" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }

        "3" {
            Write-Host ""
            Write-Host "Extracting Missing Descriptions..." -ForegroundColor Blue
            Write-Host "This will only extract descriptions for reels that don't have them." -ForegroundColor White
            Write-Host ""
            Invoke-ProcessMissingDescriptions
            Write-Host ""
            Write-Host "Description extraction finished!" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }

        "4" {
            Write-Host ""
            Write-Host "Uploading Pending Videos to Google Drive..." -ForegroundColor Magenta
            Write-Host "This will upload all pending reels to Google Drive." -ForegroundColor White
            Write-Host ""
            Invoke-ProcessPendingUploads
            Write-Host ""
            Write-Host "Upload process finished!" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }

        "5" {
            Write-Host ""
            Write-Host "Running Full Processing Workflow (No Scraping)..." -ForegroundColor White
            Write-Host "This will process existing reels: descriptions + uploads + cleanup." -ForegroundColor White
            Write-Host ""
            Invoke-FullWorkflow
            Write-Host ""
            Write-Host "Processing workflow finished!" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }

        "6" {
            Write-Host ""
            Write-Host "Current Configuration:" -ForegroundColor Blue
            Write-Host ""
            Get-ConfigDisplay
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "7" {
            Write-Host ""
            Write-Host "Checking Google Sheets Status..." -ForegroundColor Green
            Write-Host ""
            Get-GoogleSheetsStatus
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "8" {
            Write-Host ""
            Write-Host "Cleaning downloaded files..." -ForegroundColor Red
            
            $cleanedItems = Remove-DownloadedFiles
            
            if ($cleanedItems.Count -gt 0) {
                foreach ($item in $cleanedItems) {
                    Write-Host "Cleaned: $item" -ForegroundColor Green
                }
            } else {
                Write-Host "No files found to clean" -ForegroundColor Yellow
            }
            
            Write-Host "Cleanup completed!" -ForegroundColor Green
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "9" {
            Write-Host ""
            Write-Host "Testing Google Sheets Connection..." -ForegroundColor Yellow
            Write-Host ""
            Test-GoogleSheetsConnection
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "0" {
            Write-Host ""
            Write-Host "Thank you for using Instagram Reel Scraper!" -ForegroundColor Cyan
            exit 0
        }

        default {
            Write-Host ""
            Write-Host "Invalid choice. Please enter 0-9." -ForegroundColor Red
            Write-Host ""
        }
    }
    
    Clear-Host
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "    Instagram Reel Scraper Tool" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
} while ($true)