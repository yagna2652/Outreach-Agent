# Julep-Native YouTube Outreach Agent

## Quick Start (3 Steps!)

### 1. Create the Workflow Task (One-time setup)
```bash
python create_tasks.py
```
This creates the workflow task in Julep and saves the task ID to your `.env` file.

### 2. Start the Agent
```bash
python start_agent.py
```

### 3. Choose Your Mode

When you run `start_agent.py`, you'll see:
```
Choose mode:
1. Monitor mode (see live updates)
2. Fire and forget (start and exit)
3. Check existing execution status
```

## Operating Modes Explained

### Monitor Mode
- **What it does**: Starts the workflow and shows live updates
- **Use when**: You want to watch the process in real-time
- **Example output**:
  ```
  📖 Reading Google Sheet...
  📊 Found 5 pending rows to process
  🎬 Fetching YouTube transcript...
  ✏️  Updating sheet status...
  📧 Generating email...
  ✅ Processed row 2 for CreatorName
  ```

### Fire and Forget Mode
- **What it does**: Starts the workflow and immediately exits
- **Use when**: You want to let it run in the background
- **The workflow continues running on Julep's servers even after you close the script**
- **Example**:
  ```bash
  python start_agent.py --fire
  # Output: "Agent is running on Julep's infrastructure"
  # You can close your laptop - it keeps running!
  ```

### Status Check Mode
- **What it does**: Check on a running workflow
- **Use when**: You started a workflow earlier and want to check progress
- **Example**:
  ```bash
  python start_agent.py --status abc123-execution-id
  ```

## Command Line Options

```bash
# Interactive mode (default)
python start_agent.py

# Fire and forget
python start_agent.py --fire

# Check status
python start_agent.py --status <execution_id>

# Help
python start_agent.py --help
```

## What Happens Behind the Scenes

When you run `start_agent.py`, it:

1. **Sends ONE command to Julep**: "Start workflow with these credentials"
2. **Julep takes over completely**:
   - Reads your Google Sheet
   - Finds all pending rows
   - Processes each YouTube video
   - Generates personalized emails
   - Updates the sheet with results
   - Handles all errors and retries

## Key Difference from Old Approach

### Old Way (with orchestrator.py)
```python
# Your computer was doing this:
for video in videos:
    process_video()     # Wait...
    update_sheet()      # Wait...
    send_email()        # Wait...
# Your laptop had to stay on for all of this
```

### New Way (Julep-Native)
```python
# Your computer does this:
start_workflow()
# Done! Julep handles everything else
```

## The Magic: Your workflow.yaml is the Brain

Your `workflow.yaml` file contains ALL the logic:
- Reading the sheet (line 90)
- Finding pending rows (lines 99-112)
- Processing each video (lines 117-215)
- Updating statuses
- Generating emails
- Error handling

**You don't need orchestrator.py anymore** because workflow.yaml IS the orchestrator!

## Monitoring Your Agent

### Real-time Monitoring
```bash
python start_agent.py
# Select option 1 (Monitor mode)
```

### Dashboard Monitoring
After starting, you'll get a link:
```
Dashboard: https://dashboard.julep.ai/executions/{execution_id}
```

### Detached Monitoring
- Press `Ctrl+C` while monitoring to detach
- The workflow continues running on Julep
- Re-attach later with the execution ID

## Tips

1. **Test with Drafts First**: Always use draft mode before sending real emails
2. **Fire and Forget for Production**: Once tested, use fire-and-forget mode
3. **Check Your Sheet**: The Google Sheet shows real-time updates
4. **Multiple Instances**: You can run multiple workflows simultaneously

## Troubleshooting

### "No workflow task ID found"
Run `python create_tasks.py` first

### "Failed to get Google auth token"
Check that `service_account.json` exists

### Workflow seems stuck
1. Check the Julep dashboard link
2. Use `python start_agent.py --status <execution_id>`

## Why This is Better

1. **Runs on Julep's Infrastructure**: Not your laptop
2. **Survives Disconnections**: Continues even if you close the script
3. **Parallel Processing**: Built into workflow.yaml's foreach loop
4. **State Management**: Julep handles all state persistence
5. **Error Recovery**: Automatic retries built into the workflow

## Next Steps

1. **Run a test**: `python start_agent.py` (choose draft mode)
2. **Check results**: Look at your Google Sheet columns D-F
3. **Go production**: Use fire-and-forget mode for autonomous operation