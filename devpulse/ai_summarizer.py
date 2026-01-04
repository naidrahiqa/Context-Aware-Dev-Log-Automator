"""
AI integration module for generating summaries
"""
from typing import List, Dict, Any, Optional
import os

from .config import AI_PROVIDER, get_api_key, get_model_name, PRIVACY_MODE


class AISummarizer:
    """AI-powered summary generator"""
    
    def __init__(self, provider: str = AI_PROVIDER, api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or get_api_key()
        self.model = get_model_name()
        
        if not self.api_key:
            raise ValueError("API key not set. Please set DEVPULSE_API_KEY environment variable.")
        
        # Initialize client based on provider
        self.client = self._init_client()
    
    def _init_client(self):
        """Initialize AI client based on provider"""
        if self.provider == "groq":
            try:
                from groq import Groq
                return Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError("groq package not installed. Run: pip install groq")
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        elif self.provider == "litellm":
            try:
                import litellm
                return litellm
            except ImportError:
                raise ImportError("litellm package not installed. Run: pip install litellm")
        
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def generate_summary(
        self, 
        changes: List[Dict[str, Any]], 
        privacy_mode: bool = PRIVACY_MODE
    ) -> str:
        """
        Generate a summary from file changes
        
        Args:
            changes: List of file change records from database
            privacy_mode: If True, only use metadata (function/class names)
        
        Returns:
            Human-readable summary text
        """
        if not changes:
            return "No changes tracked for this period."
        
        # Build context for AI
        context = self._build_context(changes, privacy_mode)
        
        # Create prompt
        prompt = self._create_prompt(context, changes)
        
        # Get summary from AI
        summary = self._call_ai(prompt)
        
        return summary
    
    def _build_context(
        self, 
        changes: List[Dict[str, Any]], 
        privacy_mode: bool
    ) -> str:
        """Build context string from changes"""
        context_parts = []
        
        for change in changes:
            filename = change['filename']
            filepath = change['filepath']
            lines_added = change['lines_added']
            lines_removed = change['lines_removed']
            git_branch = change.get('git_branch', 'N/A')
            commit_msg = change.get('commit_message', '')
            
            if privacy_mode:
                # Use only metadata
                entry = f"""
File: {filename}
Path: {filepath}
Branch: {git_branch}
Stats: +{lines_added}/-{lines_removed}
Commit: {commit_msg or 'No commit message'}
"""
            else:
                # Include diff content
                diff = change.get('diff_content', '')
                entry = f"""
File: {filename}
Path: {filepath}
Branch: {git_branch}
Stats: +{lines_added}/-{lines_removed}
Commit: {commit_msg or 'No commit message'}

Changes:
```
{diff[:1000]}  # Limit diff size
```
"""
            
            context_parts.append(entry.strip())
        
        return "\n\n---\n\n".join(context_parts)
    
    def _create_prompt(self, context: str, changes: List[Dict[str, Any]]) -> str:
        """Create AI prompt"""
        total_files = len(set(c['filepath'] for c in changes))
        total_added = sum(c['lines_added'] for c in changes)
        total_removed = sum(c['lines_removed'] for c in changes)
        
        prompt = f"""You are a professional software development assistant. Analyze the following code changes and generate a concise, professional "Daily Dev Log" or "Done List" summary.

**Context:**
- Total Files Modified: {total_files}
- Total Lines Added: {total_added}
- Total Lines Removed: {total_removed}

**File Changes:**
{context}

**Instructions:**
1. Group related changes by feature/component
2. Use professional, clear language
3. Focus on WHAT was accomplished, not HOW (avoid technical implementation details)
4. Format as a bulleted list
5. Be concise but informative
6. Organize by importance/impact

**Output Format:**
Return a professional bulleted list like:

✓ **[Feature/Component Name]**
  • Accomplished task 1
  • Accomplished task 2

✓ **[Another Feature]**
  • Accomplished task 3
"""
        
        return prompt
    
    def _call_ai(self, prompt: str) -> str:
        """Call AI API and get response"""
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional software development assistant that creates concise, informative daily development logs."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional software development assistant that creates concise, informative daily development logs."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == "litellm":
                response = self.client.completion(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional software development assistant that creates concise, informative daily development logs."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                    api_key=self.api_key
                )
                return response['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            raise Exception(f"AI API call failed: {str(e)}")
    
    def generate_quick_summary(self, changes: List[Dict[str, Any]]) -> str:
        """Generate a quick local summary without AI"""
        if not changes:
            return "No changes recorded."
        
        files = set(c['filename'] for c in changes)
        total_added = sum(c['lines_added'] for c in changes)
        total_removed = sum(c['lines_removed'] for c in changes)
        
        summary = f"""
📊 **Quick Summary**
• Files Modified: {len(files)}
• Lines Added: {total_added}
• Lines Removed: {total_removed}

📝 **Files:**
"""
        
        for file in sorted(files):
            file_changes = [c for c in changes if c['filename'] == file]
            added = sum(c['lines_added'] for c in file_changes)
            removed = sum(c['lines_removed'] for c in file_changes)
            summary += f"\n  • {file} (+{added}/-{removed})"
        
        return summary
