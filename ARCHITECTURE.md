# DevPulse - Architecture & Design Document

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         DevPulse CLI                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐            │
│  │  Config  │───▶│   CLI    │───▶│  Database │            │
│  │ Manager  │    │ Commands │    │  Manager  │            │
│  └──────────┘    └─────┬────┘    └───────────┘            │
│                        │                                    │
│                        ├──────────┬──────────┐             │
│                        │          │          │             │
│                  ┌─────▼────┐ ┌──▼─────┐ ┌─▼──────────┐   │
│                  │   File   │ │   AI   │ │  Privacy   │   │
│                  │ Watcher  │ │Summary │ │  Engine    │   │
│                  └─────┬────┘ └────────┘ └────────────┘   │
│                        │                                    │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  File System     │
              │  (Watched Dirs)  │
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  SQLite Database │
              │  (~/.devpulse/)  │
              └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Cloud AI API    │
              │ (Groq/OpenAI)    │
              └──────────────────┘
```

---

## 📦 Module Breakdown

### 1. **config.py** - Configuration Management

**Purpose**: Centralized configuration and environment variable management

**Key Components**:

- Environment variable loading
- Path configuration (DB, config directory)
- Exclusion patterns for file watching
- AI provider configuration
- Default settings

**Environment Variables**:

- `DEVPULSE_API_KEY`: API key for AI provider (required)
- `DEVPULSE_AI_PROVIDER`: AI provider choice (groq/openai/litellm)
- `DEVPULSE_PRIVACY_MODE`: Enable privacy mode (true/false)
- `DEVPULSE_MODEL`: Override default model

**Exclusion Engine**:

```python
EXCLUSION_PATTERNS = [
    ".env", "*.key", "*.pem",      # Secrets
    "node_modules", "venv",         # Dependencies
    ".git", "dist", "build",        # VCS & artifacts
    "*.mp4", "*.jpg", "*.png"       # Media files
]
```

---

### 2. **database.py** - Data Persistence Layer

**Purpose**: SQLite database operations and schema management

**Schema Design**:

#### `file_changes` Table

```sql
CREATE TABLE file_changes (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    filepath TEXT,
    timestamp DATETIME,
    lines_added INTEGER,
    lines_removed INTEGER,
    lines_modified INTEGER,
    git_branch TEXT,
    commit_message TEXT,
    diff_content TEXT,          -- NULL in privacy mode
    file_hash TEXT,             -- SHA256 for change detection
    processed INTEGER DEFAULT 0  -- 0=unprocessed, 1=processed
)
```

#### `file_metadata` Table (Privacy Mode)

```sql
CREATE TABLE file_metadata (
    id INTEGER PRIMARY KEY,
    change_id INTEGER,
    functions_added TEXT,      -- JSON array
    functions_modified TEXT,   -- JSON array
    functions_removed TEXT,    -- JSON array
    classes_added TEXT,        -- JSON array
    classes_modified TEXT,     -- JSON array
    imports_changed TEXT,      -- JSON array
    FOREIGN KEY (change_id) REFERENCES file_changes(id)
)
```

#### `watch_paths` Table

```sql
CREATE TABLE watch_paths (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE,
    active INTEGER DEFAULT 1
)
```

#### `summary_logs` Table

```sql
CREATE TABLE summary_logs (
    id INTEGER PRIMARY KEY,
    date DATE,
    summary_text TEXT,
    total_files INTEGER,
    total_lines_added INTEGER,
    total_lines_removed INTEGER
)
```

**Key Operations**:

- `add_file_change()`: Record file modification
- `get_changes_by_date()`: Retrieve changes for summary
- `mark_as_processed()`: Mark changes as summarized
- `add_summary_log()`: Store generated summary
- `get_statistics()`: Analytics queries

**Performance Optimizations**:

- Indexed on `timestamp`, `processed`, `date` columns
- Connection pooling (sqlite3.Row for dict-like access)
- Efficient queries with parameterization

---

### 3. **watcher.py** - File System Monitoring

**Purpose**: Monitor file changes and compute diffs in real-time

**Key Components**:

#### **FileWatcher Class**

- Uses `watchdog` library for cross-platform file monitoring
- Supports recursive directory watching
- Event-driven architecture

#### **DevPulseEventHandler**

- Handles `FileModifiedEvent` from watchdog
- Filters files based on exclusion patterns
- Computes diffs and stores to database

#### **DiffAnalyzer**

```python
@staticmethod
def get_diff(old_content, new_content):
    """
    Returns: (diff_text, lines_added, lines_removed, lines_modified)
    """
    # Uses difflib.unified_diff
    # Counts +/- lines
    # Estimates modified lines
```

#### **CodeAnalyzer** (Privacy Mode)

- Extracts function/class names using regex
- Supports Python and JavaScript/TypeScript
- Compares old vs new symbols to detect changes

**Git Integration**:

```python
def get_git_branch(filepath):
    # Executes: git rev-parse --abbrev-ref HEAD

def get_last_commit_message(filepath):
    # Executes: git log -1 --pretty=%B -- <file>
```

**Caching Strategy**:

- Maintains in-memory cache: `{filepath: (hash, content)}`
- Compares SHA256 hashes to avoid redundant processing
- Only stores new diffs when hash changes

**Exclusion Logic**:

```python
def should_ignore(filepath):
    # Check file extension whitelist
    # Check filename patterns (fnmatch)
    # Check directory path components
```

---

### 4. **ai_summarizer.py** - AI Integration

**Purpose**: Generate human-readable summaries using Cloud AI APIs

**Supported Providers**:

| Provider | Library   | Model (Default)         |
| -------- | --------- | ----------------------- |
| Groq     | `groq`    | llama-3.1-70b-versatile |
| OpenAI   | `openai`  | gpt-4o-mini             |
| LiteLLM  | `litellm` | User-configurable       |

**AISummarizer Class**:

```python
class AISummarizer:
    def __init__(self, provider, api_key):
        self.client = self._init_client()

    def generate_summary(self, changes, privacy_mode):
        context = self._build_context(changes, privacy_mode)
        prompt = self._create_prompt(context, changes)
        return self._call_ai(prompt)
```

**Context Building**:

**Normal Mode**:

````
File: main.py
Path: /project/main.py
Branch: feature/auth
Stats: +45/-12
Commit: Added JWT authentication

Changes:
```diff
+ def authenticate_user(token):
+     return jwt.decode(token)
````

**Privacy Mode**:

```
File: main.py
Path: /project/main.py
Branch: feature/auth
Stats: +45/-12
Functions Added: [authenticate_user, validate_token]
Classes Added: [AuthMiddleware]
Commit: Added JWT authentication
```

**Prompt Engineering**:

```python
prompt = f"""
You are a professional software development assistant.
Generate a concise, professional "Daily Dev Log" summary.

**Context:**
- Total Files: {total_files}
- Lines Added: {total_added}
- Lines Removed: {total_removed}

**File Changes:**
{context}

**Instructions:**
1. Group related changes by feature
2. Use professional language
3. Focus on WHAT was accomplished
4. Bullet-point format
5. Organize by importance

**Output Format:**
✓ **[Feature Name]**
  • Task 1
  • Task 2
"""
```

**API Call Configuration**:

- Temperature: 0.3 (deterministic)
- Max tokens: 1000
- Timeout handling
- Error fallback to quick summary

---

### 5. **cli.py** - Command-Line Interface

**Purpose**: User-facing CLI commands using Click framework

**Command Structure**:

```
devpulse
├── track <path>        # Add directory to watch list
├── start               # Start file watcher
│   ├── --daemon        # Run in background
│   └── --privacy       # Enable privacy mode
├── log                 # Generate summary
│   ├── --today         # Today's log
│   ├── --date <date>   # Specific date
│   ├── --save          # Save to database
│   └── --no-ai         # Skip AI, quick summary
├── list                # Show watched directories
├── untrack <path>      # Remove from watch list
├── clear               # Clear history
│   └── --confirm       # Skip confirmation
├── stats               # Show statistics
│   └── --date <date>   # Date-specific stats
└── config              # Show configuration
```

**Signal Handling**:

```python
def signal_handler(sig, frame):
    watcher.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

**Error Handling**:

- Validates configuration before AI calls
- Graceful degradation (AI → Quick summary)
- User-friendly error messages

---

## 🔄 Data Flow

### 1. File Change Detection Flow

```
File Saved
    ↓
Watchdog Event (on_modified)
    ↓
DevPulseEventHandler.should_ignore()
    ├─ YES → Skip
    └─ NO → Continue
        ↓
Read File Content
    ↓
Compute SHA256 Hash
    ↓
Compare with Cache
    ├─ Same → Skip
    └─ Different → Continue
        ↓
Compute Diff (difflib)
    ↓
Get Git Info (branch, commit)
    ↓
Privacy Mode?
    ├─ YES → Extract Symbols (CodeAnalyzer)
    └─ NO → Store Full Diff
        ↓
Database.add_file_change()
    ↓
Update Cache
    ↓
Print Confirmation
```

### 2. Summary Generation Flow

```
devpulse log --today
    ↓
Validate Config
    ↓
Database.get_changes_by_date()
    ↓
Changes Found?
    ├─ NO → Exit ("No changes")
    └─ YES → Continue
        ↓
--no-ai Flag?
    ├─ YES → Quick Summary
    └─ NO → AI Summary
        ↓
    Build Context
        ↓
    Create Prompt
        ↓
    Call AI API
        ├─ Success → Return Summary
        └─ Error → Fallback to Quick Summary
            ↓
Display Summary
    ↓
--save Flag?
    ├─ YES → Store in summary_logs
    │        Mark changes as processed
    └─ NO → Done
```

---

## 🔒 Security & Privacy

### Privacy Mode Implementation

**Standard Mode**:

- Full code diffs sent to AI
- Maximum context for better summaries
- Suitable for personal projects

**Privacy Mode**:

- Only metadata sent (function/class names)
- No actual code content to AI
- Suitable for proprietary/sensitive code

**Data Flow Comparison**:

| Data Type       | Standard Mode | Privacy Mode |
| --------------- | ------------- | ------------ |
| File path       | ✓             | ✓            |
| Line counts     | ✓             | ✓            |
| Git branch      | ✓             | ✓            |
| Commit messages | ✓             | ✓            |
| Function names  | ✓             | ✓            |
| Class names     | ✓             | ✓            |
| **Code diffs**  | **✓**         | **✗**        |

### Security Best Practices

1. **API Key Storage**:

   - Environment variables only
   - Never in code or git
   - .env in .gitignore

2. **File Exclusion**:

   - Automatic exclusion of .env, keys, tokens
   - Pattern-based filtering
   - User can add custom patterns

3. **Local Data**:

   - SQLite in user's home directory
   - No cloud storage of code
   - User owns all data

4. **Git Integration**:
   - Read-only operations
   - No git modifications
   - Timeout protection (5s)

---

## ⚡ Performance Considerations

### File Watching Optimization

1. **Exclusion Patterns**: Skip heavy dirs early
2. **Hash Comparison**: Avoid redundant diff computation
3. **In-Memory Cache**: Fast lookup for file state
4. **Lazy Loading**: Only load file content when needed

### Database Optimization

1. **Indexes**: On timestamp, processed, date
2. **Prepared Statements**: SQL injection protection
3. **Batch Operations**: mark_as_processed accepts lists
4. **Connection Management**: Proper close() calls

### AI API Optimization

1. **Diff Truncation**: Limit to 1000 chars per file
2. **Batch Changes**: Single API call per day
3. **Token Efficiency**: Privacy mode reduces tokens
4. **Caching**: Summaries stored in database

---

## 🧪 Testing Strategy

### Unit Tests

- Database operations
- Diff computation
- Symbol extraction
- Exclusion logic

### Integration Tests

- File watcher with temp directories
- End-to-end CLI commands
- Database migrations

### Mock Tests

- AI API calls (avoid real API usage)
- Git commands
- File system operations

---

## 🚀 Deployment Strategies

### 1. Standalone CLI

```bash
pip install -e .
devpulse start
```

### 2. Systemd Service (Linux)

```bash
./scripts/install-linux-service.sh
sudo systemctl start devpulse
```

### 3. Windows Service (NSSM)

```powershell
.\scripts\install-windows-service.ps1 -DevPulsePath "C:\path\to\devpulse.exe" -ApiKey "..."
```

### 4. Docker Container (Future)

```dockerfile
FROM python:3.11-slim
COPY . /app
RUN pip install .
CMD ["devpulse", "start", "--daemon"]
```

---

## 📊 Future Enhancements

1. **Web Dashboard**: View logs in browser
2. **Multi-Language Support**: More symbol extractors
3. **Team Features**: Shared logs, collaboration
4. **Plugins**: Custom summarizers, exporters
5. **Analytics**: Productivity metrics, graphs
6. **Cloud Sync**: Optional cloud backup
7. **IDE Integration**: VSCode extension

---

## 🏁 Conclusion

DevPulse is designed as a **production-grade, modular** CLI tool with:

- Clean separation of concerns
- Extensible architecture
- Privacy-first approach
- Cross-platform support
- Minimal dependencies
- Professional code quality

The architecture balances **simplicity** (easy to understand and modify) with **robustness** (handles edge cases, errors gracefully).
