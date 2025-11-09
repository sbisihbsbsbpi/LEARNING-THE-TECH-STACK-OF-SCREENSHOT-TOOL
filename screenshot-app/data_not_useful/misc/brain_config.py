#!/usr/bin/env python3
"""
Project Brain Smart Config Finder
Self-learning configuration discovery engine
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
import hashlib


class SmartConfigFinder:
    """
    Smart Config Finder - Self-learning configuration discovery engine
    
    Features:
    1. Config Topology Learning - Maps all config patterns
    2. Multi-Language Parsing - .env, .yml, .json, .ts, .py, .js
    3. Semantic Search - Understands variants (PAYMENT_URL, paymentUrl, payment_url)
    4. Shadow Config Detection - Finds duplicates and conflicts
    5. Natural Language Queries - "Where is paymentGatewayUrl set?"
    """
    
    def __init__(self, project_root: str, openai_api_key: Optional[str] = None):
        self.root = Path(project_root)
        self.openai_api_key = openai_api_key
        
        # Check OpenAI availability
        self.openai_enabled = False
        if openai_api_key:
            try:
                import openai
                openai.api_key = openai_api_key
                self.openai_enabled = True
            except ImportError:
                pass
        
        # Config topology
        self.config_map = {}  # key -> [{file, line, value, type, context}]
        
        # Config file patterns
        self.config_patterns = {
            'env': ['.env', '.env.local', '.env.development', '.env.production', '.env.test'],
            'yaml': ['*.yml', '*.yaml', 'config/*.yml', 'config/*.yaml'],
            'json': ['*.json', 'config/*.json', 'settings/*.json'],
            'python': ['config.py', 'settings.py', 'constants.py', '**/config.py', '**/settings.py'],
            'typescript': ['config.ts', 'settings.ts', 'constants.ts', '**/config.ts'],
            'javascript': ['config.js', 'settings.js', 'constants.js', '**/config.js'],
        }
        
        # Embeddings cache
        self.embeddings_cache = {}
        self.load_embeddings_cache()
    
    def load_embeddings_cache(self):
        """Load embeddings cache from disk"""
        cache_file = self.root / ".brain_config_embeddings.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.embeddings_cache = json.load(f)
            except Exception:
                pass
    
    def save_embeddings_cache(self):
        """Save embeddings cache to disk"""
        cache_file = self.root / ".brain_config_embeddings.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.embeddings_cache, f)
        except Exception:
            pass
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text (with caching)"""
        if not self.openai_enabled:
            return None
        
        # Check cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]
        
        try:
            import openai
            response = openai.embeddings.create(
                model="text-embedding-3-small",
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
        try:
            import numpy as np
            return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        except ImportError:
            # Fallback without numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0.0
    
    def is_config_file(self, file_path: Path) -> bool:
        """Check if file is a config file"""
        name = file_path.name.lower()
        
        # Check exact matches
        if name in ['.env', '.env.local', '.env.development', '.env.production', '.env.test']:
            return True
        
        # Check patterns
        if name.endswith(('.yml', '.yaml', '.json')):
            return True
        
        if name in ['config.py', 'settings.py', 'constants.py', 'config.ts', 'settings.ts', 'constants.ts', 'config.js', 'settings.js', 'constants.js']:
            return True
        
        # Check if in config directory
        if 'config' in str(file_path).lower() or 'settings' in str(file_path).lower():
            return True
        
        return False
    
    def parse_env_file(self, file_path: Path) -> List[Dict]:
        """Parse .env file"""
        configs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE
                    match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)
                    if match:
                        key, value = match.groups()
                        configs.append({
                            'key': key,
                            'value': value.strip('"\''),
                            'file': str(file_path.relative_to(self.root)),
                            'line': line_num,
                            'type': 'env',
                            'context': line,
                        })
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
        
        return configs
    
    def parse_yaml_file(self, file_path: Path) -> List[Dict]:
        """Parse YAML file"""
        configs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                return configs
            
            # Flatten nested dict
            def flatten(d, parent_key='', sep='.'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            flat_data = flatten(data)
            
            for key, value in flat_data.items():
                configs.append({
                    'key': key,
                    'value': str(value),
                    'file': str(file_path.relative_to(self.root)),
                    'line': 0,  # YAML doesn't preserve line numbers easily
                    'type': 'yaml',
                    'context': f"{key}: {value}",
                })
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
        
        return configs
    
    def parse_json_file(self, file_path: Path) -> List[Dict]:
        """Parse JSON file"""
        configs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                return configs
            
            # Flatten nested dict
            def flatten(d, parent_key='', sep='.'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            flat_data = flatten(data)
            
            for key, value in flat_data.items():
                configs.append({
                    'key': key,
                    'value': str(value),
                    'file': str(file_path.relative_to(self.root)),
                    'line': 0,
                    'type': 'json',
                    'context': f'"{key}": {json.dumps(value)}',
                })
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
        
        return configs
    
    def parse_python_file(self, file_path: Path) -> List[Dict]:
        """Parse Python config file for constants"""
        configs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find constants (UPPERCASE = value)
            pattern = r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.+)$'
            
            for line_num, line in enumerate(content.split('\n'), 1):
                match = re.match(pattern, line.strip())
                if match:
                    key, value = match.groups()
                    
                    # Clean value
                    value = value.strip()
                    if value.endswith(','):
                        value = value[:-1]
                    
                    configs.append({
                        'key': key,
                        'value': value,
                        'file': str(file_path.relative_to(self.root)),
                        'line': line_num,
                        'type': 'python_const',
                        'context': line.strip(),
                    })
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
        
        return configs
    
    def parse_typescript_file(self, file_path: Path) -> List[Dict]:
        """Parse TypeScript/JavaScript config file for constants"""
        configs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find constants
            # const PAYMENT_URL = "..."
            # export const PAYMENT_URL = "..."
            pattern = r'(?:export\s+)?const\s+([A-Z_][A-Z0-9_]*)\s*[:=]\s*(.+?)(?:;|$)'
            
            for line_num, line in enumerate(content.split('\n'), 1):
                match = re.search(pattern, line)
                if match:
                    key, value = match.groups()
                    
                    # Clean value
                    value = value.strip()
                    if value.endswith(','):
                        value = value[:-1]
                    
                    configs.append({
                        'key': key,
                        'value': value,
                        'file': str(file_path.relative_to(self.root)),
                        'line': line_num,
                        'type': 'ts_const',
                        'context': line.strip(),
                    })
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
        
        return configs
    
    def learn_config_topology(self):
        """Scan codebase and learn configuration topology"""
        print("🧭 Learning configuration topology...")
        
        self.config_map = defaultdict(list)
        
        # Scan all files
        for file_path in self.root.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip hidden directories and common excludes
            if any(part.startswith('.') for part in file_path.parts):
                if not file_path.name.startswith('.env'):
                    continue
            
            if any(exclude in str(file_path) for exclude in ['node_modules', '__pycache__', 'venv', 'dist', 'build']):
                continue
            
            # Check if config file
            if not self.is_config_file(file_path):
                continue
            
            # Parse based on type
            configs = []
            
            if file_path.name.startswith('.env'):
                configs = self.parse_env_file(file_path)
            elif file_path.suffix in ['.yml', '.yaml']:
                configs = self.parse_yaml_file(file_path)
            elif file_path.suffix == '.json':
                configs = self.parse_json_file(file_path)
            elif file_path.suffix == '.py':
                configs = self.parse_python_file(file_path)
            elif file_path.suffix in ['.ts', '.js']:
                configs = self.parse_typescript_file(file_path)
            
            # Add to map
            for config in configs:
                self.config_map[config['key']].append(config)
        
        print(f"✅ Learned {len(self.config_map)} unique config keys from {sum(len(v) for v in self.config_map.values())} total entries")
    
    def normalize_key(self, key: str) -> str:
        """Normalize config key for matching"""
        # Convert to lowercase
        # Remove underscores and hyphens
        return re.sub(r'[_-]', '', key.lower())
    
    def find_config(self, query: str, use_semantic: bool = True) -> List[Dict]:
        """
        Find config by query
        
        Supports:
        - Exact match
        - Case-insensitive match
        - Variant match (PAYMENT_URL, paymentUrl, payment_url)
        - Semantic match (with OpenAI)
        """
        results = []
        
        # Normalize query
        normalized_query = self.normalize_key(query)
        
        # Exact and variant matching
        for key, configs in self.config_map.items():
            normalized_key = self.normalize_key(key)
            
            # Exact match
            if key == query:
                for config in configs:
                    results.append({
                        'config': config,
                        'match_type': 'exact',
                        'score': 10.0,
                    })
            # Case-insensitive match
            elif key.lower() == query.lower():
                for config in configs:
                    results.append({
                        'config': config,
                        'match_type': 'case_insensitive',
                        'score': 9.0,
                    })
            # Variant match (normalized)
            elif normalized_key == normalized_query:
                for config in configs:
                    results.append({
                        'config': config,
                        'match_type': 'variant',
                        'score': 8.0,
                    })
            # Partial match
            elif normalized_query in normalized_key or normalized_key in normalized_query:
                for config in configs:
                    results.append({
                        'config': config,
                        'match_type': 'partial',
                        'score': 5.0,
                    })
        
        # Semantic matching (if enabled)
        if use_semantic and self.openai_enabled and not results:
            print("🤖 Using semantic search...")
            query_embedding = self.get_embedding(query)
            
            if query_embedding:
                for key, configs in self.config_map.items():
                    key_embedding = self.get_embedding(key)
                    if key_embedding:
                        similarity = self.cosine_similarity(query_embedding, key_embedding)
                        if similarity > 0.7:  # Threshold
                            for config in configs:
                                results.append({
                                    'config': config,
                                    'match_type': 'semantic',
                                    'score': similarity * 10,
                                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def detect_shadow_configs(self) -> Dict:
        """
        Detect shadow configs - duplicates and conflicts

        Returns:
        {
            'duplicates': [...],  # Same key, same value, different files
            'conflicts': [...],   # Same key, different values
        }
        """
        duplicates = []
        conflicts = []

        for key, configs in self.config_map.items():
            if len(configs) < 2:
                continue

            # Group by value
            value_groups = defaultdict(list)
            for config in configs:
                value_groups[config['value']].append(config)

            # Check for duplicates (same value, multiple files)
            for value, group in value_groups.items():
                if len(group) > 1:
                    duplicates.append({
                        'key': key,
                        'value': value,
                        'locations': group,
                    })

            # Check for conflicts (different values)
            if len(value_groups) > 1:
                conflicts.append({
                    'key': key,
                    'values': list(value_groups.keys()),
                    'locations': configs,
                })

        return {
            'duplicates': duplicates,
            'conflicts': conflicts,
        }

    def get_all_keys(self) -> List[str]:
        """Get all config keys"""
        return sorted(self.config_map.keys())

    def get_stats(self) -> Dict:
        """Get config statistics"""
        total_keys = len(self.config_map)
        total_entries = sum(len(v) for v in self.config_map.values())

        # Count by type
        type_counts = defaultdict(int)
        for configs in self.config_map.values():
            for config in configs:
                type_counts[config['type']] += 1

        # Count by file
        file_counts = defaultdict(int)
        for configs in self.config_map.values():
            for config in configs:
                file_counts[config['file']] += 1

        return {
            'total_keys': total_keys,
            'total_entries': total_entries,
            'by_type': dict(type_counts),
            'by_file': dict(sorted(file_counts.items(), key=lambda x: x[1], reverse=True)),
        }


def main():
    """CLI for smart config finder"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 brain_config.py <config_key>")
        print('Example: python3 brain_config.py paymentGatewayUrl')
        return
    
    query = sys.argv[1]
    
    # Initialize
    import os
    project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    finder = SmartConfigFinder(project_path, openai_api_key)
    
    # Learn topology
    finder.learn_config_topology()
    
    # Find config
    results = finder.find_config(query)
    
    # Print results
    print("\n" + "=" * 70)
    print(f"🧭 SMART CONFIG FINDER")
    print("=" * 70)
    print(f"\nQuery: {query}")
    
    if not results:
        print("\n❌ No matches found")
    else:
        print(f"\n✅ Found {len(results)} match(es):\n")
        
        for i, result in enumerate(results[:10], 1):
            config = result['config']
            match_type = result['match_type']
            score = result['score']
            
            print(f"{i}. {config['file']}")
            print(f"   Key: {config['key']}")
            print(f"   Value: {config['value']}")
            print(f"   Type: {config['type']}")
            if config['line'] > 0:
                print(f"   Line: {config['line']}")
            print(f"   Match: {match_type} (score: {score:.1f})")
            print(f"   Context: {config['context']}")
            print()
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

