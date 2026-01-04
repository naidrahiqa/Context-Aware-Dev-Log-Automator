#!/usr/bin/env python3
"""
DevPulse CLI - Command Line Interface
"""
import sys
from datetime import datetime, date
from pathlib import Path
import time
import signal

import click

from devpulse.config import validate_config, PRIVACY_MODE, CONFIG_DIR
from devpulse.database import Database
from devpulse.watcher import FileWatcher
from devpulse.ai_summarizer import AISummarizer


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    DevPulse - Automated Dev Log Generator
    
    Track your coding activity and generate AI-powered daily summaries.
    """
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def track(path):
    """
    Add a directory to the watch list and start tracking.
    
    Example: devpulse track /path/to/project
    """
    abs_path = str(Path(path).resolve())
    db = Database()
    
    if db.add_watch_path(abs_path):
        click.echo(f"✓ Added to watch list: {abs_path}")
    else:
        click.echo(f"⚠ Path already being tracked: {abs_path}")
    
    click.echo("\nRun 'devpulse start' to begin tracking changes.")


@cli.command()
@click.option('--daemon', '-d', is_flag=True, help='Run as background daemon')
@click.option('--privacy', '-p', is_flag=True, help='Enable privacy mode')
def start(daemon, privacy):
    """
    Start tracking file changes in all watched directories.
    
    Use --daemon to run in background.
    """
    db = Database()
    watch_paths = db.get_watch_paths()
    
    if not watch_paths:
        click.echo("❌ No directories being tracked.")
        click.echo("Add a directory with: devpulse track <path>")
        return
    
    click.echo("🚀 Starting DevPulse...")
    click.echo(f"Privacy Mode: {'✓ Enabled' if privacy or PRIVACY_MODE else '✗ Disabled'}")
    click.echo(f"Watching {len(watch_paths)} path(s)\n")
    
    watcher = FileWatcher(watch_paths, db, privacy_mode=privacy or PRIVACY_MODE)
    
    def signal_handler(sig, frame):
        click.echo("\n\n⏹️  Stopping DevPulse...")
        watcher.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    watcher.start()
    
    if daemon:
        click.echo("Running in daemon mode. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n\n⏹️  Stopping DevPulse...")
        watcher.stop()


@cli.command()
@click.option('--today', is_flag=True, help='Generate summary for today')
@click.option('--date', '-d', 'date_str', type=str, help='Generate summary for specific date (YYYY-MM-DD)')
@click.option('--save', '-s', is_flag=True, help='Save summary to database')
@click.option('--no-ai', is_flag=True, help='Skip AI and generate quick summary')
def log(today, date_str, save, no_ai):
    """
    Generate a development log summary.
    
    Examples:
      devpulse log --today
      devpulse log --date 2026-01-01
    """
    if not today and not date_str:
        click.echo("❌ Please specify --today or --date")
        return
    
    # Validate config
    valid, msg = validate_config()
    if not valid and not no_ai:
        click.echo(f"❌ Configuration error: {msg}")
        click.echo("\nSet environment variable: DEVPULSE_API_KEY")
        click.echo("Use --no-ai flag to skip AI summary.")
        return
    
    # Determine date
    target_date = date.today().isoformat() if today else date_str
    
    # Get changes
    db = Database()
    changes = db.get_changes_by_date(target_date, processed=False)
    
    if not changes:
        click.echo(f"📭 No changes recorded for {target_date}")
        return
    
    click.echo(f"📊 Found {len(changes)} change(s) for {target_date}\n")
    
    # Generate summary
    if no_ai:
        summarizer = AISummarizer()
        summary = summarizer.generate_quick_summary(changes)
    else:
        click.echo("🤖 Generating AI summary...")
        try:
            summarizer = AISummarizer()
            summary = summarizer.generate_summary(changes)
        except Exception as e:
            click.echo(f"❌ AI summary failed: {e}")
            click.echo("\nGenerating quick summary instead...\n")
            summary = summarizer.generate_quick_summary(changes)
    
    # Display summary
    click.echo("\n" + "="*60)
    click.echo(f"  DEV LOG - {target_date}")
    click.echo("="*60 + "\n")
    click.echo(summary)
    click.echo("\n" + "="*60 + "\n")
    
    # Save summary
    if save:
        stats = db.get_statistics(target_date)
        db.add_summary_log(
            date=target_date,
            summary_text=summary,
            total_files=stats['unique_files'] or 0,
            total_lines_added=stats['total_added'] or 0,
            total_lines_removed=stats['total_removed'] or 0
        )
        
        # Mark changes as processed
        change_ids = [c['id'] for c in changes]
        db.mark_as_processed(change_ids)
        
        click.echo("✓ Summary saved to database")


@cli.command()
def list():
    """List all watched directories."""
    db = Database()
    paths = db.get_watch_paths()
    
    if not paths:
        click.echo("No directories being tracked.")
        click.echo("Add one with: devpulse track <path>")
        return
    
    click.echo(f"📂 Watching {len(paths)} path(s):\n")
    for i, path in enumerate(paths, 1):
        click.echo(f"  {i}. {path}")


@cli.command()
@click.argument('path', type=str)
def untrack(path):
    """Remove a directory from watch list."""
    db = Database()
    db.remove_watch_path(path)
    click.echo(f"✓ Removed from watch list: {path}")


@cli.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def clear(confirm):
    """Clear all tracked changes history."""
    if not confirm:
        click.confirm(
            '⚠️  This will delete all tracked changes. Continue?',
            abort=True
        )
    
    db = Database()
    db.clear_history()
    click.echo("✓ History cleared")


@cli.command()
@click.option('--date', '-d', type=str, help='Get stats for specific date (YYYY-MM-DD)')
def stats(date_str):
    """Show statistics about tracked changes."""
    db = Database()
    
    if date_str:
        stats_data = db.get_statistics(date_str)
        click.echo(f"\n📊 Statistics for {date_str}:\n")
    else:
        stats_data = db.get_statistics()
        click.echo(f"\n📊 Overall Statistics:\n")
    
    click.echo(f"  Total Changes: {stats_data['total_changes']}")
    click.echo(f"  Unique Files: {stats_data['unique_files']}")
    click.echo(f"  Lines Added: {stats_data['total_added']}")
    click.echo(f"  Lines Removed: {stats_data['total_removed']}")
    click.echo(f"  Lines Modified: {stats_data['total_modified']}\n")


@cli.command()
def config():
    """Show current configuration."""
    from devpulse.config import (
        AI_PROVIDER, PRIVACY_MODE, CONFIG_DIR, 
        DB_PATH, get_model_name
    )
    
    valid, msg = validate_config()
    
    click.echo("\n⚙️  DevPulse Configuration:\n")
    click.echo(f"  Config Directory: {CONFIG_DIR}")
    click.echo(f"  Database: {DB_PATH}")
    click.echo(f"  AI Provider: {AI_PROVIDER}")
    click.echo(f"  Model: {get_model_name()}")
    click.echo(f"  Privacy Mode: {'✓ Enabled' if PRIVACY_MODE else '✗ Disabled'}")
    click.echo(f"  API Key: {'✓ Set' if valid else '✗ Not Set'}")
    
    if not valid:
        click.echo(f"\n⚠️  {msg}")
    click.echo()


def main():
    """Entry point for CLI"""
    cli()


if __name__ == '__main__':
    main()
