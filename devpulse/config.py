"""
Configuration management for DevPulse
"""
import os
from pathlib import Path
from typing import Optional

# Application directories
APP_NAME = "devpulse"
HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / f".{APP_NAME}"
DB_PATH = CONFIG_DIR / "devpulse.db"
WATCH_LIST_FILE = CONFIG_DIR / "watch_paths.txt"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# AI Provider Configuration
AI_PROVIDER = os.getenv("DEVPULSE_AI_PROVIDER", "groq")  # groq, openai, or litellm
API_KEY = os.getenv("DEVPULSE_API_KEY", "")

# Model configurations
GROQ_MODEL = "llama-3.1-70b-versatile"
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini/gemini-1.5-flash"  # LiteLLM format for Gemini
LITELLM_MODEL = os.getenv("DEVPULSE_MODEL", "gemini/gemini-1.5-flash")

# Privacy settings
PRIVACY_MODE = os.getenv("DEVPULSE_PRIVACY_MODE", "false").lower() == "true"

# Exclusion patterns (files/dirs to ignore)
EXCLUSION_PATTERNS = [
    # Environment and secrets
    ".env", ".env.*", "*.key", "*.pem", "*.cert", 
    "credentials.json", "secrets.*",
    
    # Dependencies
    "node_modules", "venv", "env", ".venv", 
    "vendor", "__pycache__", "*.pyc",
    
    # Build artifacts
    "dist", "build", "out", "target", ".next",
    "*.egg-info", ".tsbuildinfo",
    
    # Version control
    ".git", ".svn", ".hg",
    
    # IDE
    ".vscode", ".idea", "*.swp", "*.swo",
    
    # OS
    ".DS_Store", "Thumbs.db",
    
    # Media files (usually large)
    "*.mp4", "*.avi", "*.mov", "*.mkv",
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp",
]

# File extensions to track (empty = track all)
TRACKED_EXTENSIONS = [
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".go", ".rs", ".c", ".cpp", ".h", ".hpp",
    ".java", ".kt", ".swift",
    ".rb", ".php",
    ".html", ".css", ".scss", ".sass",
    ".sql", ".sh", ".bash",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt",
]


def get_api_key() -> Optional[str]:
    """Get API key from environment"""
    if not API_KEY:
        return None
    return API_KEY


def get_model_name() -> str:
    """Get model name based on provider"""
    if AI_PROVIDER == "groq":
        return GROQ_MODEL
    elif AI_PROVIDER == "openai":
        return OPENAI_MODEL
    elif AI_PROVIDER == "gemini":
        return GEMINI_MODEL
    elif AI_PROVIDER == "litellm":
        return LITELLM_MODEL
    else:
        return os.getenv("DEVPULSE_MODEL", "gpt-3.5-turbo")


def validate_config() -> tuple[bool, str]:
    """Validate configuration"""
    if not API_KEY:
        return False, "DEVPULSE_API_KEY environment variable not set"
    
    if AI_PROVIDER not in ["groq", "openai", "litellm", "gemini"]:
        return False, f"Invalid AI provider: {AI_PROVIDER}"
    
    return True, "Configuration valid"
