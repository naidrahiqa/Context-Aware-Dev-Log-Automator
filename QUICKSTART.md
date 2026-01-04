# DevPulse - Quick Start Guide

This guide will get you up and running with DevPulse in under 5 minutes.

---

## 📋 Prerequisites

- **Python 3.9+** installed
- **Git** (optional, for branch tracking)
- **API Key** from Groq or OpenAI

---

## 🚀 Installation (3 Steps)

### Step 1: Clone/Download the Project

```bash
cd "d:/IMPHNEN/26 Januari Project/Context-Aware Dev-Log Automator"
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install DevPulse
pip install -e .
```

### Step 3: Configure Your API Key

**Get an API Key:**

- **Groq** (Recommended): [https://console.groq.com/keys](https://console.groq.com/keys)
- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**Set Environment Variables:**

**Windows PowerShell:**

```powershell
$env:DEVPULSE_API_KEY="your-api-key-here"
$env:DEVPULSE_AI_PROVIDER="groq"
```

**Windows CMD:**

```cmd
set DEVPULSE_API_KEY=your-api-key-here
set DEVPULSE_AI_PROVIDER=groq
```

**Linux/Mac:**

```bash
export DEVPULSE_API_KEY="your-api-key-here"
export DEVPULSE_AI_PROVIDER="groq"
```

**Or run the interactive setup:**

```bash
python setup.py
```

---

## ✅ Verify Installation

```bash
devpulse config
```

You should see:

```
⚙️  DevPulse Configuration:
  Config Directory: C:\Users\YourName\.devpulse
  Database: C:\Users\YourName\.devpulse\devpulse.db
  AI Provider: groq
  Model: llama-3.1-70b-versatile
  Privacy Mode: ✗ Disabled
  API Key: ✓ Set
```

---

## 🎯 Basic Usage

### 1. Track Your First Project

```bash
# Track your current project
devpulse track .

# Or track any directory
devpulse track "D:/Projects/MyApp"
```

**Output:**

```
✓ Added to watch list: D:/Projects/MyApp
Run 'devpulse start' to begin tracking changes.
```

### 2. Start Tracking Changes

**Option A: Run in Foreground** (see live updates)

```bash
devpulse start
```

**Option B: Run in Background** (recommended for daily use)

```bash
devpulse start --daemon
```

**Output:**

```
🚀 Starting DevPulse...
Privacy Mode: ✗ Disabled
Watching 1 path(s)

👁️  Watching: D:/Projects/MyApp
DevPulse is now tracking your changes...
```

Now, every time you save a file in your project, you'll see:

```
✓ Tracked: main.py (+12/-3)
```

### 3. Generate Your First Dev Log

After working for a while, generate today's summary:

```bash
devpulse log --today
```

**Output:**

```
📊 Found 15 change(s) for 2026-01-04

🤖 Generating AI summary...

==============================================================
  DEV LOG - 2026-01-04
==============================================================

✓ **Authentication Module**
  • Implemented JWT token refresh mechanism
  • Added password reset functionality
  • Fixed session timeout bug

✓ **Database Layer**
  • Created new migration for user profiles
  • Optimized query performance in dashboard

✓ **Bug Fixes**
  • Resolved memory leak in file processing
  • Fixed date formatting issues

==============================================================
```

### 4. Save the Summary

```bash
devpulse log --today --save
```

This stores the summary in the database and marks changes as processed.

---

## 🎨 Advanced Usage

### Privacy Mode

Only send function/class names to AI (no code content):

```bash
# Enable for this session
devpulse start --privacy

# Or set permanently
export DEVPULSE_PRIVACY_MODE=true
```

### Track Multiple Projects

```bash
devpulse track ~/Projects/WebApp
devpulse track ~/Projects/MobileApp
devpulse track ~/Projects/API

# List all tracked
devpulse list
```

### View Statistics

```bash
# Overall stats
devpulse stats

# Specific date
devpulse stats --date 2026-01-04
```

**Output:**

```
📊 Statistics for 2026-01-04:
  Total Changes: 15
  Unique Files: 8
  Lines Added: 234
  Lines Removed: 89
  Lines Modified: 45
```

### Generate Log for Past Dates

```bash
devpulse log --date 2026-01-03
```

### Quick Summary (Without AI)

If you want a quick summary without using API credits:

```bash
devpulse log --today --no-ai
```

**Output:**

```
📊 Quick Summary
• Files Modified: 8
• Lines Added: 234
• Lines Removed: 89

📝 Files:
  • main.py (+45/-12)
  • auth.js (+89/-23)
  • database.py (+67/-34)
  ...
```

---

## 🔧 Common Tasks

### Stop Tracking

Press `Ctrl+C` in the terminal where DevPulse is running.

### Remove a Project

```bash
devpulse untrack "D:/Projects/MyApp"
```

### Clear All History

```bash
devpulse clear
```

### View Configuration

```bash
devpulse config
```

---

## 🏃 Run as Background Service

### Windows (Automatic Startup)

```powershell
# Install as Windows service
.\scripts\install-windows-service.ps1 `
  -DevPulsePath "C:\path\to\venv\Scripts\devpulse.exe" `
  -ApiKey "your-api-key" `
  -Provider "groq"

# Start service
nssm start DevPulse
```

### Linux/Mac (Systemd)

```bash
# Install as systemd service
./scripts/install-linux-service.sh

# Start service
sudo systemctl start devpulse

# View logs
sudo journalctl -u devpulse -f
```

---

## 📅 Daily Workflow Example

### Morning Setup

```bash
# Start tracking (once per startup)
devpulse start --daemon
```

### During the Day

Just code normally! DevPulse tracks everything automatically.

### End of Day

```bash
# Generate and save your dev log
devpulse log --today --save

# Optional: View stats
devpulse stats --date 2026-01-04
```

### Weekly Review

```bash
# Generate logs for the week
devpulse log --date 2026-01-04 --save
devpulse log --date 2026-01-03 --save
devpulse log --date 2026-01-02 --save
# ... etc
```

---

## 🆘 Troubleshooting

### "Invalid API Key" Error

```bash
# Check if API key is set
devpulse config

# Set it again
export DEVPULSE_API_KEY="your-actual-api-key"
```

### "No changes recorded"

1. Make sure DevPulse is running: `devpulse start`
2. Check you're tracking the right directory: `devpulse list`
3. Make actual file changes in tracked directories

### "Command not found"

```bash
# Make sure you activated the virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Or reinstall
pip install -e .
```

### High API Costs

1. **Enable Privacy Mode**: Sends less data

   ```bash
   export DEVPULSE_PRIVACY_MODE=true
   ```

2. **Use Quick Summary**: Skip AI for less important days

   ```bash
   devpulse log --today --no-ai
   ```

3. **Use Groq Instead of OpenAI**: Much cheaper/faster
   ```bash
   export DEVPULSE_AI_PROVIDER=groq
   ```

---

## 💡 Tips & Best Practices

### 1. **Commit Often**

DevPulse tracks git commit messages. More commits = better summaries.

### 2. **Descriptive Commits**

Write meaningful commit messages:

- ✅ "Added JWT authentication to login endpoint"
- ❌ "Fixed stuff"

### 3. **End-of-Day Summaries**

Generate summaries daily while context is fresh:

```bash
devpulse log --today --save
```

### 4. **Use Privacy Mode for Work**

If working on proprietary code:

```bash
export DEVPULSE_PRIVACY_MODE=true
```

### 5. **Exclude Sensitive Directories**

DevPulse auto-excludes common patterns, but you can customize in `config.py`:

```python
EXCLUSION_PATTERNS = [
    ".env",
    "node_modules",
    "my_secret_dir",  # Add custom patterns
]
```

---

## 📚 Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
- Read [README.md](README.md) for full documentation
- Customize exclusion patterns in `devpulse/config.py`
- Set up as a background service for automatic tracking

---

## ✨ Example Dev Log Output

Here's what a real summary looks like:

```
==============================================================
  DEV LOG - 2026-01-04
==============================================================

✓ **User Authentication System**
  • Implemented JWT-based authentication with refresh tokens
  • Added password reset flow with email verification
  • Created middleware for protected routes
  • Fixed session expiration handling bug

✓ **Dashboard UI Improvements**
  • Redesigned user profile page with modern card layout
  • Added real-time notifications using WebSockets
  • Implemented dark mode toggle with persistence
  • Optimized rendering performance (40% faster loads)

✓ **API Development**
  • Created RESTful endpoints for user management
  • Added comprehensive error handling and validation
  • Implemented rate limiting (100 requests/hour)
  • Updated Swagger documentation

✓ **Database Migrations**
  • Added indexes on frequently queried columns
  • Created new tables for notification system
  • Migrated user preferences to JSONB format

✓ **Testing & Quality**
  • Wrote unit tests for authentication module (95% coverage)
  • Fixed 12 ESLint warnings
  • Added integration tests for API endpoints

✓ **Bug Fixes**
  • Resolved memory leak in file upload handler
  • Fixed timezone issues in date pickers
  • Corrected alignment issues in mobile view

==============================================================

📊 Summary Statistics:
  • Total Files Modified: 23
  • Lines Added: 1,247
  • Lines Removed: 456
```

---

**Happy Tracking! 🚀**

For questions or issues, check the [README](README.md) or open an issue on GitHub.
