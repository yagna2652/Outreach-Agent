# YouTube Outreach Agent

An automated system for generating personalized outreach emails to YouTube creators using Julep AI, APIFY, and Google Sheets.

## Features

- **Google Sheets Integration**: Reads creator information from Google Sheets and updates with email drafts
- **YouTube Transcript Extraction**: Uses APIFY to fetch video transcripts
- **AI-Powered Email Generation**: Creates personalized outreach emails based on video content
- **Julep Task Orchestration**: Uses declarative YAML workflows for processing

## Project Structure

```
ytreachoutagent/
├── orchestrator.py          # Main orchestration script
├── single_video_task.yaml   # Julep task definition
├── set_pending.py          # Helper to reset test row
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md             # This file
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ytreachoutagent
   ```

2. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your API keys:
     - `JULEP_API_KEY`: Your Julep API key
     - `APIFY_TOKEN`: Your APIFY API token
     - `GOOGLE_SHEET_ID`: Your Google Sheet ID
     - `AGENT_ID`: Julep agent ID (created during setup)
     - `TASK_ID`: Julep task ID (created automatically)

4. **Set up Google Sheets authentication**
   - Create a Google Cloud service account
   - Download the JSON key file as `service_account.json`
   - Share your Google Sheet with the service account email

5. **Prepare your Google Sheet**
   - Column A: Creator Name
   - Column B: YouTube Video URL
   - Column C: Creator Email
   - Column D: Status (leave empty or set to "Pending")
   - Column E: Email Subject (populated by script)
   - Column F: Email Body (populated by script)

## Usage

1. **Add creators to your Google Sheet**
   - Fill in columns A-C with creator information
   - Leave column D empty or set to "Pending"

2. **Run the orchestrator**
   ```bash
   python orchestrator.py
   ```

3. **Check results**
   - Column D: Status updates ("Processing", "Draft Ready", or "Failed")
   - Column E: Generated email subject
   - Column F: Generated email body

## Helper Scripts

- **Reset a row to pending status**:
  ```bash
  python set_pending.py
  ```

## How It Works

1. **Orchestrator** reads Google Sheet for pending rows
2. **Julep Task** is created/used to process each video:
   - Calls APIFY to extract YouTube transcript
   - Generates personalized email based on transcript
   - Returns email content
3. **Google Sheet** is updated with results

## API Services Used

- **Julep AI**: Agent orchestration and task management
- **APIFY**: YouTube transcript extraction (pintostudio~youtube-transcript-scraper)
- **Google Sheets API**: Data storage and management

## Limitations

- Currently generates email drafts only (doesn't send emails)
- Static email template (LLM integration pending final syntax fix)
- Processes one video at a time

## Future Enhancements

- [ ] Email sending functionality
- [ ] Dynamic email generation from transcripts
- [ ] Batch processing for multiple videos
- [ ] Advanced error handling and retry logic
- [ ] Email template customization
- [ ] Response tracking

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.