# WORKING SOLUTION - API Calls in Julep

## ✅ Confirmed Working Pattern

The `api_call` tool works with this structure:

```yaml
tools:
  - name: tool_name
    type: api_call
    description: Tool description
    api_call:
      method: GET/POST/PUT
      url: "https://complete.url.here"  # Must be complete URL

main:
  - tool: tool_name
    arguments:
      headers:
        Authorization: "Bearer token"
      json:  # For POST/PUT
        key: value
```

## Key Insights

1. **URL must be in tool definition**: The `url` field in `api_call` is required and must be a complete URL
2. **Arguments can include**: headers, json (for body), params (for query parameters)
3. **Return format**: The result is wrapped in a structure with `json`, `content`, `headers`, and `status_code`

## Problem with Dynamic URLs

The challenge is that Google Sheets API requires dynamic URL construction:
- Base: `https://sheets.googleapis.com/v4/spreadsheets/`
- Dynamic: `{spreadsheet_id}/values/{range}`

Since the URL in the tool definition must be static, we have a few options:

### Option 1: Use Function Tool
Create a custom function that makes HTTP requests with dynamic URLs

### Option 2: Use Integration Tool with MCP
Set up a proper MCP server that handles dynamic URLs

### Option 3: Create Multiple Specific Tools
Define separate tools for each specific API endpoint we need

### Option 4: Use Proxy Service
Create a proxy endpoint that accepts parameters and forwards to Google Sheets

## Recommended Approach

For our YouTube Outreach Agent, the best approach is:

1. **For Google Sheets**: Use specific tools for each operation (read A1:F100, update status column, etc.)
2. **For APIFY**: Use MCP integration once server is set up
3. **For other APIs**: Use hardcoded URLs where possible

## Next Steps

1. Create specific Google Sheets tools with fixed ranges
2. Set up APIFY MCP server for transcript fetching
3. Test the complete workflow with real data