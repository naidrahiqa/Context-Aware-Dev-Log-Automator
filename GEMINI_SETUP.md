# Using DevPulse with Google Gemini API

This guide explains how to use DevPulse with Google's Gemini API.

---

## ✅ Your Current Setup

You've already configured DevPulse with:

- **Provider:** `litellm` (supports Gemini)
- **API Key:** `AIzaSyDdqFTHRHSascogHReFQBEId98FllgEgWE`
- **Model:** `gemini/gemini-1.5-flash` (fast and cost-effective)

---

## 🚀 Quick Start

### Your .env File

Your `.env` file should contain:

```bash
DEVPULSE_AI_PROVIDER=litellm
DEVPULSE_API_KEY=AIzaSyDdqFTHRHSascogHReFQBEId98FllgEgWE
DEVPULSE_PRIVACY_MODE=false
DEVPULSE_MODEL=gemini/gemini-1.5-flash
```

### Activate Virtual Environment

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### Install DevPulse

```bash
pip install -e .
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
  AI Provider: litellm
  Model: gemini/gemini-1.5-flash
  Privacy Mode: ✗ Disabled
  API Key: ✓ Set
```

---

## 📝 Using DevPulse with Gemini

### Basic Workflow

```bash
# 1. Track your project
devpulse track .

# 2. Start monitoring
devpulse start

# Make some code changes...

# 3. Generate summary with Gemini
devpulse log --today
```

### Example Output

```
📊 Found 5 change(s) for 2026-01-04

🤖 Generating AI summary...

==============================================================
  DEV LOG - 2026-01-04
==============================================================

✓ **Project Setup**
  • Created DevPulse configuration files
  • Set up Google Gemini API integration
  • Initialized virtual environment

==============================================================
```

---

## 🎯 Gemini Model Options

DevPulse supports all Gemini models via LiteLLM. Set via `DEVPULSE_MODEL`:

### Recommended Models

| Model                     | Speed  | Cost | Best For                 |
| ------------------------- | ------ | ---- | ------------------------ |
| `gemini/gemini-1.5-flash` | ⚡⚡⚡ | 💰   | **Daily logs** (Default) |
| `gemini/gemini-1.5-pro`   | ⚡⚡   | 💰💰 | Complex summaries        |
| `gemini/gemini-pro`       | ⚡⚡   | 💰   | Balanced option          |

### Change Model

**In .env file:**

```bash
DEVPULSE_MODEL=gemini/gemini-1.5-pro
```

**Or via environment variable:**

```powershell
# Windows
$env:DEVPULSE_MODEL="gemini/gemini-1.5-pro"

# Linux/Mac
export DEVPULSE_MODEL="gemini/gemini-1.5-pro"
```

---

## 💰 Gemini Pricing (as of 2026)

| Model            | Input (per 1M tokens) | Output (per 1M tokens) |
| ---------------- | --------------------- | ---------------------- |
| Gemini 1.5 Flash | Free tier available   | Free tier available    |
| Gemini 1.5 Pro   | $0.35                 | $1.05                  |

**Typical Usage:**

- Daily log (20 files): ~5,000 tokens
- Monthly cost: **< $1** with Flash model

---

## 🔧 Troubleshooting

### Issue: "Invalid API Key"

**Check your API key:**

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Generate new API key if needed
3. Update in `.env` file:
   ```bash
   DEVPULSE_API_KEY=your-new-key-here
   ```

### Issue: "Model not found"

**Make sure model name has `gemini/` prefix:**

```bash
# ✅ Correct
DEVPULSE_MODEL=gemini/gemini-1.5-flash

# ❌ Wrong
DEVPULSE_MODEL=gemini-1.5-flash
```

### Issue: "Rate limit exceeded"

**Solutions:**

1. Wait a few minutes and try again
2. Use Privacy Mode to reduce tokens:
   ```bash
   DEVPULSE_PRIVACY_MODE=true
   ```
3. Generate logs less frequently

### Issue: Import Error for LiteLLM

**Install LiteLLM:**

```bash
pip install litellm>=1.30.0
```

**Or reinstall all dependencies:**

```bash
pip install -r requirements.txt
```

---

## 🔒 Privacy with Gemini

### Standard Mode

- Full code diffs sent to Gemini
- Better context for summaries
- Suitable for personal/open-source projects

### Privacy Mode

```bash
# Enable in .env
DEVPULSE_PRIVACY_MODE=true
```

**What's sent:**

- ✅ Function/class names
- ✅ File names and paths
- ✅ Line counts
- ✅ Git branch and commits
- ❌ **No actual code content**

---

## 💡 Tips for Best Results with Gemini

### 1. Write Good Commit Messages

Gemini uses commit messages for context:

```bash
# ✅ Good
git commit -m "Add user authentication with JWT tokens"

# ❌ Bad
git commit -m "update"
```

### 2. Use Privacy Mode for Proprietary Code

```bash
DEVPULSE_PRIVACY_MODE=true
```

### 3. Commit Frequently

More commits = better context for summaries

### 4. Generate Logs Daily

Fresh context produces better summaries:

```bash
devpulse log --today --save
```

---

## 📊 Compare with Other Providers

| Feature        | Gemini (Flash) | Groq        | OpenAI      |
| -------------- | -------------- | ----------- | ----------- |
| Speed          | ⚡⚡⚡         | ⚡⚡⚡      | ⚡⚡        |
| Cost           | 💰 Free tier   | 💰 Low      | 💰💰 Higher |
| Quality        | ⭐⭐⭐⭐       | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐  |
| Context Window | 1M tokens      | 128K tokens | 128K tokens |

**Recommendation:** Gemini 1.5 Flash is excellent for DevPulse due to:

- **Free tier** for moderate usage
- **Fast inference** (< 3s)
- **Large context window** (1M tokens)
- **Good quality** summaries

---

## 🚀 Advanced Configuration

### Use Different Models for Different Projects

Create project-specific `.env` files:

**Project A (.env.projecta):**

```bash
DEVPULSE_MODEL=gemini/gemini-1.5-flash
```

**Project B (.env.projectb):**

```bash
DEVPULSE_MODEL=gemini/gemini-1.5-pro
```

Load before running:

```bash
# Windows
Get-Content .env.projecta | ForEach-Object {
    $var = $_.Split('=')
    [Environment]::SetEnvironmentVariable($var[0], $var[1])
}

# Linux/Mac
export $(cat .env.projecta | xargs)
```

### Temperature Control

For more deterministic summaries, LiteLLM uses default temperature of 0.3.

To customize, edit `devpulse/ai_summarizer.py` line ~150:

```python
temperature=0.1,  # More deterministic
# or
temperature=0.5,  # More creative
```

---

## 📖 Example Commands

### Daily Workflow

```bash
# Morning: Start tracking
devpulse start --daemon

# Evening: Generate log
devpulse log --today --save

# View stats
devpulse stats
```

### Weekly Review

```bash
# Generate logs for the week
for day in 01 02 03 04 05 06 07; do
    devpulse log --date 2026-01-$day
done
```

### Quick Summary Without AI

Save API calls during testing:

```bash
devpulse log --today --no-ai
```

---

## 🆘 Getting Help

### Check Configuration

```bash
devpulse config
```

### View All Commands

```bash
devpulse --help
```

### Test API Connection

Create a test file and track it:

```bash
mkdir test-gemini
cd test-gemini
echo "print('Hello Gemini')" > test.py
devpulse track .
devpulse start
# Edit test.py
# Stop with Ctrl+C
devpulse log --today
```

---

## 📚 Additional Resources

- **Google AI Studio:** https://makersuite.google.com/
- **Gemini API Docs:** https://ai.google.dev/docs
- **LiteLLM Docs:** https://docs.litellm.ai/
- **DevPulse Docs:** See README.md

---

## ✅ Setup Checklist

- [x] Python 3.9+ installed
- [x] Virtual environment created
- [x] DevPulse installed (`pip install -e .`)
- [x] Gemini API key obtained
- [x] `.env` file configured
- [x] Configuration verified (`devpulse config`)
- [ ] Project tracked (`devpulse track <path>`)
- [ ] Watcher started (`devpulse start`)
- [ ] First log generated (`devpulse log --today`)

---

## 🎉 You're All Set!

DevPulse is now configured to use **Google Gemini API**. Start tracking your projects and let Gemini generate professional development logs for you!

**Next Steps:**

1. Activate your virtual environment
2. Install DevPulse: `pip install -e .`
3. Track a project: `devpulse track .`
4. Start monitoring: `devpulse start`
5. Generate your first log: `devpulse log --today`

**Happy coding! 🚀**
