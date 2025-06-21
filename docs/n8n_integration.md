# n8n Integration Guide

Complete guide to setting up n8n workflow automation for processing Instagram reels and uploading to YouTube.

## Overview

This guide shows how to create an end-to-end automation workflow using n8n that:

1. **Monitors** Google Sheets for new Instagram reels
2. **Downloads** reel videos using yt-dlp
3. **Processes** videos (optional: editing, thumbnails)
4. **Uploads** to YouTube automatically
5. **Updates** status in Google Sheets

## Prerequisites

- **n8n instance** (self-hosted or cloud)
- **Google Sheets** set up with Instagram scraper
- **YouTube API** credentials
- **Basic n8n knowledge** (recommended)

## Phase 1: n8n Setup

### Option A: n8n Cloud (Recommended for Beginners)

1. **Sign up** at [n8n.cloud](https://n8n.cloud)
2. **Create** a new workflow
3. **Import** the provided workflow template

### Option B: Self-Hosted n8n

#### Docker Installation
```bash
# Pull and run n8n
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n

# With persistent data
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

#### npm Installation
```bash
# Install n8n globally
npm install n8n -g

# Start n8n
n8n start
```

Access n8n at: `http://localhost:5678`

## Phase 2: Workflow Import

### Import Pre-Built Workflow

1. **Download** the workflow file: `n8n_workflow.json`
2. **Open** n8n interface
3. **Click** "Import from file"
4. **Select** the downloaded JSON file
5. **Click** "Import"

### Manual Workflow Creation

If you prefer to build from scratch, here's the workflow structure:

```
Google Sheets Trigger → Filter New Rows → Download Video → Process Video → YouTube Upload → Update Status
```


## Phase 4: Advanced Features

### Video Processing

Add optional video processing between download and upload:

#### FFmpeg Processing Node
```bash
# Add intro/outro, watermark, or format conversion
ffmpeg -i "{{ $json.downloadPath }}" \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -c:a aac \
  -preset fast -crf 23 \
  "{{ $json.processedPath }}"
```

### Thumbnail Generation

#### Generate Custom Thumbnails
```bash
# Extract frame for thumbnail
ffmpeg -i "{{ $json.downloadPath }}" \
  -ss 00:00:02 -vframes 1 \
  -vf "scale=1280:720" \
  "{{ $json.thumbnailPath }}"
```

### Content Filtering

#### Content Validation Node
```javascript
// Check video duration, content, etc.
const metadata = $node["Download Video"].json;

// Skip if too short
if (metadata.duration < 15) {
  return [{
    json: {
      skip: true,
      reason: 'Video too short (< 15 seconds)'
    }
  }];
}

// Skip if too long
if (metadata.duration > 180) {
  return [{
    json: {
      skip: true,
      reason: 'Video too long (> 3 minutes)'
    }
  }];
}

return [{ json: { valid: true } }];
```

## Phase 5: YouTube API Setup

### Create YouTube API Credentials

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable** YouTube Data API v3
3. **Create** OAuth 2.0 credentials
4. **Download** client secret JSON
5. **Configure** in n8n credentials

### YouTube Upload Configuration

```json
{
  "title": "{{ $json.youtubeTitle }}",
  "description": "{{ $json.youtubeDescription }}",
  "tags": ["instagram", "reels", "shorts", "{{ $json.username }}"],
  "categoryId": "24",
}
```

## Phase 6: Scheduling and Monitoring

### Workflow Scheduling

#### Option 1: Polling Schedule
```json
{
  "triggerInterval": 300,
  "timezone": "America/New_York",
  "skipOnError": true
}
```

#### Option 2: Webhook Trigger
```javascript
// Webhook endpoint for external triggers
const webhookUrl = "https://your-n8n-instance.com/webhook/instagram-upload";

// Call from external system
fetch(webhookUrl, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ trigger: 'new_reels' })
});
```

### Monitoring and Notifications

#### Slack Notifications
```json
{
  "channel": "#automation",
  "text": "✅ Successfully uploaded {{ $json.youtubeTitle }} to YouTube",
  "attachments": [{
    "color": "good",
    "fields": [
      { "title": "Username", "value": "{{ $json.username }}", "short": true },
      { "title": "YouTube URL", "value": "{{ $json.youtubeUrl }}", "short": true }
    ]
  }]
}
```

#### Email Notifications
```json
{
  "to": "admin@yoursite.com",
  "subject": "Instagram to YouTube Upload Report",
  "text": "Processed {{ $json.totalReels }} reels. {{ $json.successCount }} successful, {{ $json.errorCount }} failed."
}
```

## Phase 7: Testing and Deployment

### Test Workflow

1. **Create test data** in Google Sheets
2. **Set status** to "Not Processed"
3. **Run workflow manually**
4. **Verify** each step completes
5. **Check** YouTube upload
6. **Confirm** status update

### Production Deployment

#### Environment Variables for n8n hosting
```bash
# n8n environment configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password

# Database configuration
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=n8n_password

# Webhook configuration
WEBHOOK_URL=https://your-domain.com/
N8N_PROTOCOL=https
N8N_HOST=your-domain.com
```

#### Security Configuration
```bash
# SSL/TLS
N8N_PROTOCOL=https
N8N_SSL_KEY=/path/to/ssl/key.pem
N8N_SSL_CERT=/path/to/ssl/cert.pem

# CORS
N8N_CORS_ORIGIN=https://your-domain.com
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Download fails | Private account | Update status to "Skipped" |
| Upload quota exceeded | YouTube API limits | Implement rate limiting |
| Authentication errors | Expired tokens | Refresh OAuth credentials |
| Video format issues | Unsupported format | Add ffmpeg processing |
| Workflow stops | Unhandled errors | Add error handling nodes |

### Debug Mode

Enable debugging:
```json
{
  "executions": {
    "saveDataOnError": "all",
    "saveDataOnSuccess": "all",
    "saveManualExecutions": true
  },
  "logging": {
    "level": "debug",
    "outputs": ["console", "file"]
  }
}
```

### Performance Optimization

```json
{
  "concurrency": 5,
  "maxConcurrentExecutions": 10,
  "executionTimeout": 3600,
  "maxExecutions": 1000
}
```

## Advanced Workflows

### Multi-Platform Upload

Extend the workflow to upload to multiple platforms:

```
Download → Process → [YouTube Upload, TikTok Upload, Facebook Upload] → Update Status
```

### Content Moderation

Add content checking before upload:

```
Download → Content Analysis → Moderation Check → Upload → Update
```

### Analytics Integration

Track performance across platforms:

```
Upload → Wait → Fetch Analytics → Update Metrics → Generate Report
```

---

**Next Steps:**
- [Advanced Usage](advanced_usage.md) - Power user features
- [Troubleshooting](troubleshooting.md) - Solve workflow issues
- [Developer Guide](developer_guide.md) - Extend functionality
