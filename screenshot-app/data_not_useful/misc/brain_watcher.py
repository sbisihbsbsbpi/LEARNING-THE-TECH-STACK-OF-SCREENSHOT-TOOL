#!/usr/bin/env python3
"""
Project Brain Watcher - Auto-updating file index
Monitors file system changes and updates index in real-time
"""

import time
import sys
from pathlib import Path

# Optional watchdog integration
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

from project_brain import ProjectBrain


class ProjectBrainWatcher(FileSystemEventHandler):
    """File system event handler that updates Project Brain index"""
    
    def __init__(self, brain: ProjectBrain):
        self.brain = brain
        self.last_update = time.time()
        self.pending_updates = set()
        self.debounce_seconds = 2  # Wait 2 seconds before updating
    
    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Skip hidden files and common ignore patterns
        if file_path.name.startswith('.'):
            return
        if any(part in file_path.parts for part in ['node_modules', '__pycache__', '.git', 'dist', 'build']):
            return
        
        self.pending_updates.add(file_path)
        print(f"📝 Detected change: {file_path.name}")
    
    def on_created(self, event):
        """Handle file creation"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Skip hidden files and common ignore patterns
        if file_path.name.startswith('.'):
            return
        if any(part in file_path.parts for part in ['node_modules', '__pycache__', '.git', 'dist', 'build']):
            return
        
        self.pending_updates.add(file_path)
        print(f"✨ Detected new file: {file_path.name}")
    
    def on_deleted(self, event):
        """Handle file deletion"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        rel_path = str(file_path.relative_to(self.brain.root))
        
        # Remove from index
        if rel_path in self.brain.index:
            del self.brain.index[rel_path]
            print(f"🗑️  Removed from index: {file_path.name}")
            self.brain.save_index()
    
    def process_pending_updates(self):
        """Process pending file updates (debounced)"""
        if not self.pending_updates:
            return
        
        # Check if enough time has passed since last update
        if time.time() - self.last_update < self.debounce_seconds:
            return
        
        print(f"\n🔄 Updating index for {len(self.pending_updates)} files...")
        
        for file_path in self.pending_updates:
            try:
                rel_path = file_path.relative_to(self.brain.root)
                
                # Skip large files
                if file_path.stat().st_size > 500_000:
                    continue
                
                # Read file preview
                preview = ""
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        preview = f.read(500)
                except Exception:
                    pass
                
                # Update index
                file_hash = self.brain._hash_file(file_path)
                self.brain.file_hashes[str(rel_path)] = file_hash
                
                self.brain.index[str(rel_path)] = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "rel_path": str(rel_path),
                    "type": file_path.suffix,
                    "size": file_path.stat().st_size,
                    "modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(file_path.stat().st_mtime)),
                    "category": self.brain._categorize_file(str(rel_path)),
                    "purpose": self.brain._infer_purpose(file_path.name, str(rel_path)),
                    "hash": file_hash,
                    "preview": preview,
                }
                
                # Extract dependencies
                if file_path.suffix == '.py':
                    self.brain._extract_python_dependencies(file_path, str(rel_path))
                elif file_path.suffix in ['.ts', '.tsx', '.js', '.jsx']:
                    self.brain._extract_js_dependencies(file_path, str(rel_path))
                
            except Exception as e:
                print(f"  ⚠️  Error updating {file_path.name}: {e}")
        
        # Rebuild graph if enabled
        if self.brain.graph_enabled:
            self.brain._build_graph()
        
        # Save index
        self.brain.save_index()
        print(f"✅ Index updated!\n")
        
        # Clear pending updates
        self.pending_updates.clear()
        self.last_update = time.time()


def start_watcher(project_path: str):
    """Start watching project for file changes"""
    if not WATCHDOG_AVAILABLE:
        print("❌ Watchdog not installed. Run: pip install watchdog")
        return
    
    print("=" * 60)
    print("🧠 PROJECT BRAIN WATCHER")
    print("=" * 60)
    print("Monitoring file changes and auto-updating index...")
    print("Press Ctrl+C to stop\n")
    
    # Initialize brain
    brain = ProjectBrain(project_path)
    
    # Load existing index
    index_file = brain.root / "project_index.json"
    if index_file.exists():
        print("📖 Loading existing index...")
        import json
        with open(index_file) as f:
            data = json.load(f)
            brain.index = data['index']
            brain.dependencies = {k: set(v) for k, v in data['dependencies'].items()}
            brain.file_hashes = data.get('file_hashes', {})
        print(f"✅ Loaded {len(brain.index)} files from index\n")
    else:
        print("🔍 Scanning project (first time)...")
        brain.scan_project()
        brain.save_index()
        print()
    
    # Create event handler and observer
    event_handler = ProjectBrainWatcher(brain)
    observer = Observer()
    observer.schedule(event_handler, str(brain.root), recursive=True)
    observer.start()
    
    print("👀 Watching for changes...\n")
    
    try:
        while True:
            time.sleep(1)
            # Process pending updates (debounced)
            event_handler.process_pending_updates()
    except KeyboardInterrupt:
        print("\n\n👋 Stopping watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Watcher stopped")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
    
    start_watcher(project_path)


if __name__ == "__main__":
    main()

