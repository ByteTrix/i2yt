# Changelog

## Recent Updates

### Google Drive Service Account Fix (Critical)

#### Issue Addressed
- **Service Account Storage Quota Error**: Fixed the critical issue where Google Drive uploads failed with "Service Accounts do not have storage quota" error
- **Root Cause**: Service accounts cannot upload files to their own Google Drive due to storage limitations

#### Solutions Implemented
1. **Shared Drive Support**: Added configuration for Google Workspace Shared Drives
2. **Personal Drive Folder Sharing**: Enhanced support for sharing personal folders with service accounts
3. **Advanced Upload Settings**: Added timeout, retry, and resumable upload configurations

#### Configuration Updates
- `config_template.py`: Added new Google Drive settings with detailed explanations
- Added `USE_SHARED_DRIVE`, `SHARED_DRIVE_ID`, `UPLOAD_TIMEOUT`, and other advanced settings
- Clear documentation of service account limitations and solutions

#### Documentation Updates
- **Updated README.md**: Added important warning about service account limitations
- **Enhanced troubleshooting.md**: Added comprehensive Google Drive error handling section
- **Updated google_sheets_setup.md**: Added detailed Google Drive setup instructions
- **Updated configuration.md**: Added advanced Google Drive configuration options

### Launcher and Setup Improvements

#### Files Added
- `setup.py` - Automated setup script for easy installation
- Added comprehensive project structure documentation

#### Files Removed
- `Create_Shortcut.ps1` - Removed automated shortcut creation script
- `start_chrome_debug.bat` - Consolidated into main login script

#### Changes Made
- **Updated `Launch_Instagram_Scraper.bat`**: 
  - Fixed PowerShell execution issues
  - Added automatic working directory setting
  - Improved error handling and user guidance
  
- **Enhanced README.md**:
  - Added automated setup instructions using `setup.py`
  - Updated project structure to reflect current files
  - Added clear instructions for batch file path customization
  - Added reference to comprehensive running guide
  
- **Updated Documentation**:
  - `docs/developer_guide.md`: Updated project structure
  - `docs/troubleshooting.md`: Removed references to deleted files
  - `docs/configuration.md`: Cleaned up platform-specific settings
  
#### User Impact
- **Easier Setup**: Users can now run `python setup.py` for automated installation
- **Better Windows Experience**: Batch launcher now works from any location
- **Clearer Instructions**: Updated documentation reflects actual file structure
- **Manual Shortcut Creation**: Users now manually create desktop shortcuts (more reliable)

#### Migration Notes
For existing users:
1. The batch file path must be updated manually (one-time setup)
2. Desktop shortcuts should be recreated manually by right-clicking the batch file
3. No functional changes to the core scraping functionality
