# DevPulse 🚀

A lightweight CLI-based tool that tracks your local coding activity and automatically generates human-readable daily "Done-Lists" or "Dev Logs" using Cloud AI APIs (Groq/OpenAI) to save local disk space.

## ✨ Features

- 🔍 **Smart File Watcher**: Monitors file changes in real-time using `watchdog`
- 🛡️ **Exclusion Engine**: Automatically ignores sensitive files (.env, keys) and heavy directories (node_modules, .git, venv)
- 💾 **Local SQLite Storage**: Stores metadata, diffs, git branch info, and timestamps
- 🤖 **Cloud AI Integration**: Uses Groq (Llama-3-70b) or OpenAI API to generate professional dev logs
- 🔒 **Privacy Mode**: Send only function/class names and commit messages instead of full code diffs
- ⚡ **Lightweight**: Minimal disk usage by leveraging cloud AI instead of local LLMs
- 📊 **Statistics**: Track your productivity with detailed statistics

## 🏗️ Architecture

```
devpulse/
├── __init__.py           # Package initialization
├── config.py             # Configuration and environment variables
├── database.py           # SQLite schema and operations
├── watcher.py            # File system watcher (watchdog)
├── ai_summarizer.py      # AI integration (Groq/OpenAI/LiteLLM)
└── cli.py                # Command-line interface
```

## 📦 Installation

### Option 1: Install from source (recommended)

```bash
# Clone or navigate to the project directory
cd devpulse

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .
```

### Option 2: Install dependencies only

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Set your API key as an environment variable:

### For Groq (recommended - faster and cheaper):

```bash
# Linux/Mac
export DEVPULSE_API_KEY="your-groq-api-key"
export DEVPULSE_AI_PROVIDER="groq"

# Windows PowerShell
$env:DEVPULSE_API_KEY="your-groq-api-key"
$env:DEVPULSE_AI_PROVIDER="groq"

# Windows CMD
set DEVPULSE_API_KEY=your-groq-api-key
set DEVPULSE_AI_PROVIDER=groq
```

### For OpenAI:

```bash
export DEVPULSE_API_KEY="your-openai-api-key"
export DEVPULSE_AI_PROVIDER="openai"
```

### Optional: Enable Privacy Mode

```bash
# Only send function/class names, not full code diffs
export DEVPULSE_PRIVACY_MODE="true"
```

## 🚀 Usage

### 1. Add a directory to track

```bash
devpulse track /path/to/your/project
```

### 2. Start tracking changes

```bash
# Run in foreground
devpulse start

# Run with privacy mode
devpulse start --privacy

# Run as daemon (background)
devpulse start --daemon
```

### 3. Generate daily dev log

```bash
# Generate log for today
devpulse log --today

# Generate log for specific date
devpulse log --date 2026-01-04

# Save to database
devpulse log --today --save

# Generate quick summary without AI
devpulse log --today --no-ai
```

### 4. View tracked directories

```bash
devpulse list
```

### 5. Remove directory from tracking

```bash
devpulse untrack /path/to/project
```

### 6. View statistics

```bash
# Overall statistics
devpulse stats

# Statistics for specific date
devpulse stats --date 2026-01-04
```

### 7. Clear history

```bash
devpulse clear
```

### 8. View configuration

```bash
devpulse config
```

## 📊 Database Schema

### file_changes

| Column         | Type     | Description                      |
| -------------- | -------- | -------------------------------- |
| id             | INTEGER  | Primary key                      |
| filename       | TEXT     | File name                        |
| filepath       | TEXT     | Full file path                   |
| timestamp      | DATETIME | When change occurred             |
| lines_added    | INTEGER  | Lines added                      |
| lines_removed  | INTEGER  | Lines removed                    |
| lines_modified | INTEGER  | Lines modified                   |
| git_branch     | TEXT     | Current git branch               |
| commit_message | TEXT     | Last commit message              |
| diff_content   | TEXT     | Full diff (NULL in privacy mode) |
| file_hash      | TEXT     | SHA256 hash of file              |
| processed      | INTEGER  | 0=unprocessed, 1=processed       |

### file_metadata (Privacy Mode)

| Column             | Type    | Description                  |
| ------------------ | ------- | ---------------------------- |
| id                 | INTEGER | Primary key                  |
| change_id          | INTEGER | Foreign key to file_changes  |
| functions_added    | TEXT    | JSON array of function names |
| functions_modified | TEXT    | JSON array of function names |
| functions_removed  | TEXT    | JSON array of function names |
| classes_added      | TEXT    | JSON array of class names    |
| classes_modified   | TEXT    | JSON array of class names    |
| imports_changed    | TEXT    | JSON array of imports        |

### watch_paths

| Column | Type    | Description             |
| ------ | ------- | ----------------------- |
| id     | INTEGER | Primary key             |
| path   | TEXT    | Directory path (unique) |
| active | INTEGER | 1=active, 0=inactive    |

### summary_logs

| Column              | Type    | Description          |
| ------------------- | ------- | -------------------- |
| id                  | INTEGER | Primary key          |
| date                | DATE    | Summary date         |
| summary_text        | TEXT    | AI-generated summary |
| total_files         | INTEGER | Files changed        |
| total_lines_added   | INTEGER | Total lines added    |
| total_lines_removed | INTEGER | Total lines removed  |

## 🔒 Privacy & Security

- **Environment Variables**: API keys are stored only in environment variables, never in code
- **Privacy Mode**: Enable to send only function/class names and commit messages to AI
- **Local Storage**: All change data stored locally in SQLite
- **Exclusion Engine**: Automatically excludes sensitive files (.env, .key, .pem, etc.)
- **No Telemetry**: No data sent anywhere except to your chosen AI provider when generating summaries

## 🏃 Running as Background Process (Daemon)

### Linux/Mac - Using systemd

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/devpulse.service
```

Add:

```ini
[Unit]
Description=DevPulse File Watcher
After=network.target

[Service]
Type=simple
User=your-username
Environment="DEVPULSE_API_KEY=your-api-key"
Environment="DEVPULSE_AI_PROVIDER=groq"
ExecStart=/path/to/venv/bin/devpulse start --daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable devpulse
sudo systemctl start devpulse
sudo systemctl status devpulse
```

### Linux/Mac - Using nohup

```bash
nohup devpulse start --daemon > /dev/null 2>&1 &
```

### Windows - Using Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "At startup")
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\devpulse.exe`
   - Arguments: `start --daemon`
5. Set environment variables in task properties

### Windows - Using NSSM (Non-Sucking Service Manager)

```powershell
# Install NSSM
choco install nssm

# Install service
nssm install DevPulse "C:\path\to\venv\Scripts\devpulse.exe" "start --daemon"

# Set environment variables
nssm set DevPulse AppEnvironmentExtra DEVPULSE_API_KEY=your-key DEVPULSE_AI_PROVIDER=groq

# Start service
nssm start DevPulse
```

## 🛠️ Development

### Run tests

```bash
pip install -e ".[dev]"
pytest
```

### Code formatting

```bash
black devpulse/
```

### Type checking

```bash
mypy devpulse/
```

## 📝 Example Output

```
==============================================================
  DEV LOG - 2026-01-04
==============================================================

✓ **Authentication Module**
  • Implemented JWT token refresh mechanism
  • Added password reset functionality via email
  • Fixed session timeout bug in admin panel

✓ **User Dashboard**
  • Redesigned profile settings UI with dark mode support
  • Added real-time notification system
  • Optimized data loading performance by 40%

✓ **API Improvements**
  • Refactored user endpoints for better error handling
  • Added rate limiting middleware
  • Updated API documentation

✓ **Bug Fixes**
  • Resolved memory leak in file upload service
  • Fixed date formatting issues in reports
  • Corrected timezone handling in scheduler

==============================================================
```

## 🌟 Supported File Types

Python, JavaScript, TypeScript, Go, Rust, C/C++, Java, Kotlin, Swift, Ruby, PHP, HTML, CSS/SCSS, SQL, Shell scripts, JSON, YAML, Markdown, and more.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📄 License

MIT License - feel free to use this in your projects!

## 🙏 Acknowledgments

- Built with [Watchdog](https://github.com/gorakhargosh/watchdog)
- Powered by [Groq](https://groq.com/) or [OpenAI](https://openai.com/)
- CLI framework: [Click](https://click.palletsprojects.com/)

---

**Made with ❤️ for developers who want to track their progress effortlessly**
