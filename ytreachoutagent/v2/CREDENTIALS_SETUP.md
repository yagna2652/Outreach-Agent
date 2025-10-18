# Credentials Setup Guide

## Required Credentials

### 1. Julep API Key ✅
- Already configured in `.env`
- Get from: https://dashboard.julep.ai/

### 2. Google Sheets API

#### Option A: OAuth Playground (Quick Testing)
1. Go to: https://developers.google.com/oauthplayground/
2. In the left panel, find and select: `Google Sheets API v4`
3. Select scope: `https://www.googleapis.com/auth/spreadsheets`
4. Click "Authorize APIs"
5. Sign in with your Google account
6. Click "Exchange authorization code for tokens"
7. Copy the **Access token** (not refresh token)
8. Add to `.env`: `GOOGLE_AUTH_TOKEN=your_access_token_here`

**Note:** OAuth Playground tokens expire after 1 hour. For production, use Service Account.

#### Option B: Service Account (Production)
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create Service Account credentials
5. Download JSON key file
6. Share your spreadsheet with the service account email

#### Get Spreadsheet ID
1. Open your Google Sheet
2. The URL looks like: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. Copy the `SPREADSHEET_ID` part
4. Add to `.env`: `GOOGLE_SPREADSHEET_ID=your_spreadsheet_id`

### 3. APIFY Token
1. Sign up at: https://apify.com/
2. Go to Settings → Integrations → API tokens
3. Create a new API token
4. Add to `.env`: `APIFY_TOKEN=your_apify_token`

### 4. APIFY MCP Server Setup
The APIFY MCP server needs to be running for transcript fetching:

```bash
# Install MCP server globally
npm install -g @apify/mcp-server

# Run the server with your token
APIFY_API_TOKEN=your_apify_token npx @apify/mcp-server
```

Or add to your MCP configuration file (`~/.mcp/config.json`):
```json
{
  "servers": {
    "apify": {
      "command": "npx",
      "args": ["@apify/mcp-server"],
      "env": {
        "APIFY_API_TOKEN": "your_apify_token"
      }
    }
  }
}
```

## Test Your Setup

```bash
# Test API connections
python test_api.py

# Run the full agent setup
python agents/youtube_monitor_agent.py
```

## Troubleshooting

### Google API Errors
- **401 Unauthorized**: Token expired or invalid
- **403 Forbidden**: API not enabled or no access to spreadsheet
- **404 Not Found**: Invalid spreadsheet ID

### APIFY Errors
- **MCP connection failed**: MCP server not running
- **Actor not found**: Check actor ID in task YAML files

### Julep Errors
- **Task validation failed**: Check YAML syntax
- **Tool not found**: Ensure using correct tool types (api_call, integration, system)