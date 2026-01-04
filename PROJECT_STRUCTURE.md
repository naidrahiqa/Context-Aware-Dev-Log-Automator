# DevPulse - Project Structure

```
Context-Aware Dev-Log Automator/
│
├── devpulse/                          # Main package directory
│   ├── __init__.py                    # Package initialization
│   ├── config.py                      # Configuration & environment vars
│   ├── database.py                    # SQLite schema & operations
│   ├── watcher.py                     # File watcher & diff analyzer
│   ├── ai_summarizer.py               # AI integration (Groq/OpenAI)
│   └── cli.py                         # Command-line interface
│
├── scripts/                           # Deployment scripts
│   ├── devpulse.service.template      # Systemd service template
│   ├── install-linux-service.sh       # Linux service installer
│   └── install-windows-service.ps1    # Windows service installer
│
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── ARCHITECTURE.md                    # System architecture doc
├── LICENSE                            # MIT License
├── QUICKSTART.md                      # Quick start guide
├── README.md                          # Main documentation
├── pyproject.toml                     # Python project config
├── requirements.txt                   # Python dependencies
└── setup.py                           # Interactive setup script

```

## 📊 File Breakdown

### Core Modules (devpulse/)

| File               | Lines | Purpose                                          |
| ------------------ | ----- | ------------------------------------------------ |
| `config.py`        | ~85   | Environment configuration, exclusion patterns    |
| `database.py`      | ~330  | SQLite operations, 4 tables, CRUD functions      |
| `watcher.py`       | ~330  | File watching, diff computation, git integration |
| `ai_summarizer.py` | ~270  | AI API integration, prompt engineering           |
| `cli.py`           | ~260  | CLI commands, user interface                     |

**Total Core Code:** ~1,275 lines

### Documentation

| File              | Purpose                            |
| ----------------- | ---------------------------------- |
| `README.md`       | Installation, usage, features      |
| `QUICKSTART.md`   | 5-minute getting started guide     |
| `ARCHITECTURE.md` | System design, data flows, schemas |
| `.env.example`    | Environment variable template      |

### Scripts

| File                          | Purpose                          |
| ----------------------------- | -------------------------------- |
| `setup.py`                    | Interactive configuration wizard |
| `install-linux-service.sh`    | Systemd service installer        |
| `install-windows-service.ps1` | Windows/NSSM service installer   |

## 🗃️ Runtime Files (Created Automatically)

```
~/.devpulse/                           # User config directory
├── devpulse.db                        # SQLite database
└── watch_paths.txt                    # (Optional) Watch list backup
```

## 📦 Dependencies

### Production

- `click>=8.1.7` - CLI framework
- `watchdog>=3.0.0` - File system monitoring
- `groq>=0.4.0` - Groq AI API client
- `openai>=1.12.0` - OpenAI API client
- `litellm>=1.30.0` - Universal LLM client

### Development (Optional)

- `pytest>=7.4.0` - Testing
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Linting
- `mypy>=1.5.0` - Type checking

## 🎯 Entry Points

After installation (`pip install -e .`), the following command becomes available:

```bash
devpulse -> devpulse.cli:main
```

## 🔄 Configuration Hierarchy

1. **Environment Variables** (Highest Priority)

   ```
   DEVPULSE_API_KEY
   DEVPULSE_AI_PROVIDER
   DEVPULSE_PRIVACY_MODE
   DEVPULSE_MODEL
   ```

2. **Configuration File** (Medium Priority)

   ```
   devpulse/config.py
   ```

3. **Default Values** (Lowest Priority)
   - AI Provider: `groq`
   - Model: `llama-3.1-70b-versatile`
   - Privacy Mode: `false`

## 📈 Code Statistics

| Metric              | Count  |
| ------------------- | ------ |
| Python Modules      | 6      |
| CLI Commands        | 8      |
| Database Tables     | 4      |
| Documentation Files | 4      |
| Deployment Scripts  | 3      |
| Lines of Code       | ~1,275 |
| Lines of Docs       | ~950   |

## 🏗️ Module Dependencies

```
cli.py
 ├── config.py
 ├── database.py
 ├── watcher.py
 │   ├── config.py
 │   └── database.py
 └── ai_summarizer.py
     └── config.py

database.py
 └── config.py

watcher.py
 ├── config.py
 └── database.py

ai_summarizer.py
 └── config.py
```

**No circular dependencies!** ✅

## 🧪 Testing Structure (Future)

```
tests/
├── __init__.py
├── test_config.py
├── test_database.py
├── test_watcher.py
├── test_ai_summarizer.py
├── test_cli.py
└── fixtures/
    ├── sample_diffs.txt
    └── sample_code.py
```

## 📝 Notes

- **Modular Design**: Each file has a single responsibility
- **No Globals**: All state in classes or function params
- **Type Hints**: (Can be added for better IDE support)
- **Error Handling**: Graceful degradation throughout
- **Extensibility**: Easy to add new AI providers or file types
