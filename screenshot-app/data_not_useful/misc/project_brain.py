#!/usr/bin/env python3
"""
Project Brain - Intelligent File Management System
Knows what files exist, what they do, and finds what you need instantly

Enhanced with OpenAI for semantic understanding (optional)
"""

import os
import json
import ast
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
from collections import defaultdict

# Optional OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

# Optional NetworkX for graph intelligence
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

class ProjectBrain:
    """
    An intelligent system that:
    1. Maps your entire project structure
    2. Understands file purposes and relationships
    3. Finds files based on intent/purpose
    4. Tracks dependencies and usage
    5. Suggests what you need before you ask
    """
    
    def __init__(self, root_dir: str, openai_api_key: Optional[str] = None):
        self.root = Path(root_dir)
        self.index: Dict = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.file_purposes: Dict[str, str] = {}
        self.activity_log: List[Dict] = []

        # OpenAI configuration (optional)
        self.openai_enabled = False
        if openai_api_key and OPENAI_AVAILABLE:
            openai.api_key = openai_api_key
            self.openai_enabled = True
            print("🤖 OpenAI integration enabled for semantic search!")
        elif openai_api_key and not OPENAI_AVAILABLE:
            print("⚠️  OpenAI requested but not installed. Run: pip install openai")

        # File content hashes for change detection
        self.file_hashes: Dict[str, str] = {}

        # Graph intelligence (optional)
        self.graph_enabled = NETWORKX_AVAILABLE
        self.graph = None
        if NETWORKX_AVAILABLE:
            self.graph = nx.DiGraph()
            print("📊 Graph intelligence enabled!")
        else:
            print("ℹ️  NetworkX not installed. Run: pip install networkx for graph features")
        
        # Intent mapping - what files do what
        self.intent_map = {
            "screenshot": ["screenshot_service.py", "main.py"],
            "database": ["config.py", "auth_state.json"],
            "frontend": ["App.tsx", "main.tsx", "styles.css"],
            "backend": ["main.py", "screenshot_service.py", "document_service.py"],
            "api": ["main.py"],
            "config": ["config.py", "settings"],
            "auth": ["auth_state.json", "screenshot_service.py"],
            "document": ["document_service.py"],
            "quality": ["quality_checker.py"],
            "logging": ["logging_config.py"],
            "stealth": ["screenshot_service.py"],
            "test": ["test_", "check_"],
            "docs": [".md"],
        }
        
        # File type categories
        self.categories = {
            "production": ["main.py", "screenshot_service.py", "document_service.py", 
                          "quality_checker.py", "logging_config.py", "config.py",
                          "App.tsx", "main.tsx", "styles.css"],
            "config": ["config.py", "requirements.txt", "package.json", "tsconfig.json"],
            "test": ["test_", "check_"],
            "docs": [".md"],
            "archived": ["misc-code/"],
            "runtime": ["auth_state.json", "screenshots/", "logs/", "output/"],
        }
    
    def _hash_file(self, file_path: Path) -> str:
        """Generate MD5 hash of file content"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def scan_project(self) -> Dict:
        """Scan entire project and build comprehensive index"""
        print("🧠 Scanning project structure...")

        for root, dirs, files in os.walk(self.root):
            # Skip common ignore patterns
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'dist', 'build']]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.root)

                # Skip large binary files (>500KB)
                if file_path.stat().st_size > 500_000:
                    continue

                # Generate file hash
                file_hash = self._hash_file(file_path)
                self.file_hashes[str(rel_path)] = file_hash

                # Read file preview (first 500 chars for semantic search)
                preview = ""
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        preview = f.read(500)
                except Exception:
                    pass

                self.index[str(rel_path)] = {
                    "name": file,
                    "path": str(file_path),
                    "rel_path": str(rel_path),
                    "type": file_path.suffix,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "category": self._categorize_file(str(rel_path)),
                    "purpose": self._infer_purpose(file, str(rel_path)),
                    "hash": file_hash,
                    "preview": preview,
                }

                # Extract dependencies for Python files
                if file.endswith('.py'):
                    self._extract_python_dependencies(file_path, str(rel_path))

                # Extract dependencies for TypeScript/JavaScript files
                elif file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    self._extract_js_dependencies(file_path, str(rel_path))

        print(f"✅ Indexed {len(self.index)} files")

        # Build dependency graph
        if self.graph_enabled:
            self._build_graph()

        return self.index
    
    def _categorize_file(self, rel_path: str) -> str:
        """Determine file category"""
        for category, patterns in self.categories.items():
            for pattern in patterns:
                if pattern in rel_path:
                    return category
        return "other"
    
    def _infer_purpose(self, filename: str, rel_path: str) -> str:
        """Infer what a file does based on name and location"""
        purposes = {
            "main.py": "FastAPI backend entry point",
            "screenshot_service.py": "Screenshot capture with Playwright + stealth",
            "document_service.py": "Word document generation",
            "quality_checker.py": "Screenshot quality validation",
            "logging_config.py": "Structured logging setup",
            "config.py": "Centralized configuration with Pydantic",
            "App.tsx": "Main React application UI",
            "main.tsx": "React entry point",
            "styles.css": "Application styles",
            "requirements.txt": "Python dependencies",
            "package.json": "Node.js dependencies",
            "auth_state.json": "Browser authentication state",
        }
        
        if filename in purposes:
            return purposes[filename]
        
        # Pattern-based inference
        if "test_" in filename:
            return f"Test script for {filename.replace('test_', '').replace('.py', '')}"
        if filename.endswith('.md'):
            return "Documentation"
        if "config" in filename.lower():
            return "Configuration file"
        
        return "Unknown purpose"
    
    def _extract_python_dependencies(self, file_path: Path, rel_path: str):
        """Extract imports from Python files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.dependencies[rel_path].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.dependencies[rel_path].add(node.module)
        except Exception as e:
            pass  # Skip files that can't be parsed
    
    def _extract_js_dependencies(self, file_path: Path, rel_path: str):
        """Extract imports from JS/TS files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Match import statements
            import_pattern = r'import\s+.*?\s+from\s+["\'](.+?)["\']'
            imports = re.findall(import_pattern, content)
            
            for imp in imports:
                self.dependencies[rel_path].add(imp)
        except Exception as e:
            pass
    
    def find_by_intent(self, intent: str) -> List[Dict]:
        """Find files based on what you want to do"""
        intent = intent.lower()
        results = []
        
        # Check intent map
        for key, patterns in self.intent_map.items():
            if intent in key or key in intent:
                for rel_path, info in self.index.items():
                    for pattern in patterns:
                        if pattern in rel_path or pattern in info['name']:
                            results.append({
                                "file": rel_path,
                                "purpose": info['purpose'],
                                "category": info['category'],
                                "match_reason": f"Matches intent '{key}'"
                            })
        
        # Deduplicate
        seen = set()
        unique_results = []
        for r in results:
            if r['file'] not in seen:
                seen.add(r['file'])
                unique_results.append(r)
        
        return unique_results
    
    def find_production_files(self) -> List[str]:
        """Get all production code files"""
        return [f for f, info in self.index.items() if info['category'] == 'production']
    
    def find_dependencies(self, file_path: str) -> Set[str]:
        """Find what a file depends on"""
        return self.dependencies.get(file_path, set())
    
    def find_dependents(self, module_name: str) -> List[str]:
        """Find what files depend on a module"""
        dependents = []
        for file, deps in self.dependencies.items():
            if module_name in deps:
                dependents.append(file)
        return dependents
    
    def search(self, query: str) -> List[Dict]:
        """Smart search across files"""
        query = query.lower()
        results = []
        
        for rel_path, info in self.index.items():
            score = 0
            reasons = []
            
            # Match filename
            if query in info['name'].lower():
                score += 10
                reasons.append("filename match")
            
            # Match path
            if query in rel_path.lower():
                score += 5
                reasons.append("path match")
            
            # Match purpose
            if query in info['purpose'].lower():
                score += 8
                reasons.append("purpose match")
            
            # Match category
            if query in info['category']:
                score += 3
                reasons.append("category match")
            
            if score > 0:
                results.append({
                    "file": rel_path,
                    "score": score,
                    "purpose": info['purpose'],
                    "category": info['category'],
                    "reasons": reasons
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _build_graph(self):
        """Build dependency graph from index"""
        if not self.graph_enabled:
            return

        print("📊 Building dependency graph...")

        # Add all files as nodes
        for rel_path, info in self.index.items():
            self.graph.add_node(
                rel_path,
                name=info['name'],
                category=info['category'],
                purpose=info['purpose'],
                size=info['size'],
                type=info['type']
            )

        # Add dependency edges
        for file_path, deps in self.dependencies.items():
            for dep in deps:
                # Try to find the actual file for this dependency
                dep_file = self._resolve_dependency(dep)
                if dep_file and dep_file in self.index:
                    self.graph.add_edge(file_path, dep_file, type='imports')

        print(f"📊 Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

    def _resolve_dependency(self, dep: str) -> Optional[str]:
        """Resolve a dependency name to an actual file path"""
        # Try direct match
        for rel_path in self.index.keys():
            if dep in rel_path:
                return rel_path

        # Try module name match
        dep_file = dep.replace('.', '/') + '.py'
        if dep_file in self.index:
            return dep_file

        # Try TypeScript/JavaScript
        for ext in ['.ts', '.tsx', '.js', '.jsx']:
            dep_file = dep.replace('.', '/') + ext
            if dep_file in self.index:
                return dep_file

        return None

    def graph_query_dependents(self, file_or_module: str) -> List[Dict]:
        """
        Graph-based query: Find all files that depend on this file/module
        Example: "Which modules depend on screenshot_service?"
        """
        if not self.graph_enabled:
            return []

        # Find the node
        target_node = None
        for node in self.graph.nodes():
            if file_or_module in node or node.endswith(file_or_module):
                target_node = node
                break

        if not target_node:
            return []

        # Find all predecessors (files that import this one)
        dependents = list(self.graph.predecessors(target_node))

        results = []
        for dep in dependents:
            info = self.index.get(dep, {})
            results.append({
                "file": dep,
                "purpose": info.get('purpose', 'Unknown'),
                "category": info.get('category', 'unknown'),
            })

        return results

    def graph_query_dependencies(self, file_path: str) -> List[Dict]:
        """
        Graph-based query: Find all files this file depends on
        """
        if not self.graph_enabled:
            return []

        # Find the node
        target_node = None
        for node in self.graph.nodes():
            if file_path in node or node.endswith(file_path):
                target_node = node
                break

        if not target_node:
            return []

        # Find all successors (files this one imports)
        dependencies = list(self.graph.successors(target_node))

        results = []
        for dep in dependencies:
            info = self.index.get(dep, {})
            results.append({
                "file": dep,
                "purpose": info.get('purpose', 'Unknown'),
                "category": info.get('category', 'unknown'),
            })

        return results

    def graph_query_impact(self, file_path: str, max_depth: int = 3) -> Dict:
        """
        Graph-based query: Find impact radius of changing this file
        Returns all files that would be affected (directly or indirectly)
        """
        if not self.graph_enabled:
            return {"direct": [], "indirect": [], "total_impact": 0}

        # Find the node
        target_node = None
        for node in self.graph.nodes():
            if file_path in node or node.endswith(file_path):
                target_node = node
                break

        if not target_node:
            return {"direct": [], "indirect": [], "total_impact": 0}

        # Direct dependents (depth 1)
        direct = list(self.graph.predecessors(target_node))

        # Indirect dependents (depth 2+)
        indirect = set()
        for depth in range(2, max_depth + 1):
            for node in list(direct) + list(indirect):
                predecessors = self.graph.predecessors(node)
                for pred in predecessors:
                    if pred != target_node and pred not in direct:
                        indirect.add(pred)

        return {
            "direct": [{"file": f, "purpose": self.index.get(f, {}).get('purpose', 'Unknown')} for f in direct],
            "indirect": [{"file": f, "purpose": self.index.get(f, {}).get('purpose', 'Unknown')} for f in indirect],
            "total_impact": len(direct) + len(indirect)
        }

    def graph_query_circular_deps(self) -> List[List[str]]:
        """
        Graph-based query: Find circular dependencies
        Returns list of cycles
        """
        if not self.graph_enabled:
            return []

        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except Exception:
            return []

    def graph_query_orphans(self) -> List[Dict]:
        """
        Graph-based query: Find orphaned files (no dependencies, no dependents)
        """
        if not self.graph_enabled:
            return []

        orphans = []
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)

            if in_degree == 0 and out_degree == 0:
                info = self.index.get(node, {})
                orphans.append({
                    "file": node,
                    "purpose": info.get('purpose', 'Unknown'),
                    "category": info.get('category', 'unknown'),
                })

        return orphans

    def health_check(self) -> Dict:
        """
        Comprehensive dependency health check
        Returns issues found in the project
        """
        issues = {
            "circular_dependencies": [],
            "orphaned_files": [],
            "large_files": [],
            "unused_imports": [],
            "missing_dependencies": [],
            "total_issues": 0,
        }

        # Check for circular dependencies
        if self.graph_enabled:
            issues["circular_dependencies"] = self.graph_query_circular_deps()
            issues["orphaned_files"] = self.graph_query_orphans()

        # Check for large files (>100KB)
        for rel_path, info in self.index.items():
            if info['size'] > 100_000:
                issues["large_files"].append({
                    "file": rel_path,
                    "size": info['size'],
                    "size_kb": info['size'] // 1024,
                })

        # Check for missing dependencies (imports that don't resolve)
        for file_path, deps in self.dependencies.items():
            for dep in deps:
                # Skip standard library and external packages
                if dep in ['os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing',
                          'asyncio', 'logging', 'collections', 're', 'hashlib']:
                    continue
                if dep.startswith(('fastapi', 'playwright', 'openai', 'networkx', 'watchdog')):
                    continue

                # Check if dependency resolves to a file
                resolved = self._resolve_dependency(dep)
                if not resolved:
                    issues["missing_dependencies"].append({
                        "file": file_path,
                        "missing_import": dep,
                    })

        # Calculate total issues
        issues["total_issues"] = (
            len(issues["circular_dependencies"]) +
            len(issues["orphaned_files"]) +
            len(issues["large_files"]) +
            len(issues["missing_dependencies"])
        )

        return issues

    def ask_ai(self, query: str) -> str:
        """
        Use OpenAI to answer semantic questions about the project
        Example: "Where is the code that handles screenshot capture?"
        """
        if not self.openai_enabled:
            return "❌ OpenAI integration not enabled. Provide API key when initializing ProjectBrain."

        # Build context from index (limit to top 40 files to stay within token limits)
        context_files = []
        for rel_path, info in list(self.index.items())[:40]:
            context_files.append(f"{rel_path}:\n{info['preview']}\n")

        context = "\n".join(context_files)

        prompt = f"""You are an intelligent project file locator for a screenshot automation tool.

Project Context (file previews):
{context}

User Question: "{query}"

Provide:
1. The most relevant file path(s)
2. Brief reasoning why
3. What the file does

Be concise and specific."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500,
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"❌ OpenAI API error: {e}"

    def save_index(self, output_file: str = "project_index.json"):
        """Save index to file"""
        data = {
            "index": self.index,
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "file_hashes": self.file_hashes,
            "generated": datetime.now().isoformat(),
        }

        with open(self.root / output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Saved index to {output_file}")
    
    def print_summary(self):
        """Print project summary"""
        print("\n" + "="*60)
        print("📊 PROJECT BRAIN SUMMARY")
        print("="*60)
        
        # Count by category
        categories = defaultdict(int)
        for info in self.index.values():
            categories[info['category']] += 1
        
        print("\n📁 Files by Category:")
        for cat, count in sorted(categories.items()):
            print(f"   {cat:15} {count:3} files")
        
        print(f"\n📦 Total Files: {len(self.index)}")
        print(f"🔗 Dependencies Tracked: {len(self.dependencies)}")
        
        print("\n🎯 Production Files:")
        for f in self.find_production_files()[:10]:
            print(f"   ✅ {f}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Initialize and scan
    brain = ProjectBrain("/Users/tlreddy/Documents/project 1/screenshot-app")
    brain.scan_project()
    brain.save_index()
    brain.print_summary()
    
    # Example queries
    print("\n🔍 Example: Find screenshot-related files")
    results = brain.find_by_intent("screenshot")
    for r in results[:5]:
        print(f"   📄 {r['file']}")
        print(f"      Purpose: {r['purpose']}")
    
    print("\n🔍 Example: Search for 'config'")
    results = brain.search("config")
    for r in results[:5]:
        print(f"   📄 {r['file']} (score: {r['score']})")
        print(f"      {r['purpose']}")

