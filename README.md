# Instagram to YouTube Automation Workflow

This project automates the process of checking Instagram accounts for new reels, downloading them, and uploading to YouTube while tracking processed content in Airtable to avoid duplicates.

## Workflow Overview

### 1. Instagram Reel Checker (`check-instagram.yml`)
- **Schedule**: Runs every 2 hours during active posting times (6 AM - 10 PM IST)
- **Primary Account Check**: First checks your main Instagram account for recent reels
- **Airtable Deduplication**: Verifies if the reel has already been processed
- **Backup Account Fallback**: If no new content from primary account, checks backup account
- **Automatic Trigger**: Triggers the download workflow when new content is found

### 2. Download Workflow (`download.yml`)
- **Media Download**: Downloads the selected reel using yt-dlp
- **Cookie Management**: Uses appropriate cookies based on account type (primary/backup)
- **N8N Integration**: Triggers the n8n webhook with metadata for processing

### 3. N8N Processing (`updated-n8n-workflow.json`)
- **Artifact Processing**: Downloads and extracts media from GitHub Actions
- **AI Enhancement**: Uses Google Gemini to clean and improve video descriptions
- **YouTube Upload**: Uploads processed video to YouTube
- **Airtable Tracking**: Records processed URLs to prevent duplicates

## Setup Instructions

### GitHub Secrets Required

```bash
# Instagram Account Credentials
INSTA_COOKIES              # Cookies for primary Instagram account
BACKUP_INSTA_COOKIES       # Cookies for backup Instagram account
PRIMARY_INSTA_USERNAME     # Username of primary account
BACKUP_INSTA_USERNAME      # Username of backup account

# Airtable Configuration
AIRTABLE_TOKEN            # Personal Access Token from Airtable
AIRTABLE_BASE_ID          # Base ID of your Airtable workspace
AIRTABLE_TABLE_ID         # Table ID where processed URLs are tracked

# N8N Integration
N8N_WEBHOOK_URL          # Your n8n webhook URL
```

### Airtable Setup

Create a table with the following columns:
- `url` (Single line text) - Instagram reel URL
- `Date` (Date) - Processing timestamp
- `account_type` (Single select: primary/backup) - Source account
- `youtube_url` (URL) - YouTube video URL after upload
- `status` (Single select: processed/failed) - Processing status

### N8N Workflow Setup

1. Import the `updated-n8n-workflow.json` into your n8n instance
2. Configure the following credentials:
   - GitHub API access
   - YouTube OAuth2 API
   - Google Gemini API
   - Airtable Personal Access Token
3. Update the webhook URL in your GitHub secrets

## How It Works

### Automatic Detection Flow

1. **Scheduled Check**: Every 2 hours, the checker workflow runs
2. **Primary Account**: Checks your main Instagram account for reels posted in the last 24 hours
3. **Duplicate Check**: Queries Airtable to see if the reel URL has been processed
4. **Backup Account**: If no new content from primary, checks backup account
5. **Trigger Download**: If new content found, triggers download workflow with appropriate cookies

### Processing Flow

1. **Download**: Downloads the selected reel and description
2. **Webhook Trigger**: Sends metadata to n8n including source URL and account type
3. **N8N Processing**:
   - Downloads artifacts from GitHub Actions
   - Extracts video and description files
   - Uses AI to clean up the description
   - Uploads to YouTube
   - Records the processed URL in Airtable

### Manual Triggers

You can manually trigger workflows:

```bash
# Force check both accounts regardless of recent activity
gh workflow run check-instagram.yml -f force_check=true

# Manually download a specific reel
gh workflow run download.yml -f url=https://www.instagram.com/reel/xxxxx -f account_type=primary
```

## File Structure

```
.github/workflows/
├── check-instagram.yml    # Main checker workflow
└── download.yml          # Download and processing workflow

├── insta to yt.json      # Original n8n workflow
├── updated-n8n-workflow.json  # Enhanced n8n workflow
└── README.md            # This documentation
```

## Features

✅ **Automatic Discovery**: Finds new reels without manual intervention  
✅ **Duplicate Prevention**: Tracks processed content in Airtable  
✅ **Multi-Account Support**: Primary and backup Instagram accounts  
✅ **Smart Scheduling**: Runs during active posting hours  
✅ **Cookie Management**: Handles different accounts automatically  
✅ **AI Enhancement**: Improves video descriptions for YouTube  
✅ **Error Handling**: Robust error handling and logging  
✅ **Manual Override**: Force check options for testing  

## Monitoring

- Check GitHub Actions tab for workflow runs
- Monitor Airtable for processed reels
- Review n8n execution logs for processing status
- YouTube Studio for uploaded videos

## Troubleshooting

### Common Issues

1. **Cookie Expiration**: Update Instagram cookies in GitHub secrets
2. **API Rate Limits**: Adjust check frequency if hitting limits
3. **Airtable Permissions**: Ensure token has read/write access
4. **N8N Webhook**: Verify webhook URL is accessible

### Debug Mode

Enable debug logging by setting workflow environment variables:
```yaml
env:
  DEBUG: true
```

## Customization

### Adjust Check Frequency
Modify the cron schedule in `check-instagram.yml`:
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours instead of 2
```

### Change Recent Reel Timeframe
Update the `is_recent_reel` function to check different time periods:
```python
def is_recent_reel(upload_date, hours=48):  # 48 hours instead of 24
```

### Add More Accounts
Extend the checker script to support additional backup accounts by adding more cookie files and account environment variables.
