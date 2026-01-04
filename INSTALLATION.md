# DevPulse - Installation & Testing Guide

This guide walks you through installing DevPulse and running your first test to ensure everything works correctly.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.9 or higher** installed

  ```bash
  python --version  # Should show 3.9+
  ```

- [ ] **pip** package manager

  ```bash
  pip --version
  ```

- [ ] **Git** (optional, for branch tracking)

  ```bash
  git --version
  ```

- [ ] **API Key** from Groq or OpenAI
  - Groq: https://console.groq.com/keys (Recommended - Free tier available)
  - OpenAI: https://platform.openai.com/api-keys

---

## 🚀 Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd "d:/IMPHNEN/26 Januari Project/Context-Aware Dev-Log Automator"
```

### Step 2: Create Virtual Environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Verification:**
Your command prompt should now show `(venv)` prefix.

### Step 3: Install DevPulse

```bash
pip install -e .
```

**Expected Output:**

```
Successfully installed click-8.1.7 devpulse-1.0.0 groq-0.4.0 openai-1.12.0 watchdog-3.0.0 ...
```

### Step 4: Verify Installation

```bash
devpulse --version
```

**Expected Output:**

```
devpulse, version 1.0.0
```

---

## ⚙️ Configuration

### Option 1: Interactive Setup (Recommended for First-Time Users)

```bash
python setup.py
```

Follow the prompts:

1. Select AI provider (Groq recommended)
2. Enter API key
3. Choose privacy mode

### Option 2: Manual Environment Setup

**Windows PowerShell:**

```powershell
$env:DEVPULSE_API_KEY="your-groq-api-key-here"
$env:DEVPULSE_AI_PROVIDER="groq"
$env:DEVPULSE_PRIVACY_MODE="false"
```

**Windows CMD:**

```cmd
set DEVPULSE_API_KEY=your-groq-api-key-here
set DEVPULSE_AI_PROVIDER=groq
set DEVPULSE_PRIVACY_MODE=false
```

**Linux/Mac:**

```bash
export DEVPULSE_API_KEY="your-groq-api-key-here"
export DEVPULSE_AI_PROVIDER="groq"
export DEVPULSE_PRIVACY_MODE="false"
```

### Verify Configuration

```bash
devpulse config
```

**Expected Output:**

```
⚙️  DevPulse Configuration:
  Config Directory: C:\Users\YourName\.devpulse
  Database: C:\Users\YourName\.devpulse\devpulse.db
  AI Provider: groq
  Model: llama-3.1-70b-versatile
  Privacy Mode: ✗ Disabled
  API Key: ✓ Set
```

**✅ If you see "API Key: ✓ Set", you're ready to go!**

---

## 🧪 Testing DevPulse

### Test 1: Basic Tracking

**Step 1: Create a test directory**

```bash
mkdir test-devpulse
cd test-devpulse
```

**Step 2: Initialize git (optional)**

```bash
git init
```

**Step 3: Track this directory**

```bash
devpulse track .
```

**Expected Output:**

```
✓ Added to watch list: D:/path/to/test-devpulse
Run 'devpulse start' to begin tracking changes.
```

**Step 4: Start tracking**

Open a **new terminal window** and run:

```bash
cd "d:/IMPHNEN/26 Januari Project/Context-Aware Dev-Log Automator"
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

devpulse start
```

**Expected Output:**

```
🚀 Starting DevPulse...
Privacy Mode: ✗ Disabled
Watching 1 path(s)

👁️  Watching: D:/path/to/test-devpulse
DevPulse is now tracking your changes...
```

**Leave this terminal running!**

### Test 2: Make Code Changes

In your **original terminal** (in test-devpulse directory):

**Create a Python file:**

```bash
# Create test.py
echo 'def hello():' > test.py
echo '    print("Hello, DevPulse!")' >> test.py
```

**Expected Output in DevPulse terminal:**

```
✓ Tracked: test.py (+2/-0)
```

**Make more changes:**

```bash
echo '' >> test.py
echo 'def goodbye():' >> test.py
echo '    print("Goodbye!")' >> test.py

echo '' >> test.py
echo 'if __name__ == "__main__":' >> test.py
echo '    hello()' >> test.py
echo '    goodbye()' >> test.py
```

**Expected Output:**

```
✓ Tracked: test.py (+6/-0)
```

**Commit your changes (optional):**

```bash
git add test.py
git commit -m "Add hello and goodbye functions"
```

### Test 3: Generate Summary

**Step 1: Stop the watcher**

In the DevPulse terminal, press `Ctrl+C`

```
⏹️  Stopping DevPulse...
```

**Step 2: Generate today's log**

```bash
devpulse log --today
```

**Expected Output:**

```
📊 Found 2 change(s) for 2026-01-04

🤖 Generating AI summary...

==============================================================
  DEV LOG - 2026-01-04
==============================================================

✓ **Test Script Development**
  • Created hello function to display greeting message
  • Added goodbye function for farewell message
  • Implemented main execution block to call both functions

==============================================================
```

**🎉 Success! You've successfully tested DevPulse!**

### Test 4: More CLI Commands

**View statistics:**

```bash
devpulse stats
```

**Expected Output:**

```
📊 Overall Statistics:
  Total Changes: 2
  Unique Files: 1
  Lines Added: 8
  Lines Removed: 0
  Lines Modified: 0
```

**Save the summary:**

```bash
devpulse log --today --save
```

**Expected Output:**

```
✓ Summary saved to database
```

**List tracked directories:**

```bash
devpulse list
```

**Expected Output:**

```
📂 Watching 1 path(s):
  1. D:/path/to/test-devpulse
```

---

## ✅ Verification Checklist

After testing, verify:

- [ ] DevPulse tracks file changes in real-time
- [ ] Changes appear in the terminal with `✓ Tracked: filename`
- [ ] `devpulse log --today` generates an AI summary
- [ ] `devpulse stats` shows correct statistics
- [ ] `devpulse config` confirms API key is set
- [ ] Database created at `~/.devpulse/devpulse.db`

---

## 🧹 Cleanup Test Environment

```bash
# Stop tracking test directory
devpulse untrack "D:/path/to/test-devpulse"

# Clear test data
devpulse clear --confirm

# Remove test directory
cd ..
rm -rf test-devpulse  # Linux/Mac
# OR
Remove-Item -Recurse -Force test-devpulse  # Windows PowerShell
```

---

## 🔧 Troubleshooting

### Issue: "devpulse: command not found"

**Solution:**

```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall
pip install -e .
```

### Issue: "Invalid API Key"

**Solution:**

```bash
# Check configuration
devpulse config

# Re-set API key
export DEVPULSE_API_KEY="your-actual-key"  # Linux/Mac
$env:DEVPULSE_API_KEY="your-actual-key"   # Windows PowerShell

# Verify
devpulse config
```

### Issue: "No changes recorded"

**Possible Causes:**

1. DevPulse watcher not running → Run `devpulse start`
2. Wrong directory tracked → Check `devpulse list`
3. File excluded by patterns → Check `EXCLUSION_PATTERNS` in config.py

**Solution:**

```bash
# Ensure tracking the right directory
devpulse track /correct/path

# Start watcher
devpulse start
```

### Issue: "AI API Error"

**Possible Causes:**

1. Invalid API key
2. Rate limit exceeded
3. Network issues

**Solution:**

```bash
# Use quick summary instead
devpulse log --today --no-ai

# Check API key
devpulse config

# Try again later (rate limits reset)
```

### Issue: Files Not Being Tracked

**Check if file is excluded:**

1. Look at `devpulse/config.py`
2. Check `EXCLUSION_PATTERNS` list
3. Verify file extension is in `TRACKED_EXTENSIONS` (if set)

**Solution:**

```python
# Edit devpulse/config.py
EXCLUSION_PATTERNS = [
    # Comment out patterns you don't want excluded
    # ".env",
    # "node_modules",
]
```

---

## 🏁 Next Steps

### For Development Use

1. **Track your real projects:**

   ```bash
   devpulse track ~/Projects/MyApp
   devpulse track ~/Projects/AnotherApp
   ```

2. **Run as daemon:**

   ```bash
   devpulse start --daemon
   ```

3. **Set up daily routine:**
   - Morning: `devpulse start --daemon`
   - Evening: `devpulse log --today --save`

### For Production Deployment

1. **Install as service (Linux):**

   ```bash
   ./scripts/install-linux-service.sh
   ```

2. **Install as service (Windows):**
   ```powershell
   .\scripts\install-windows-service.ps1 `
     -DevPulsePath "C:\path\to\venv\Scripts\devpulse.exe" `
     -ApiKey "your-key" `
     -Provider "groq"
   ```

### For Team Use

1. **Share configuration:**

   - Document your exclusion patterns
   - Share `.env.example` with team
   - Provide installation guide

2. **Standardize workflow:**
   - Daily log generation time
   - Privacy mode settings
   - Summary format preferences

---

## 📚 Additional Resources

- **Full Documentation:** [README.md](README.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Project Structure:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## ✅ Installation Complete!

You've successfully installed and tested DevPulse. You're now ready to:

- ✅ Track your coding activity automatically
- ✅ Generate AI-powered daily dev logs
- ✅ Monitor your productivity with statistics
- ✅ Run as a background service

**Happy tracking! 🚀**

---

**Need Help?**

- Review documentation files
- Check troubleshooting section above
- Open an issue on GitHub (if applicable)
