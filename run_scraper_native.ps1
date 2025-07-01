# Pure PowerShell implementation without embedded Python code
# Set window title and clear screen
$Host.UI.RawUI.WindowTitle = "Instagram Reel Scraper"
Clear-Host

#region Helper Functions

function Invoke-PythonModule {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Module,
        
        [Parameter(Mandatory=$true)]
        [string]$Function,
        
        [Parameter(Mandatory=$false)]
        [string[]]$Args = @(),
        
        [Parameter(Mandatory=$false)]
        [string]$ErrorMessage = "Python execution failed"
    )
    
    try {
        $argString = if ($Args.Count -gt 0) { "'" + ($Args -join "', '") + "'" } else { "" }
        $pythonScript = "from $Module import $Function; $Function($argString)"
        
        $result = python -c $pythonScript 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            return $result
        } else {
            Write-Host "$ErrorMessage (Exit code: $LASTEXITCODE)" -ForegroundColor Red
            return $null
        }
    }
    catch {
        Write-Host "$ErrorMessage : $_" -ForegroundColor Red
        return $null
    }
}

function Show-ConfigDisplay {
    Write-Host "📊 Reading configuration..." -ForegroundColor Yellow
    
    try {
        # Read config values using simple python commands
        $urlCount = python -c "import config; print(len(config.INSTAGRAM_URLS))" 2>$null
        $targetLinks = python -c "import config; print(config.TARGET_LINKS)" 2>$null
        $daysLimit = python -c "import config; print(config.DAYS_LIMIT)" 2>$null
        $headless = python -c "import config; print(config.HEADLESS)" 2>$null
        $fastMode = python -c "import config; print(config.FAST_MODE)" 2>$null
        $batchSize = python -c "import config; print(config.BATCH_SIZE)" 2>$null
        $maxScrolls = python -c "import config; print(config.MAX_SCROLLS)" 2>$null
        $scrollDelay = python -c "import config; print(config.SCROLL_DELAY)" 2>$null
        
        Write-Host ""
        Write-Host "📊 Instagram URLs: $urlCount configured" -ForegroundColor Green
        Write-Host "🎯 Target links per URL: $targetLinks" -ForegroundColor Green
        Write-Host "📅 Days limit: $daysLimit days" -ForegroundColor Green
        Write-Host "👻 Headless mode: $headless" -ForegroundColor Green
        Write-Host "⚡ Fast mode: $fastMode" -ForegroundColor Green
        Write-Host "📦 Batch size: $batchSize" -ForegroundColor Green
        Write-Host "🔄 Max scrolls: $maxScrolls" -ForegroundColor Green
        Write-Host "⏱️  Scroll delay: ${scrollDelay}s" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "📱 Configured URLs:" -ForegroundColor Cyan
        
        $urls = python -c "import config; [print(f'{i+1}. {url}') for i, url in enumerate(config.INSTAGRAM_URLS)]" 2>$null
        if ($urls) {
            $urls | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
        }
        
        Write-Host ""
        Write-Host "📈 Google Sheets Rate Limiting:" -ForegroundColor Cyan
        
        $maxCalls = python -c "import config; print(config.SHEETS_MAX_CALLS_PER_MINUTE)" 2>$null
        $retryAttempts = python -c "import config; print(config.SHEETS_RETRY_ATTEMPTS)" 2>$null
        $retryDelay = python -c "import config; print(config.SHEETS_BASE_RETRY_DELAY)" 2>$null
        
        Write-Host "  Max calls/minute: $maxCalls" -ForegroundColor White
        Write-Host "  Retry attempts: $retryAttempts" -ForegroundColor White
        Write-Host "  Base retry delay: ${retryDelay}s" -ForegroundColor White
    }
    catch {
        Write-Host "❌ Error reading configuration: $_" -ForegroundColor Red
    }
}

function Start-ProcessMissingDescriptions {
    Write-Host "🔍 Starting description extraction..." -ForegroundColor Yellow
    
    try {
        python -c "from main_processor import InstagramProcessor; processor = InstagramProcessor(); processor.process_missing_descriptions()"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Description extraction completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Description extraction failed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error during description extraction: $_" -ForegroundColor Red
    }
}

function Start-ProcessPendingUploads {
    Write-Host "📤 Starting upload process..." -ForegroundColor Yellow
    
    try {
        python -c "from main_processor import InstagramProcessor; processor = InstagramProcessor(); processor.process_pending_uploads()"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Upload process completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Upload process failed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error during upload process: $_" -ForegroundColor Red
    }
}

function Start-FullWorkflow {
    Write-Host "🔄 Starting full workflow..." -ForegroundColor Yellow
    
    try {
        python -c "from main_processor import InstagramProcessor; processor = InstagramProcessor(); processor.run_full_workflow()"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Full workflow completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Full workflow failed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error during full workflow: $_" -ForegroundColor Red
    }
}

function Show-GoogleSheetsStatus {
    Write-Host "📊 Checking Google Sheets status..." -ForegroundColor Yellow
    
    try {
        python -c @"
from google_sheets_manager import GoogleSheetsManager
try:
    sheets = GoogleSheetsManager()
    all_data = sheets.get_all_data()
    
    if all_data:
        total_rows = len(all_data) - 1
        print(f'📊 Total reels in sheet: {total_rows}')
        
        status_counts = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'other': 0}
        
        for row in all_data[1:]:
            if len(row) > 5:
                status = row[5].lower() if row[5] else 'pending'
                if status in status_counts:
                    status_counts[status] += 1
                else:
                    status_counts['other'] += 1
        
        print('📈 Status breakdown:')
        print(f'  🟡 Pending: {status_counts["pending"]}')
        print(f'  🔵 Processing: {status_counts["processing"]}')
        print(f'  🟢 Completed: {status_counts["completed"]}')
        print(f'  🔴 Failed: {status_counts["failed"]}')
        if status_counts['other'] > 0:
            print(f'  ⚪ Other: {status_counts["other"]}')
        
        print('📅 Recent entries (last 5):')
        recent_rows = all_data[-5:] if len(all_data) > 5 else all_data[1:]
        for i, row in enumerate(recent_rows, 1):
            if len(row) > 3:
                date = row[0] if len(row) > 0 else 'N/A'
                username = row[1] if len(row) > 1 else 'N/A'
                reel_id = row[3] if len(row) > 3 else 'N/A'
                status = row[5] if len(row) > 5 else 'pending'
                print(f'  {i}. {date} | {username} | {reel_id} | {status}')
    else:
        print('⚠️  No data found in Google Sheets')
        
except Exception as e:
    print(f'❌ Error accessing Google Sheets: {e}')
    if 'quota' in str(e).lower():
        print('💡 Tip: Wait a few minutes for quota to reset')
"@
    }
    catch {
        Write-Host "❌ Error checking Google Sheets status: $_" -ForegroundColor Red
    }
}

function Test-GoogleSheetsConnection {
    Write-Host "🔗 Testing Google Sheets connection..." -ForegroundColor Yellow
    
    try {
        python -c @"
from google_sheets_manager import GoogleSheetsManager
import time

print('🔗 Connecting to Google Sheets...')
start_time = time.time()

try:
    sheets = GoogleSheetsManager()
    connection_time = time.time() - start_time
    print(f'✅ Connection successful! ({connection_time:.2f}s)')
    
    print('📊 Testing data retrieval...')
    all_data = sheets.get_all_data()
    
    if all_data:
        print(f'✅ Data retrieval successful! ({len(all_data)} rows)')
        print(f'📋 Headers: {all_data[0] if all_data else "No headers found"}')
        print(f'🗂️  Cache status: {len(sheets._url_cache)} URLs cached')
    else:
        print('⚠️  No data retrieved (sheet might be empty)')
    
    print('✅ All tests passed!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    if 'quota' in str(e).lower():
        print('💡 This is likely a temporary quota limit. Wait and try again.')
    elif 'permission' in str(e).lower():
        print('💡 Check that credentials.json has proper permissions.')
    elif 'not found' in str(e).lower():
        print('💡 Check that the Google Sheets ID in config.py is correct.')
"@
    }
    catch {
        Write-Host "❌ Error during connection test: $_" -ForegroundColor Red
    }
}

function Remove-DownloadedFiles {
    Write-Host "🗑️  Cleaning downloaded files..." -ForegroundColor Yellow
    $cleanedItems = @()
    
    # Clean downloaded_reels directory
    if (Test-Path "downloaded_reels") {
        try {
            $fileCount = (Get-ChildItem "downloaded_reels" -Recurse -File).Count
            Remove-Item "downloaded_reels" -Recurse -Force
            $cleanedItems += "downloaded_reels directory ($fileCount files)"
        }
        catch {
            Write-Host "⚠️  Warning: Could not remove some files in downloaded_reels" -ForegroundColor Yellow
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
            Write-Host "⚠️  Warning: Could not remove some MP4 files" -ForegroundColor Yellow
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
            Write-Host "⚠️  Warning: Could not remove some JSON files" -ForegroundColor Yellow
        }
    }
    
    if ($cleanedItems.Count -gt 0) {
        foreach ($item in $cleanedItems) {
            Write-Host "✅ Cleaned: $item" -ForegroundColor Green
        }
    } else {
        Write-Host "ℹ️  No files found to clean" -ForegroundColor Yellow
    }
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
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
}
catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
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
        Write-Host "✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ ERROR: Missing required files. Cannot continue." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "✅ All checks passed!" -ForegroundColor Green
Write-Host ""

# Main menu loop
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
            Write-Host "🚀 Starting Instagram Scraper (Full Mode)..." -ForegroundColor Green
            Write-Host "This will scrape with full date checking enabled." -ForegroundColor White
            Write-Host ""
            python run_scraper.py
            Write-Host ""
            Write-Host "✅ Scraper finished!" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }

        "2" {
            Write-Host ""
            Write-Host "⚡ Starting Instagram Scraper (Fast Mode)..." -ForegroundColor Yellow
            Write-Host "This will skip date checking for faster scraping." -ForegroundColor White
            Write-Host ""
            $env:SKIP_DATE_CHECKING = "True"
            python run_scraper.py
            Remove-Item Env:SKIP_DATE_CHECKING -ErrorAction SilentlyContinue
            Write-Host ""
            Write-Host "✅ Scraper finished!" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }

        "3" {
            Write-Host ""
            Write-Host "📝 Extracting Missing Descriptions..." -ForegroundColor Blue
            Write-Host "This will only extract descriptions for reels that don't have them." -ForegroundColor White
            Write-Host ""
            Start-ProcessMissingDescriptions
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "4" {
            Write-Host ""
            Write-Host "📤 Uploading Pending Videos to Google Drive..." -ForegroundColor Magenta
            Write-Host "This will upload all pending reels to Google Drive." -ForegroundColor White
            Write-Host ""
            Start-ProcessPendingUploads
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "5" {
            Write-Host ""
            Write-Host "🔄 Running Full Processing Workflow (No Scraping)..." -ForegroundColor White
            Write-Host "This will process existing reels: descriptions + uploads + cleanup." -ForegroundColor White
            Write-Host ""
            Start-FullWorkflow
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "6" {
            Write-Host ""
            Write-Host "⚙️  Current Configuration:" -ForegroundColor Blue
            Write-Host ""
            Show-ConfigDisplay
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "7" {
            Write-Host ""
            Write-Host "📊 Checking Google Sheets Status..." -ForegroundColor Green
            Write-Host ""
            Show-GoogleSheetsStatus
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "8" {
            Write-Host ""
            Remove-DownloadedFiles
            Write-Host ""
            Write-Host "✅ Cleanup completed!" -ForegroundColor Green
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "9" {
            Write-Host ""
            Test-GoogleSheetsConnection
            Write-Host ""
            Read-Host "Press Enter to continue"
        }

        "0" {
            Write-Host ""
            Write-Host "👋 Thank you for using Instagram Reel Scraper!" -ForegroundColor Cyan
            exit 0
        }

        default {
            Write-Host ""
            Write-Host "❌ Invalid choice. Please enter 0-9." -ForegroundColor Red
            Write-Host ""
        }
    }
    
    Clear-Host
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "    Instagram Reel Scraper Tool" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
} while ($true)
