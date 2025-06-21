# IG to YT - n8n Integration Guide

Simple guide for connecting Google Sheets data to n8n workflow.

## Sheet Structure

The tool saves data with these columns:

1. **Timestamp** - Collection time
2. **Reel URL** - Full IG link
3. **Reel ID** - Unique identifier
4. **Status** - "Pending", "Processing", "Completed", or "Error"

## Basic n8n Setup

### 1. Find Pending Links

Create a Google Sheets node to find new links:

```json
{
  "resource": "row",
  "operation": "getAll",
  "documentId": "YOUR_SHEET_ID",
  "sheetName": "Sheet1",
  "options": {
    "filter": {
      "values": {
        "Status": "Pending"
      }
    }
  }
}
```

### 2. Mark as Processing

Before downloading, update status:

```json
{
  "resource": "row",
  "operation": "update",
  "documentId": "YOUR_SHEET_ID",
  "sheetName": "Sheet1",
  "rowId": "={{ $json.row_number }}",
  "columns": {
    "Status": "Processing"
  }
}
```

### 3. Download and Process

Use HTTP Request nodes or specialized IG downloaders.

### 4. Update When Done

After YT upload, mark as completed:

```json
{
  "resource": "row",
  "operation": "update",
  "documentId": "YOUR_SHEET_ID",
  "sheetName": "Sheet1",
  "rowId": "={{ $json.row_number }}",
  "columns": {
    "Status": "Completed",
    "YouTube URL": "={{ $json.youtube_url }}"
  }
}
```

## Status Values

- **Pending** - Ready for processing
- **Processing** - Being handled by n8n
- **Completed** - Successfully uploaded to YT
- **Error** - Failed processing

## Sample Webhook

If using webhooks, this format works well:

```json
{
  "reel_url": "https://www.instagram.com/reel/ABC123/",
  "reel_id": "ABC123"
}
```

## Ready-Made Workflow

Import `workflow.json` into n8n for a working example that:

1. Checks for new links every day
2. Processes each one
3. Uploads to YT
4. Updates status
