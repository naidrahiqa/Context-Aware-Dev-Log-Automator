"""
Database schema and operations for DevPulse
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from .config import DB_PATH


class Database:
    """SQLite database manager for DevPulse"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # File changes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                lines_added INTEGER DEFAULT 0,
                lines_removed INTEGER DEFAULT 0,
                lines_modified INTEGER DEFAULT 0,
                git_branch TEXT,
                commit_message TEXT,
                diff_content TEXT,
                file_hash TEXT,
                processed INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Watch paths table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watch_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Metadata for privacy mode
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_id INTEGER NOT NULL,
                functions_added TEXT,
                functions_modified TEXT,
                functions_removed TEXT,
                classes_added TEXT,
                classes_modified TEXT,
                imports_changed TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (change_id) REFERENCES file_changes(id)
            )
        """)
        
        # Summary logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summary_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                summary_text TEXT NOT NULL,
                total_files INTEGER DEFAULT 0,
                total_lines_added INTEGER DEFAULT 0,
                total_lines_removed INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON file_changes(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_processed 
            ON file_changes(processed)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_date 
            ON summary_logs(date)
        """)
        
        conn.commit()
        conn.close()
    
    def add_file_change(
        self,
        filename: str,
        filepath: str,
        lines_added: int = 0,
        lines_removed: int = 0,
        lines_modified: int = 0,
        git_branch: Optional[str] = None,
        commit_message: Optional[str] = None,
        diff_content: Optional[str] = None,
        file_hash: Optional[str] = None
    ) -> int:
        """Add a file change record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO file_changes 
            (filename, filepath, lines_added, lines_removed, lines_modified,
             git_branch, commit_message, diff_content, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, filepath, lines_added, lines_removed, lines_modified,
            git_branch, commit_message, diff_content, file_hash
        ))
        
        change_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return change_id
    
    def add_file_metadata(
        self,
        change_id: int,
        functions_added: List[str] = None,
        functions_modified: List[str] = None,
        functions_removed: List[str] = None,
        classes_added: List[str] = None,
        classes_modified: List[str] = None,
        imports_changed: List[str] = None
    ):
        """Add metadata for privacy mode"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO file_metadata
            (change_id, functions_added, functions_modified, functions_removed,
             classes_added, classes_modified, imports_changed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            change_id,
            json.dumps(functions_added or []),
            json.dumps(functions_modified or []),
            json.dumps(functions_removed or []),
            json.dumps(classes_added or []),
            json.dumps(classes_modified or []),
            json.dumps(imports_changed or [])
        ))
        
        conn.commit()
        conn.close()
    
    def get_changes_by_date(
        self, 
        date: str, 
        processed: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get file changes for a specific date"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM file_changes 
            WHERE DATE(timestamp) = ?
        """
        params = [date]
        
        if processed is not None:
            query += " AND processed = ?"
            params.append(1 if processed else 0)
        
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def mark_as_processed(self, change_ids: List[int]):
        """Mark changes as processed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholders = ",".join(["?" for _ in change_ids])
        cursor.execute(
            f"UPDATE file_changes SET processed = 1 WHERE id IN ({placeholders})",
            change_ids
        )
        
        conn.commit()
        conn.close()
    
    def add_summary_log(
        self,
        date: str,
        summary_text: str,
        total_files: int,
        total_lines_added: int,
        total_lines_removed: int
    ):
        """Add a summary log entry"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO summary_logs
            (date, summary_text, total_files, total_lines_added, total_lines_removed)
            VALUES (?, ?, ?, ?, ?)
        """, (date, summary_text, total_files, total_lines_added, total_lines_removed))
        
        conn.commit()
        conn.close()
    
    def add_watch_path(self, path: str) -> bool:
        """Add a path to watch list"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO watch_paths (path) VALUES (?)", (path,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Path already exists
    
    def get_watch_paths(self) -> List[str]:
        """Get all active watch paths"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM watch_paths WHERE active = 1")
        paths = [row["path"] for row in cursor.fetchall()]
        conn.close()
        return paths
    
    def remove_watch_path(self, path: str):
        """Remove a watch path"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE watch_paths SET active = 0 WHERE path = ?", (path,))
        conn.commit()
        conn.close()
    
    def clear_history(self):
        """Clear all history data"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM file_changes")
        cursor.execute("DELETE FROM file_metadata")
        cursor.execute("DELETE FROM summary_logs")
        
        conn.commit()
        conn.close()
    
    def get_statistics(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a date or overall"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if date:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_changes,
                    COUNT(DISTINCT filepath) as unique_files,
                    SUM(lines_added) as total_added,
                    SUM(lines_removed) as total_removed,
                    SUM(lines_modified) as total_modified
                FROM file_changes
                WHERE DATE(timestamp) = ?
            """, (date,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_changes,
                    COUNT(DISTINCT filepath) as unique_files,
                    SUM(lines_added) as total_added,
                    SUM(lines_removed) as total_removed,
                    SUM(lines_modified) as total_modified
                FROM file_changes
            """)
        
        stats = dict(cursor.fetchone())
        conn.close()
        return stats
