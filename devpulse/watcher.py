"""
File watcher implementation using watchdog
"""
import hashlib
import difflib
from pathlib import Path
from typing import Optional, List, Set
import fnmatch
import subprocess
import re

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

from .config import EXCLUSION_PATTERNS, TRACKED_EXTENSIONS
from .database import Database


class CodeAnalyzer:
    """Analyze code changes for privacy mode"""
    
    @staticmethod
    def extract_python_symbols(code: str) -> dict:
        """Extract function and class names from Python code"""
        functions = re.findall(r'^\s*def\s+(\w+)\s*\(', code, re.MULTILINE)
        classes = re.findall(r'^\s*class\s+(\w+)\s*[:\(]', code, re.MULTILINE)
        imports = re.findall(r'^\s*(?:from|import)\s+([^\s]+)', code, re.MULTILINE)
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports
        }
    
    @staticmethod
    def extract_js_symbols(code: str) -> dict:
        """Extract function and class names from JavaScript/TypeScript code"""
        functions = re.findall(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))', code, re.MULTILINE)
        classes = re.findall(r'class\s+(\w+)\s*[{]', code, re.MULTILINE)
        imports = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', code, re.MULTILINE)
        
        # Flatten tuple results
        functions = [f[0] or f[1] for f in functions]
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports
        }
    
    @staticmethod
    def extract_symbols(filepath: str, code: str) -> dict:
        """Extract symbols based on file extension"""
        ext = Path(filepath).suffix
        
        if ext == '.py':
            return CodeAnalyzer.extract_python_symbols(code)
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            return CodeAnalyzer.extract_js_symbols(code)
        else:
            return {'functions': [], 'classes': [], 'imports': []}


class DiffAnalyzer:
    """Analyze file diffs"""
    
    @staticmethod
    def compute_file_hash(filepath: Path) -> str:
        """Compute SHA256 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def get_diff(old_content: str, new_content: str) -> tuple[str, int, int, int]:
        """
        Compute diff between old and new content
        Returns: (diff_text, lines_added, lines_removed, lines_modified)
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
        diff_text = '\n'.join(diff)
        
        lines_added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        lines_removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        lines_modified = min(lines_added, lines_removed)
        
        return diff_text, lines_added, lines_removed, lines_modified
    
    @staticmethod
    def get_git_branch(filepath: Path) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=filepath.parent,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_last_commit_message(filepath: Path) -> Optional[str]:
        """Get last commit message for file"""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B', '--', str(filepath)],
                cwd=filepath.parent,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


class DevPulseEventHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, db: Database, privacy_mode: bool = False):
        self.db = db
        self.privacy_mode = privacy_mode
        self.file_cache: dict = {}  # filepath -> (hash, content)
    
    def should_ignore(self, filepath: str) -> bool:
        """Check if file should be ignored based on exclusion patterns"""
        path = Path(filepath)
        
        # Check if extension is tracked
        if TRACKED_EXTENSIONS and path.suffix not in TRACKED_EXTENSIONS:
            return True
        
        # Check exclusion patterns
        for pattern in EXCLUSION_PATTERNS:
            # Check filename
            if fnmatch.fnmatch(path.name, pattern):
                return True
            
            # Check full path parts
            for part in path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        
        return False
    
    def on_modified(self, event):
        """Handle file modification event"""
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        
        if self.should_ignore(str(filepath)):
            return
        
        try:
            self._process_file_change(filepath)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    def _process_file_change(self, filepath: Path):
        """Process a file change"""
        # Read new content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                new_content = f.read()
        except UnicodeDecodeError:
            # Skip binary files
            return
        except Exception as e:
            print(f"Could not read {filepath}: {e}")
            return
        
        # Compute new hash
        new_hash = DiffAnalyzer.compute_file_hash(filepath)
        
        # Get old content from cache
        old_hash, old_content = self.file_cache.get(str(filepath), ("", ""))
        
        # Skip if file hasn't changed
        if old_hash == new_hash:
            return
        
        # Compute diff
        if old_content:
            diff_text, lines_added, lines_removed, lines_modified = DiffAnalyzer.get_diff(
                old_content, new_content
            )
        else:
            # New file
            diff_text = new_content
            lines_added = len(new_content.splitlines())
            lines_removed = 0
            lines_modified = 0
        
        # Get git information
        git_branch = DiffAnalyzer.get_git_branch(filepath)
        commit_message = DiffAnalyzer.get_last_commit_message(filepath)
        
        # Store in database
        change_id = self.db.add_file_change(
            filename=filepath.name,
            filepath=str(filepath),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
            git_branch=git_branch,
            commit_message=commit_message,
            diff_content=diff_text if not self.privacy_mode else None,
            file_hash=new_hash
        )
        
        # Extract metadata for privacy mode
        if self.privacy_mode:
            old_symbols = CodeAnalyzer.extract_symbols(str(filepath), old_content) if old_content else {}
            new_symbols = CodeAnalyzer.extract_symbols(str(filepath), new_content)
            
            # Determine what changed
            old_funcs = set(old_symbols.get('functions', []))
            new_funcs = set(new_symbols.get('functions', []))
            old_classes = set(old_symbols.get('classes', []))
            new_classes = set(new_symbols.get('classes', []))
            old_imports = set(old_symbols.get('imports', []))
            new_imports = set(new_symbols.get('imports', []))
            
            self.db.add_file_metadata(
                change_id=change_id,
                functions_added=list(new_funcs - old_funcs),
                functions_modified=list(new_funcs & old_funcs),
                functions_removed=list(old_funcs - new_funcs),
                classes_added=list(new_classes - old_classes),
                classes_modified=list(new_classes & old_classes),
                imports_changed=list(new_imports ^ old_imports)
            )
        
        # Update cache
        self.file_cache[str(filepath)] = (new_hash, new_content)
        
        print(f"✓ Tracked: {filepath.name} (+{lines_added}/-{lines_removed})")


class FileWatcher:
    """Main file watcher class"""
    
    def __init__(self, paths: List[str], db: Database, privacy_mode: bool = False):
        self.paths = [Path(p).resolve() for p in paths]
        self.db = db
        self.privacy_mode = privacy_mode
        self.observer = Observer()
        self.event_handler = DevPulseEventHandler(db, privacy_mode)
    
    def start(self):
        """Start watching files"""
        for path in self.paths:
            if not path.exists():
                print(f"Warning: Path does not exist: {path}")
                continue
            
            self.observer.schedule(
                self.event_handler,
                str(path),
                recursive=True
            )
            print(f"👁️  Watching: {path}")
        
        self.observer.start()
        print("DevPulse is now tracking your changes...")
    
    def stop(self):
        """Stop watching files"""
        self.observer.stop()
        self.observer.join()
