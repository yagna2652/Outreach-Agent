# YouTube Outreach Agent

A Julep-powered automated agent that processes Google Sheets to perform personalized YouTube creator outreach by analyzing video transcripts and generating tailored emails.

## 🎉 NEW: Fully Julep-Native Implementation

**We've migrated to a Julep-native approach that runs autonomously on Julep's infrastructure!**

### Quick Start (Just 2 Commands!)
```bash
# One-time setup: Create the workflow task
python create_tasks.py

# Start the agent (Julep handles everything)
python start_agent.py
```

📖 **See [JULEP_NATIVE_GUIDE.md](./JULEP_NATIVE_GUIDE.md) for complete documentation of the new approach.**

### What Changed?
- **No more orchestrator.py** - Julep handles all orchestration
- **Runs on Julep's servers** - Your laptop can shut down
- **Parallel processing** - Built into the workflow
- **Fire and forget mode** - Start and walk away

---

## Legacy Documentation (Previous Implementation)

## 🚀 Features

- **Google Sheets Integration** - Read and process creator data from Google Sheets
- **YouTube Transcript Extraction** - Fetch video transcripts using APIFY
- **AI Email Generation** - Generate personalized emails using Claude LLM
- **Gmail Integration** - Send emails or save as drafts
- **Automated Status Tracking** - Update sheet with processing status

## 📁 Project Structure

```
ytreachoutagent/
├── .env                    # API keys and configuration
├── service_account.json    # Google service account credentials
├── requirements.txt        # Python dependencies
│
├── workflow.yaml           # Main Julep workflow definition
├── run_workflow.py         # Execute the workflow
├── monitor_execution.py    # Monitor running executions
├── create_tasks.py         # Create Julep tasks
│
├── sheets_reader.py        # Test Google Sheets reading
├── sheets_writer.py        # Test Google Sheets writing
├── google_sheets_handler.py # Google Sheets utilities
│
└── README.md              # This file
```

## 🔧 Setup Instructions

### 1. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a service account and download JSON key
4. Place the key as `service_account.json`
5. Share your Google Sheet with the service account email

### 3. Environment Configuration

Create a `.env` file with:

```env
# Julep Configuration
JULEP_API_KEY=your_julep_api_key
AGENT_ID=your_agent_id

# Google Sheets
GOOGLE_SHEET_ID=your_sheet_id

# APIFY
APIFY_TOKEN=your_apify_token

# Email (Gmail)
EMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### 4. Google Sheet Format

Your Google Sheet should have these columns:

| Column | Field | Description |
|--------|-------|-------------|
| A | Creator Name | YouTube creator's name |
| B | YouTube URL | Video or channel URL |
| C | Email | Recipient email address |
| D | Status | Processing status (Pending/Processing/Completed) |
| E | Notes | Email subject or status notes |
| F | Email Draft | Generated email content |

## 💻 Usage

### Test Google Sheets Connection

```bash
# Test reading from sheet
python sheets_reader.py

# Test writing to sheet
python sheets_writer.py
```

### Run the Workflow

```bash
python run_workflow.py
```

This will:
1. Prompt you to choose between draft mode or sending emails
2. Read pending rows from your Google Sheet
3. Fetch YouTube transcripts for each video
4. Generate personalized emails
5. Either send emails or save as drafts
6. Update sheet with status

### Monitor Execution

```bash
# Monitor by execution ID
python monitor_execution.py <execution_id>

# Or run interactively
python monitor_execution.py
```

## 🔄 Workflow Process

1. **Read Sheet** - Fetch all rows marked as "Pending"
2. **Extract Transcript** - Use APIFY to get video transcript
3. **Generate Email** - Use Claude to create personalized email
4. **Send/Save** - Send email or save as draft
5. **Update Status** - Mark row as completed

## ⚠️ Current Limitations

- Julep's `foreach` loop validation has issues - may need workarounds
- Variable scoping in Julep tools requires specific syntax
- APIFY processing takes 10-30 seconds per video

## 🐛 Troubleshooting

### Authentication Issues
- Verify service account has Editor access to sheet
- Check that `service_account.json` is valid
- Ensure sheet is shared with service account email

### APIFY Issues
- Verify APIFY token is active
- Check APIFY actor is available
- Allow 10-30 seconds for transcript extraction

### Email Issues
- Use Gmail app-specific password (not regular password)
- Enable 2FA on Gmail account first
- Check spam folder for test emails

## 📚 Technologies

- **Julep** - Agent orchestration
- **Google Sheets API** - Data storage
- **APIFY** - YouTube transcript extraction
- **Claude (Anthropic)** - Email generation
- **Gmail SMTP** - Email sending
- **Python 3.8+** - Runtime

## 🔒 Security Notes

- Never commit `.env` or `service_account.json`
- Use app-specific passwords for Gmail
- Rotate API keys regularly
- Keep service account permissions minimal

## 📝 License

MIT