#!/usr/bin/env python3
"""
Project Brain Context Continuity System
Your "bookmark of cognition" - remembers where you left off and helps you resume work
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class ContextContinuity:
    """Tracks work sessions and provides smart recaps"""
    
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.context_file = self.root / ".brain_context.json"
        self.sessions: List[Dict] = []
        self.current_session: Optional[Dict] = None
        self.load_context()
    
    def load_context(self):
        """Load existing context data"""
        if self.context_file.exists():
            with open(self.context_file, 'r') as f:
                data = json.load(f)
                self.sessions = data.get('sessions', [])
    
    def save_context(self):
        """Save context data"""
        data = {
            'sessions': self.sessions,
            'last_updated': datetime.now().isoformat(),
        }
        with open(self.context_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_session(self, description: str = ""):
        """Start a new work session"""
        self.current_session = {
            'id': len(self.sessions) + 1,
            'start_time': datetime.now().isoformat(),
            'description': description,
            'files_edited': [],
            'files_viewed': [],
            'commands_run': [],
            'notes': [],
            'commits': [],
        }
        print(f"📝 Started session #{self.current_session['id']}")
        if description:
            print(f"   Description: {description}")
    
    def end_session(self, summary: str = ""):
        """End current work session"""
        if not self.current_session:
            print("⚠️  No active session")
            return
        
        self.current_session['end_time'] = datetime.now().isoformat()
        self.current_session['summary'] = summary
        
        # Calculate duration
        start = datetime.fromisoformat(self.current_session['start_time'])
        end = datetime.fromisoformat(self.current_session['end_time'])
        duration = end - start
        self.current_session['duration_minutes'] = int(duration.total_seconds() / 60)
        
        self.sessions.append(self.current_session)
        self.save_context()
        
        print(f"✅ Ended session #{self.current_session['id']}")
        print(f"   Duration: {self.current_session['duration_minutes']} minutes")
        print(f"   Files edited: {len(self.current_session['files_edited'])}")
        
        self.current_session = None
    
    def track_file_edit(self, file_path: str):
        """Track a file being edited"""
        if not self.current_session:
            return
        
        if file_path not in self.current_session['files_edited']:
            self.current_session['files_edited'].append(file_path)
            print(f"📝 Tracked edit: {file_path}")
    
    def track_file_view(self, file_path: str):
        """Track a file being viewed"""
        if not self.current_session:
            return
        
        if file_path not in self.current_session['files_viewed']:
            self.current_session['files_viewed'].append(file_path)
    
    def track_command(self, command: str):
        """Track a command being run"""
        if not self.current_session:
            return
        
        self.current_session['commands_run'].append({
            'command': command,
            'timestamp': datetime.now().isoformat(),
        })
    
    def add_note(self, note: str):
        """Add a note to current session"""
        if not self.current_session:
            print("⚠️  No active session. Start one with: start <description>")
            return
        
        self.current_session['notes'].append({
            'note': note,
            'timestamp': datetime.now().isoformat(),
        })
        print(f"📌 Note added: {note}")
    
    def get_last_session(self) -> Optional[Dict]:
        """Get the most recent session"""
        if not self.sessions:
            return None
        return self.sessions[-1]
    
    def get_recent_sessions(self, days: int = 7) -> List[Dict]:
        """Get sessions from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for session in self.sessions:
            session_time = datetime.fromisoformat(session['start_time'])
            if session_time >= cutoff:
                recent.append(session)
        
        return recent
    
    def get_git_commits_since(self, since_date: str) -> List[Dict]:
        """Get git commits since a specific date"""
        try:
            # Get commits since date
            cmd = f'git log --since="{since_date}" --pretty=format:"%H|%an|%ad|%s" --date=iso'
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0][:8],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3],
                    })
            
            return commits
        except Exception:
            return []
    
    def get_git_changed_files_since(self, since_date: str) -> List[str]:
        """Get files changed in git since a specific date"""
        try:
            cmd = f'git log --since="{since_date}" --name-only --pretty=format: | sort -u'
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return []
            
            files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            return files
        except Exception:
            return []
    
    def generate_recap(self) -> Dict:
        """Generate a comprehensive recap of recent work"""
        last_session = self.get_last_session()
        
        if not last_session:
            return {
                'message': "👋 Welcome! This is your first session.",
                'suggestions': ["Start a new session with: start <description>"]
            }
        
        # Calculate time since last session
        last_time = datetime.fromisoformat(last_session['start_time'])
        time_away = datetime.now() - last_time
        days_away = time_away.days
        
        # Get recent sessions
        recent_sessions = self.get_recent_sessions(days=30)
        
        # Get git commits since last session
        commits = self.get_git_commits_since(last_session['start_time'])
        
        # Get changed files
        changed_files = self.get_git_changed_files_since(last_session['start_time'])
        
        # Aggregate frequently edited files
        file_frequency = defaultdict(int)
        for session in recent_sessions:
            for file in session.get('files_edited', []):
                file_frequency[file] += 1
        
        top_files = sorted(file_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        recap = {
            'time_away_days': days_away,
            'last_session': last_session,
            'recent_sessions_count': len(recent_sessions),
            'commits_since_last': commits,
            'changed_files': changed_files,
            'frequently_edited': top_files,
            'total_sessions': len(self.sessions),
        }
        
        return recap
    
    def print_recap(self):
        """Print a beautiful recap"""
        recap = self.generate_recap()
        
        if 'message' in recap:
            print(recap['message'])
            return
        
        print("\n" + "=" * 70)
        print("🧠 CONTEXT CONTINUITY - WELCOME BACK!")
        print("=" * 70)
        
        # Time away
        days = recap['time_away_days']
        if days == 0:
            print("\n⏰ You were here earlier today")
        elif days == 1:
            print("\n⏰ You were here yesterday")
        else:
            print(f"\n⏰ You've been away for {days} days")
        
        # Last session recap
        last = recap['last_session']
        print(f"\n📝 Last Session (#{last['id']}):")
        print(f"   Started: {last['start_time'][:19]}")
        if last.get('description'):
            print(f"   Description: {last['description']}")
        if last.get('summary'):
            print(f"   Summary: {last['summary']}")
        print(f"   Duration: {last.get('duration_minutes', 0)} minutes")
        
        # Files edited in last session
        if last.get('files_edited'):
            print(f"\n📄 Files You Were Working On:")
            for file in last['files_edited'][:5]:
                print(f"   • {file}")
        
        # Notes from last session
        if last.get('notes'):
            print(f"\n📌 Your Notes:")
            for note_obj in last['notes']:
                print(f"   • {note_obj['note']}")
        
        # Recent commits
        if recap['commits_since_last']:
            print(f"\n🔄 Commits Since Last Session ({len(recap['commits_since_last'])}):")
            for commit in recap['commits_since_last'][:5]:
                print(f"   {commit['hash']} - {commit['message']}")
                print(f"   └─ by {commit['author']} on {commit['date'][:10]}")
        
        # Changed files
        if recap['changed_files']:
            print(f"\n📝 Files Changed Since Last Session ({len(recap['changed_files'])}):")
            for file in recap['changed_files'][:10]:
                print(f"   • {file}")
        
        # Frequently edited files
        if recap['frequently_edited']:
            print(f"\n🔥 Your Most Edited Files (Last 30 Days):")
            for file, count in recap['frequently_edited']:
                print(f"   • {file} ({count} edits)")
        
        # Recent activity summary
        print(f"\n📊 Recent Activity (Last 30 Days):")
        print(f"   Sessions: {recap['recent_sessions_count']}")
        print(f"   Total Sessions Ever: {recap['total_sessions']}")
        
        # Suggestions
        print(f"\n💡 Suggestions:")
        if last.get('files_edited'):
            print(f"   • Continue working on: {last['files_edited'][0]}")
        if recap['commits_since_last']:
            print(f"   • Review recent commits: git log --since=\"{last['start_time'][:10]}\"")
        print(f"   • Start new session: start <description>")
        print(f"   • Add note: note <your note>")
        
        print("\n" + "=" * 70 + "\n")


def main():
    """Main CLI for context continuity"""
    import sys
    
    project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
    context = ContextContinuity(project_path)
    
    if len(sys.argv) < 2:
        # No command - show recap
        context.print_recap()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        description = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        context.start_session(description)
        context.save_context()
    
    elif command == 'end':
        summary = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        context.end_session(summary)
    
    elif command == 'note':
        note = ' '.join(sys.argv[2:])
        if not note:
            print("❌ Please provide a note")
            return
        context.add_note(note)
        context.save_context()
    
    elif command == 'edit':
        file_path = ' '.join(sys.argv[2:])
        if not file_path:
            print("❌ Please provide a file path")
            return
        context.track_file_edit(file_path)
        context.save_context()
    
    elif command == 'recap':
        context.print_recap()
    
    elif command == 'sessions':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        sessions = context.get_recent_sessions(days)
        
        print(f"\n📊 Sessions (Last {days} Days):\n")
        for session in sessions:
            print(f"Session #{session['id']} - {session['start_time'][:19]}")
            if session.get('description'):
                print(f"  Description: {session['description']}")
            print(f"  Duration: {session.get('duration_minutes', 0)} minutes")
            print(f"  Files edited: {len(session.get('files_edited', []))}")
            print()
    
    elif command == 'help':
        print("\n🧠 Context Continuity Commands:\n")
        print("  recap              - Show welcome back recap (default)")
        print("  start <desc>       - Start a new work session")
        print("  end <summary>      - End current session")
        print("  note <text>        - Add a note to current session")
        print("  edit <file>        - Track a file edit")
        print("  sessions [days]    - Show recent sessions")
        print("  help               - Show this help\n")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python3 brain_context.py help' for usage")


if __name__ == "__main__":
    main()

