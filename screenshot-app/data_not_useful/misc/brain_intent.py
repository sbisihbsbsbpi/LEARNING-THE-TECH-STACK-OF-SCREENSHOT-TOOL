#!/usr/bin/env python3
"""
Project Brain Intent Engine
Understands developer purpose and serves the most relevant code areas
"""

import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib

# Optional: OpenAI for embeddings
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

# Optional: NumPy for vector operations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class IntentEngine:
    """
    Intent Engine - Understands developer purpose and finds relevant code
    
    Layers:
    1. Intent Understanding - Maps natural language to semantic vectors
    2. Code Hotspot Mapping - Indexed graph of files↔functions↔commits
    3. Insight Layer - Highlights issues, commits, patterns
    """
    
    def __init__(self, project_root: str, openai_api_key: Optional[str] = None):
        self.root = Path(project_root)
        self.openai_api_key = openai_api_key
        self.openai_enabled = OPENAI_AVAILABLE and openai_api_key
        
        if self.openai_enabled:
            openai.api_key = openai_api_key
        
        # Intent categories and keywords
        self.intent_categories = {
            'performance': ['slow', 'lag', 'optimize', 'speed', 'performance', 'fast', 'cache', 'async'],
            'bug': ['fix', 'bug', 'error', 'crash', 'issue', 'broken', 'fail', 'exception'],
            'feature': ['add', 'implement', 'create', 'new', 'feature', 'support', 'enable'],
            'refactor': ['refactor', 'clean', 'improve', 'restructure', 'organize', 'simplify'],
            'security': ['security', 'auth', 'login', 'permission', 'vulnerability', 'encrypt'],
            'ui': ['ui', 'interface', 'design', 'layout', 'style', 'component', 'visual'],
            'api': ['api', 'endpoint', 'route', 'request', 'response', 'integration'],
            'database': ['database', 'db', 'query', 'sql', 'schema', 'migration', 'data'],
            'test': ['test', 'testing', 'spec', 'coverage', 'unit', 'integration'],
        }
        
        # Domain keywords
        self.domain_keywords = {
            'authentication': ['login', 'auth', 'user', 'password', 'token', 'session', 'oauth'],
            'payment': ['payment', 'pay', 'checkout', 'stripe', 'paypal', 'apple pay', 'transaction'],
            'screenshot': ['screenshot', 'capture', 'image', 'browser', 'playwright', 'stealth'],
            'config': ['config', 'settings', 'environment', 'env', 'configuration'],
            'api': ['api', 'endpoint', 'route', 'fastapi', 'rest', 'graphql'],
            'frontend': ['react', 'component', 'ui', 'tsx', 'jsx', 'frontend', 'tauri'],
            'backend': ['backend', 'server', 'service', 'controller', 'model'],
        }
        
        # Code hotspot graph
        self.hotspots = {
            'files': {},        # file_path -> metadata
            'functions': {},    # function_name -> metadata
            'commits': {},      # commit_hash -> metadata
            'issues': {},       # issue_id -> metadata
        }
        
        # Embeddings cache
        self.embeddings_cache = {}
        self.load_embeddings_cache()
    
    def load_embeddings_cache(self):
        """Load cached embeddings"""
        cache_file = self.root / ".brain_embeddings.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.embeddings_cache = json.load(f)
    
    def save_embeddings_cache(self):
        """Save embeddings cache"""
        cache_file = self.root / ".brain_embeddings.json"
        with open(cache_file, 'w') as f:
            json.dump(self.embeddings_cache, f, indent=2)
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text (with caching)"""
        if not self.openai_enabled:
            return None
        
        # Check cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]
        
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",  # Faster and cheaper
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache it
            self.embeddings_cache[text_hash] = embedding
            self.save_embeddings_cache()
            
            return embedding
        except Exception as e:
            print(f"⚠️  Embedding error: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not NUMPY_AVAILABLE:
            # Fallback: simple dot product
            return sum(a * b for a, b in zip(vec1, vec2))
        
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def classify_intent(self, intent: str) -> Dict:
        """
        Classify intent into categories and domains
        Returns: {category: score, domain: score}
        """
        intent_lower = intent.lower()
        
        # Category scoring
        category_scores = {}
        for category, keywords in self.intent_categories.items():
            score = sum(1 for kw in keywords if kw in intent_lower)
            if score > 0:
                category_scores[category] = score
        
        # Domain scoring
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in intent_lower)
            if score > 0:
                domain_scores[domain] = score
        
        return {
            'categories': category_scores,
            'domains': domain_scores,
            'primary_category': max(category_scores.items(), key=lambda x: x[1])[0] if category_scores else 'general',
            'primary_domain': max(domain_scores.items(), key=lambda x: x[1])[0] if domain_scores else 'general',
        }
    
    def build_hotspot_graph(self, brain_index: Dict):
        """
        Build code hotspot graph from project brain index
        """
        print("🔥 Building code hotspot graph...")
        
        # Index files
        for file_path, info in brain_index.items():
            self.hotspots['files'][file_path] = {
                'path': file_path,
                'name': info['name'],
                'category': info['category'],
                'purpose': info['purpose'],
                'size': info['size'],
                'preview': info.get('preview', ''),
                'embedding': None,  # Will be computed on demand
            }
        
        # Extract functions from Python files
        for file_path, info in brain_index.items():
            if file_path.endswith('.py'):
                functions = self._extract_python_functions(self.root / file_path)
                for func_name, func_info in functions.items():
                    full_name = f"{file_path}::{func_name}"
                    self.hotspots['functions'][full_name] = {
                        'name': func_name,
                        'file': file_path,
                        'line': func_info['line'],
                        'signature': func_info['signature'],
                        'docstring': func_info.get('docstring', ''),
                        'embedding': None,
                    }
        
        # Index recent commits
        commits = self._get_recent_commits(days=30)
        for commit in commits:
            self.hotspots['commits'][commit['hash']] = commit
        
        print(f"✅ Indexed {len(self.hotspots['files'])} files")
        print(f"✅ Indexed {len(self.hotspots['functions'])} functions")
        print(f"✅ Indexed {len(self.hotspots['commits'])} commits")
    
    def _extract_python_functions(self, file_path: Path) -> Dict:
        """Extract function definitions from Python file"""
        functions = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based extraction
            pattern = r'^\s*(async\s+)?def\s+(\w+)\s*\((.*?)\):'
            for i, line in enumerate(content.split('\n'), 1):
                match = re.match(pattern, line)
                if match:
                    is_async = match.group(1) is not None
                    func_name = match.group(2)
                    params = match.group(3)
                    
                    # Extract docstring (simple approach)
                    docstring = ""
                    lines = content.split('\n')
                    if i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.startswith('"""') or next_line.startswith("'''"):
                            docstring = next_line.strip('"""').strip("'''")
                    
                    functions[func_name] = {
                        'line': i,
                        'signature': f"{'async ' if is_async else ''}def {func_name}({params})",
                        'docstring': docstring,
                        'is_async': is_async,
                    }
        except Exception:
            pass
        
        return functions
    
    def _get_recent_commits(self, days: int = 30) -> List[Dict]:
        """Get recent git commits"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            cmd = f'git log --since="{since_date}" --pretty=format:"%H|%an|%ad|%s" --date=iso --name-only'
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
            current_commit = None
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    if current_commit:
                        commits.append(current_commit)
                        current_commit = None
                    continue
                
                if '|' in line:
                    # Commit header
                    parts = line.split('|')
                    if len(parts) >= 4:
                        current_commit = {
                            'hash': parts[0][:8],
                            'author': parts[1],
                            'date': parts[2],
                            'message': parts[3],
                            'files': [],
                        }
                else:
                    # File name
                    if current_commit:
                        current_commit['files'].append(line.strip())
            
            if current_commit:
                commits.append(current_commit)
            
            return commits
        except Exception:
            return []
    
    def find_hotspots(self, intent: str, top_k: int = 10) -> Dict:
        """
        Find code hotspots relevant to the intent
        
        Returns:
        {
            'intent_analysis': {...},
            'file_matches': [...],
            'function_matches': [...],
            'commit_matches': [...],
            'insights': [...]
        }
        """
        print(f"\n🎯 Analyzing intent: '{intent}'")
        
        # Step 1: Classify intent
        classification = self.classify_intent(intent)
        print(f"📊 Category: {classification['primary_category']}")
        print(f"📊 Domain: {classification['primary_domain']}")
        
        # Step 2: Keyword-based matching (fast)
        file_matches = self._keyword_match_files(intent, classification)
        function_matches = self._keyword_match_functions(intent, classification)
        commit_matches = self._keyword_match_commits(intent, classification)
        
        # Step 3: Semantic matching (if OpenAI available)
        if self.openai_enabled:
            print("🤖 Computing semantic similarity...")
            intent_embedding = self.get_embedding(intent)
            if intent_embedding:
                file_matches = self._semantic_rank(file_matches, intent_embedding, 'files')
                function_matches = self._semantic_rank(function_matches, intent_embedding, 'functions')
        
        # Step 4: Generate insights
        insights = self._generate_insights(intent, classification, file_matches, function_matches, commit_matches)
        
        return {
            'intent': intent,
            'intent_analysis': classification,
            'file_matches': file_matches[:top_k],
            'function_matches': function_matches[:top_k],
            'commit_matches': commit_matches[:top_k],
            'insights': insights,
        }
    
    def _keyword_match_files(self, intent: str, classification: Dict) -> List[Dict]:
        """Match files using keywords"""
        matches = []
        intent_lower = intent.lower()
        
        for file_path, info in self.hotspots['files'].items():
            score = 0
            reasons = []
            
            # Match in file name
            if any(word in info['name'].lower() for word in intent_lower.split()):
                score += 3
                reasons.append("filename match")
            
            # Match in purpose
            if any(word in info['purpose'].lower() for word in intent_lower.split()):
                score += 2
                reasons.append("purpose match")
            
            # Match category
            if classification['primary_category'] in info['category']:
                score += 1
                reasons.append(f"{classification['primary_category']} category")
            
            # Match domain
            domain = classification['primary_domain']
            if domain in info['purpose'].lower() or domain in info['name'].lower():
                score += 2
                reasons.append(f"{domain} domain")
            
            if score > 0:
                matches.append({
                    'file': file_path,
                    'score': score,
                    'reasons': reasons,
                    'info': info,
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
    
    def _keyword_match_functions(self, intent: str, classification: Dict) -> List[Dict]:
        """Match functions using keywords"""
        matches = []
        intent_lower = intent.lower()
        
        for func_full_name, info in self.hotspots['functions'].items():
            score = 0
            reasons = []
            
            # Match in function name
            if any(word in info['name'].lower() for word in intent_lower.split()):
                score += 3
                reasons.append("function name match")
            
            # Match in docstring
            if info['docstring'] and any(word in info['docstring'].lower() for word in intent_lower.split()):
                score += 2
                reasons.append("docstring match")
            
            # Async functions for performance intents
            if classification['primary_category'] == 'performance' and info.get('is_async'):
                score += 1
                reasons.append("async function (performance relevant)")
            
            if score > 0:
                matches.append({
                    'function': func_full_name,
                    'score': score,
                    'reasons': reasons,
                    'info': info,
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
    
    def _keyword_match_commits(self, intent: str, classification: Dict) -> List[Dict]:
        """Match commits using keywords"""
        matches = []
        intent_lower = intent.lower()
        
        for commit_hash, info in self.hotspots['commits'].items():
            score = 0
            reasons = []
            
            # Match in commit message
            if any(word in info['message'].lower() for word in intent_lower.split()):
                score += 3
                reasons.append("commit message match")
            
            # Match category keywords in message
            category = classification['primary_category']
            category_keywords = self.intent_categories.get(category, [])
            if any(kw in info['message'].lower() for kw in category_keywords):
                score += 2
                reasons.append(f"{category} related")
            
            if score > 0:
                matches.append({
                    'commit': commit_hash,
                    'score': score,
                    'reasons': reasons,
                    'info': info,
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
    
    def _semantic_rank(self, matches: List[Dict], intent_embedding: List[float], hotspot_type: str) -> List[Dict]:
        """Re-rank matches using semantic similarity"""
        for match in matches:
            # Get or compute embedding for this item
            item_key = match.get('file') or match.get('function') or match.get('commit')
            item_info = match['info']
            
            # Create text representation
            if hotspot_type == 'files':
                text = f"{item_info['name']} {item_info['purpose']} {item_info.get('preview', '')[:200]}"
            elif hotspot_type == 'functions':
                text = f"{item_info['name']} {item_info['signature']} {item_info.get('docstring', '')}"
            else:
                text = item_info.get('message', '')
            
            # Get embedding
            embedding = self.get_embedding(text)
            if embedding:
                similarity = self.cosine_similarity(intent_embedding, embedding)
                match['semantic_score'] = similarity
                match['score'] += similarity * 5  # Weight semantic similarity
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
    
    def _generate_insights(self, intent: str, classification: Dict, file_matches: List, function_matches: List, commit_matches: List) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # Performance insights
        if classification['primary_category'] == 'performance':
            async_funcs = [f for f in function_matches if f['info'].get('is_async')]
            if async_funcs:
                insights.append(f"🔍 Found {len(async_funcs)} async functions - check for await bottlenecks")
        
        # Recent changes
        if commit_matches:
            recent = commit_matches[0]
            insights.append(f"📝 Most recent related commit: {recent['info']['message']} ({recent['info']['date'][:10]})")
        
        # File hotspots
        if file_matches:
            top_file = file_matches[0]
            insights.append(f"🎯 Primary hotspot: {top_file['file']} - {top_file['info']['purpose']}")
        
        # Function suggestions
        if function_matches:
            top_func = function_matches[0]
            insights.append(f"⚡ Check function: {top_func['function']} at line {top_func['info']['line']}")
        
        return insights


def main():
    """CLI for intent engine"""
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python3 brain_intent.py <intent>")
        print('Example: python3 brain_intent.py "fix login lag"')
        return
    
    intent = ' '.join(sys.argv[1:])
    
    # Initialize
    project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    engine = IntentEngine(project_path, openai_api_key)
    
    # Load brain index
    from project_brain import ProjectBrain
    brain = ProjectBrain(project_path, openai_api_key)
    
    index_file = brain.root / "project_index.json"
    if index_file.exists():
        with open(index_file) as f:
            data = json.load(f)
            brain.index = data['index']
    
    # Build hotspot graph
    engine.build_hotspot_graph(brain.index)
    
    # Find hotspots
    results = engine.find_hotspots(intent)
    
    # Print results
    print("\n" + "=" * 70)
    print("🎯 INTENT ENGINE RESULTS")
    print("=" * 70)
    
    print(f"\n💡 Insights:")
    for insight in results['insights']:
        print(f"   {insight}")
    
    print(f"\n📄 Top File Matches:")
    for match in results['file_matches'][:5]:
        print(f"   {match['file']} (score: {match['score']:.1f})")
        print(f"      └─ {', '.join(match['reasons'])}")
    
    print(f"\n⚡ Top Function Matches:")
    for match in results['function_matches'][:5]:
        print(f"   {match['function']} (score: {match['score']:.1f})")
        print(f"      └─ {match['info']['signature']}")
    
    print(f"\n📝 Related Commits:")
    for match in results['commit_matches'][:5]:
        print(f"   {match['commit']} - {match['info']['message']}")
        print(f"      └─ {match['info']['date'][:10]}")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

