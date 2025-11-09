#!/usr/bin/env python3
"""
Project Brain AI-Based Error Context Reconstructor
Diagnostic AI that remembers how errors were fixed before
"""

import json
import re
import sqlite3
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


class ErrorContextReconstructor:
    """
    AI-Based Error Context Reconstructor
    
    Features:
    1. Error Signature Capture - Stack traces, messages, environment
    2. Context Reconstruction - Git history, tests, past errors
    3. Intelligent Recall - Vector similarity search for past errors
    4. Fix Suggestions - Ranked by similarity, recency, frequency
    5. Learning Memory - Stores all errors and their fixes
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
        
        # Initialize database
        self.db_path = self.root / ".brain_errors.db"
        self.init_database()
        
        # Embeddings cache
        self.embeddings_cache = {}
        self.load_embeddings_cache()
    
    def init_database(self):
        """Initialize SQLite database for error storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Errors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature TEXT NOT NULL,
                error_type TEXT,
                error_message TEXT,
                stack_trace TEXT,
                file_path TEXT,
                line_number INTEGER,
                function_name TEXT,
                environment TEXT,
                timestamp TEXT,
                embedding_hash TEXT,
                UNIQUE(signature)
            )
        """)
        
        # Fixes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fixes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_id INTEGER,
                commit_hash TEXT,
                commit_message TEXT,
                commit_date TEXT,
                diff_summary TEXT,
                fix_description TEXT,
                confirmed BOOLEAN DEFAULT 0,
                FOREIGN KEY(error_id) REFERENCES errors(id)
            )
        """)
        
        # Error occurrences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS occurrences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_id INTEGER,
                timestamp TEXT,
                environment TEXT,
                context TEXT,
                FOREIGN KEY(error_id) REFERENCES errors(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def load_embeddings_cache(self):
        """Load embeddings cache from disk"""
        cache_file = self.root / ".brain_error_embeddings.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.embeddings_cache = json.load(f)
            except Exception:
                pass
    
    def save_embeddings_cache(self):
        """Save embeddings cache to disk"""
        cache_file = self.root / ".brain_error_embeddings.json"
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
                model="text-embedding-3-large",
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
    
    def parse_error(self, error_text: str, environment: str = "unknown") -> Dict:
        """
        Parse error text and extract signature
        
        Supports:
        - Python tracebacks
        - JavaScript errors
        - TypeScript errors
        - Generic error messages
        """
        error_info = {
            'error_type': None,
            'error_message': None,
            'stack_trace': error_text,
            'file_path': None,
            'line_number': None,
            'function_name': None,
            'environment': environment,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Python traceback
        python_match = re.search(r'File "([^"]+)", line (\d+), in (\w+)', error_text)
        if python_match:
            error_info['file_path'] = python_match.group(1)
            error_info['line_number'] = int(python_match.group(2))
            error_info['function_name'] = python_match.group(3)
        
        # Python error type
        python_error = re.search(r'(\w+Error): (.+)', error_text)
        if python_error:
            error_info['error_type'] = python_error.group(1)
            error_info['error_message'] = python_error.group(2)
        
        # JavaScript/TypeScript error
        js_match = re.search(r'at (\w+) \(([^:]+):(\d+):\d+\)', error_text)
        if js_match:
            error_info['function_name'] = js_match.group(1)
            error_info['file_path'] = js_match.group(2)
            error_info['line_number'] = int(js_match.group(3))
        
        # JavaScript error type
        js_error = re.search(r'(Error|TypeError|ReferenceError|SyntaxError): (.+)', error_text)
        if js_error:
            error_info['error_type'] = js_error.group(1)
            error_info['error_message'] = js_error.group(2)
        
        # Generic error message (first line)
        if not error_info['error_message']:
            first_line = error_text.split('\n')[0].strip()
            if first_line:
                error_info['error_message'] = first_line
        
        # Create signature
        signature_parts = []
        if error_info['error_type']:
            signature_parts.append(error_info['error_type'])
        if error_info['file_path']:
            # Normalize file path (relative to project root)
            try:
                rel_path = str(Path(error_info['file_path']).relative_to(self.root))
                error_info['file_path'] = rel_path
                signature_parts.append(rel_path)
            except ValueError:
                signature_parts.append(error_info['file_path'])
        if error_info['function_name']:
            signature_parts.append(error_info['function_name'])
        if error_info['error_message']:
            # Normalize error message (remove dynamic parts like numbers, paths)
            normalized_msg = re.sub(r'\d+', 'N', error_info['error_message'])
            normalized_msg = re.sub(r'/[^\s]+', '/PATH', normalized_msg)
            signature_parts.append(normalized_msg[:100])
        
        error_info['signature'] = '::'.join(signature_parts)
        
        return error_info
    
    def store_error(self, error_info: Dict) -> int:
        """Store error in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create embedding
        embedding_text = f"{error_info['error_type']} {error_info['error_message']} {error_info['file_path']} {error_info['function_name']}"
        embedding = self.get_embedding(embedding_text)
        embedding_hash = hashlib.md5(embedding_text.encode()).hexdigest() if embedding else None
        
        # Check if error already exists
        cursor.execute("SELECT id FROM errors WHERE signature = ?", (error_info['signature'],))
        existing = cursor.fetchone()
        
        if existing:
            error_id = existing[0]
            # Add occurrence
            cursor.execute("""
                INSERT INTO occurrences (error_id, timestamp, environment, context)
                VALUES (?, ?, ?, ?)
            """, (error_id, error_info['timestamp'], error_info['environment'], error_info['stack_trace']))
        else:
            # Insert new error
            cursor.execute("""
                INSERT INTO errors (signature, error_type, error_message, stack_trace, file_path, line_number, function_name, environment, timestamp, embedding_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                error_info['signature'],
                error_info['error_type'],
                error_info['error_message'],
                error_info['stack_trace'],
                error_info['file_path'],
                error_info['line_number'],
                error_info['function_name'],
                error_info['environment'],
                error_info['timestamp'],
                embedding_hash
            ))
            error_id = cursor.lastrowid
            
            # Add first occurrence
            cursor.execute("""
                INSERT INTO occurrences (error_id, timestamp, environment, context)
                VALUES (?, ?, ?, ?)
            """, (error_id, error_info['timestamp'], error_info['environment'], error_info['stack_trace']))
        
        conn.commit()
        conn.close()
        
        return error_id
    
    def find_related_commits(self, file_path: str, line_number: Optional[int] = None, days: int = 90) -> List[Dict]:
        """Find commits that touched the error location"""
        commits = []
        
        if not file_path:
            return commits
        
        try:
            # Get commits that modified this file
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            cmd = ['git', 'log', '--since', since_date, '--format=%H|%s|%ai|%an', '--', file_path]
            result = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commit_hash, message, date, author = parts
                        
                        # Check if commit message suggests a fix
                        is_fix = any(keyword in message.lower() for keyword in ['fix', 'bug', 'error', 'issue', 'resolve', 'patch'])
                        
                        commits.append({
                            'hash': commit_hash,
                            'message': message,
                            'date': date,
                            'author': author,
                            'is_fix': is_fix,
                        })
        except Exception as e:
            print(f"⚠️  Error finding commits: {e}")
        
        return commits
    
    def get_commit_diff(self, commit_hash: str, file_path: Optional[str] = None) -> str:
        """Get diff for a commit"""
        try:
            cmd = ['git', 'show', '--format=', commit_hash]
            if file_path:
                cmd.extend(['--', file_path])
            
            result = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        
        return ""
    
    def find_related_tests(self, file_path: str) -> List[str]:
        """Find test files related to the error location"""
        if not file_path:
            return []
        
        test_files = []
        
        # Strategy 1: Naming convention
        file_name = Path(file_path).stem
        
        # Python tests
        for pattern in [f'test_{file_name}.py', f'{file_name}_test.py', f'test_*{file_name}*.py']:
            for test_file in self.root.rglob(pattern):
                test_files.append(str(test_file.relative_to(self.root)))
        
        # JavaScript/TypeScript tests
        for pattern in [f'{file_name}.test.ts', f'{file_name}.spec.ts', f'{file_name}.test.js', f'{file_name}.spec.js']:
            for test_file in self.root.rglob(pattern):
                test_files.append(str(test_file.relative_to(self.root)))
        
        return list(set(test_files))

    def find_similar_errors(self, error_info: Dict, top_k: int = 5) -> List[Dict]:
        """
        Find similar past errors using vector similarity

        Returns list of similar errors with:
        - Error details
        - Similarity score
        - Fixes applied
        - Occurrences count
        """
        similar_errors = []

        # Create embedding for current error
        embedding_text = f"{error_info['error_type']} {error_info['error_message']} {error_info['file_path']} {error_info['function_name']}"
        current_embedding = self.get_embedding(embedding_text)

        if not current_embedding:
            # Fallback to keyword matching
            return self._find_similar_errors_keyword(error_info, top_k)

        # Get all errors from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, signature, error_type, error_message, file_path, line_number, function_name, timestamp, embedding_hash
            FROM errors
            WHERE signature != ?
        """, (error_info.get('signature', ''),))

        all_errors = cursor.fetchall()

        # Calculate similarity for each error
        for error_row in all_errors:
            error_id, signature, error_type, error_message, file_path, line_number, function_name, timestamp, embedding_hash = error_row

            # Get embedding
            past_embedding_text = f"{error_type} {error_message} {file_path} {function_name}"
            past_embedding = self.get_embedding(past_embedding_text)

            if not past_embedding:
                continue

            # Calculate similarity
            similarity = self.cosine_similarity(current_embedding, past_embedding)

            if similarity > 0.6:  # Threshold
                # Get fixes for this error
                cursor.execute("""
                    SELECT commit_hash, commit_message, commit_date, diff_summary, fix_description, confirmed
                    FROM fixes
                    WHERE error_id = ?
                    ORDER BY confirmed DESC, commit_date DESC
                """, (error_id,))

                fixes = []
                for fix_row in cursor.fetchall():
                    fixes.append({
                        'commit_hash': fix_row[0],
                        'commit_message': fix_row[1],
                        'commit_date': fix_row[2],
                        'diff_summary': fix_row[3],
                        'fix_description': fix_row[4],
                        'confirmed': bool(fix_row[5]),
                    })

                # Get occurrence count
                cursor.execute("SELECT COUNT(*) FROM occurrences WHERE error_id = ?", (error_id,))
                occurrence_count = cursor.fetchone()[0]

                similar_errors.append({
                    'error_id': error_id,
                    'signature': signature,
                    'error_type': error_type,
                    'error_message': error_message,
                    'file_path': file_path,
                    'line_number': line_number,
                    'function_name': function_name,
                    'timestamp': timestamp,
                    'similarity': similarity,
                    'fixes': fixes,
                    'occurrence_count': occurrence_count,
                })

        conn.close()

        # Sort by similarity
        similar_errors.sort(key=lambda x: x['similarity'], reverse=True)

        return similar_errors[:top_k]

    def _find_similar_errors_keyword(self, error_info: Dict, top_k: int = 5) -> List[Dict]:
        """Fallback keyword-based similarity search"""
        similar_errors = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Search by error type and file path
        cursor.execute("""
            SELECT id, signature, error_type, error_message, file_path, line_number, function_name, timestamp
            FROM errors
            WHERE (error_type = ? OR file_path = ? OR function_name = ?)
            AND signature != ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (
            error_info.get('error_type'),
            error_info.get('file_path'),
            error_info.get('function_name'),
            error_info.get('signature', ''),
            top_k
        ))

        for error_row in cursor.fetchall():
            error_id, signature, error_type, error_message, file_path, line_number, function_name, timestamp = error_row

            # Get fixes
            cursor.execute("""
                SELECT commit_hash, commit_message, commit_date, diff_summary, fix_description, confirmed
                FROM fixes
                WHERE error_id = ?
                ORDER BY confirmed DESC, commit_date DESC
            """, (error_id,))

            fixes = []
            for fix_row in cursor.fetchall():
                fixes.append({
                    'commit_hash': fix_row[0],
                    'commit_message': fix_row[1],
                    'commit_date': fix_row[2],
                    'diff_summary': fix_row[3],
                    'fix_description': fix_row[4],
                    'confirmed': bool(fix_row[5]),
                })

            # Get occurrence count
            cursor.execute("SELECT COUNT(*) FROM occurrences WHERE error_id = ?", (error_id,))
            occurrence_count = cursor.fetchone()[0]

            similar_errors.append({
                'error_id': error_id,
                'signature': signature,
                'error_type': error_type,
                'error_message': error_message,
                'file_path': file_path,
                'line_number': line_number,
                'function_name': function_name,
                'timestamp': timestamp,
                'similarity': 0.5,  # Default keyword match score
                'fixes': fixes,
                'occurrence_count': occurrence_count,
            })

        conn.close()

        return similar_errors

    def reconstruct_context(self, error_text: str, environment: str = "unknown") -> Dict:
        """
        Reconstruct full context for an error

        Returns:
        - Error signature
        - Similar past errors
        - Related commits
        - Related tests
        - Suggested fixes
        """
        # Parse error
        error_info = self.parse_error(error_text, environment)

        # Store error
        error_id = self.store_error(error_info)

        # Find similar errors
        similar_errors = self.find_similar_errors(error_info)

        # Find related commits
        related_commits = []
        if error_info['file_path']:
            related_commits = self.find_related_commits(error_info['file_path'], error_info['line_number'])

        # Find related tests
        related_tests = []
        if error_info['file_path']:
            related_tests = self.find_related_tests(error_info['file_path'])

        # Generate fix suggestions
        fix_suggestions = self._generate_fix_suggestions(error_info, similar_errors, related_commits)

        return {
            'error_id': error_id,
            'error_info': error_info,
            'similar_errors': similar_errors,
            'related_commits': related_commits,
            'related_tests': related_tests,
            'fix_suggestions': fix_suggestions,
        }

    def _generate_fix_suggestions(self, error_info: Dict, similar_errors: List[Dict], related_commits: List[Dict]) -> List[Dict]:
        """Generate ranked fix suggestions"""
        suggestions = []

        # From similar errors
        for similar in similar_errors:
            for fix in similar['fixes']:
                suggestions.append({
                    'source': 'similar_error',
                    'description': f"Similar error fixed by: {fix['commit_message']}",
                    'commit_hash': fix['commit_hash'],
                    'commit_date': fix['commit_date'],
                    'diff_summary': fix['diff_summary'],
                    'similarity': similar['similarity'],
                    'confirmed': fix['confirmed'],
                    'score': similar['similarity'] * (2.0 if fix['confirmed'] else 1.0),
                })

        # From related commits (fixes)
        for commit in related_commits:
            if commit['is_fix']:
                suggestions.append({
                    'source': 'related_commit',
                    'description': f"Related fix: {commit['message']}",
                    'commit_hash': commit['hash'],
                    'commit_date': commit['date'],
                    'diff_summary': None,
                    'similarity': 0.7,
                    'confirmed': False,
                    'score': 0.7,
                })

        # Sort by score
        suggestions.sort(key=lambda x: x['score'], reverse=True)

        return suggestions[:5]  # Top 5

    def confirm_fix(self, error_id: int, commit_hash: str, fix_description: str = ""):
        """Confirm that a fix worked for an error"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get commit details
        try:
            cmd = ['git', 'show', '--format=%s|%ai', '--no-patch', commit_hash]
            result = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                commit_message = parts[0] if len(parts) > 0 else ""
                commit_date = parts[1] if len(parts) > 1 else ""

                # Get diff summary
                diff = self.get_commit_diff(commit_hash)
                diff_summary = diff[:500] if diff else ""

                # Insert fix
                cursor.execute("""
                    INSERT INTO fixes (error_id, commit_hash, commit_message, commit_date, diff_summary, fix_description, confirmed)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (error_id, commit_hash, commit_message, commit_date, diff_summary, fix_description))

                conn.commit()
        except Exception as e:
            print(f"⚠️  Error confirming fix: {e}")
        finally:
            conn.close()

    def get_error_stats(self) -> Dict:
        """Get error statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total errors
        cursor.execute("SELECT COUNT(*) FROM errors")
        total_errors = cursor.fetchone()[0]

        # Total occurrences
        cursor.execute("SELECT COUNT(*) FROM occurrences")
        total_occurrences = cursor.fetchone()[0]

        # Errors with fixes
        cursor.execute("SELECT COUNT(DISTINCT error_id) FROM fixes")
        errors_with_fixes = cursor.fetchone()[0]

        # Top error types
        cursor.execute("""
            SELECT error_type, COUNT(*) as count
            FROM errors
            GROUP BY error_type
            ORDER BY count DESC
            LIMIT 10
        """)
        top_error_types = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Most frequent errors
        cursor.execute("""
            SELECT e.signature, e.error_message, COUNT(o.id) as count
            FROM errors e
            JOIN occurrences o ON e.id = o.error_id
            GROUP BY e.id
            ORDER BY count DESC
            LIMIT 10
        """)
        most_frequent = [{'signature': row[0], 'message': row[1], 'count': row[2]} for row in cursor.fetchall()]

        conn.close()

        return {
            'total_errors': total_errors,
            'total_occurrences': total_occurrences,
            'errors_with_fixes': errors_with_fixes,
            'top_error_types': top_error_types,
            'most_frequent': most_frequent,
        }


def main():
    """CLI for error context reconstructor"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 brain_error.py <error_file>")
        print('       python3 brain_error.py stats')
        return

    # Initialize
    import os
    project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
    openai_api_key = os.getenv("OPENAI_API_KEY")

    reconstructor = ErrorContextReconstructor(project_path, openai_api_key)

    if sys.argv[1] == 'stats':
        # Show statistics
        stats = reconstructor.get_error_stats()

        print("\n" + "=" * 70)
        print("🧠 ERROR CONTEXT RECONSTRUCTOR - STATISTICS")
        print("=" * 70)

        print(f"\n📊 Overview:")
        print(f"   Total unique errors: {stats['total_errors']}")
        print(f"   Total occurrences: {stats['total_occurrences']}")
        print(f"   Errors with fixes: {stats['errors_with_fixes']}")

        if stats['top_error_types']:
            print(f"\n🔥 Top Error Types:")
            for item in stats['top_error_types']:
                print(f"   {item['type']}: {item['count']}")

        if stats['most_frequent']:
            print(f"\n📈 Most Frequent Errors:")
            for item in stats['most_frequent']:
                print(f"   {item['signature']}: {item['count']} times")

        print("\n" + "=" * 70)
    else:
        # Analyze error from file
        error_file = sys.argv[1]

        try:
            with open(error_file, 'r') as f:
                error_text = f.read()
        except FileNotFoundError:
            print(f"❌ Error file not found: {error_file}")
            return

        # Reconstruct context
        context = reconstructor.reconstruct_context(error_text)

        # Print results
        print("\n" + "=" * 70)
        print("🧠 ERROR CONTEXT RECONSTRUCTOR")
        print("=" * 70)

        error_info = context['error_info']
        print(f"\n📍 Error Signature:")
        print(f"   {error_info['signature']}")

        if error_info['error_type']:
            print(f"\n🔴 Error Type: {error_info['error_type']}")
        if error_info['error_message']:
            print(f"💬 Message: {error_info['error_message']}")
        if error_info['file_path']:
            print(f"📄 File: {error_info['file_path']}")
            if error_info['line_number']:
                print(f"📍 Line: {error_info['line_number']}")
        if error_info['function_name']:
            print(f"⚙️  Function: {error_info['function_name']}")

        # Similar errors
        if context['similar_errors']:
            print(f"\n🔍 Similar Past Errors ({len(context['similar_errors'])}):")
            for i, similar in enumerate(context['similar_errors'][:3], 1):
                print(f"\n   {i}. {similar['signature']}")
                print(f"      Similarity: {similar['similarity']:.2%}")
                print(f"      Occurrences: {similar['occurrence_count']}")
                if similar['fixes']:
                    print(f"      Fixes: {len(similar['fixes'])}")
                    for fix in similar['fixes'][:1]:
                        print(f"         ✅ {fix['commit_message']} ({fix['commit_date'][:10]})")

        # Fix suggestions
        if context['fix_suggestions']:
            print(f"\n💡 Fix Suggestions:")
            for i, suggestion in enumerate(context['fix_suggestions'][:3], 1):
                print(f"\n   {i}. {suggestion['description']}")
                print(f"      Commit: {suggestion['commit_hash'][:8]}")
                print(f"      Date: {suggestion['commit_date'][:10]}")
                print(f"      Score: {suggestion['score']:.2f}")
                if suggestion['confirmed']:
                    print(f"      ✅ Confirmed fix")

        # Related commits
        if context['related_commits']:
            print(f"\n📝 Related Commits ({len(context['related_commits'])}):")
            for commit in context['related_commits'][:3]:
                print(f"   • {commit['message']} ({commit['date'][:10]})")

        # Related tests
        if context['related_tests']:
            print(f"\n🧪 Related Tests ({len(context['related_tests'])}):")
            for test in context['related_tests'][:5]:
                print(f"   • {test}")

        print("\n" + "=" * 70)


if __name__ == "__main__":
    main()


