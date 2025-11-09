#!/usr/bin/env python3
"""
Project Brain Change Impact Forecaster
Predicts what might break before you touch code
"""

import json
import subprocess
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from datetime import datetime, timedelta


class ChangeImpactForecaster:
    """
    Change Impact Forecaster - Predicts what might break before code changes
    
    Features:
    1. Dependency Tracing - Direct and indirect dependencies
    2. Git History Analysis - Commit patterns, change frequency, bug history
    3. Test Mapping - Related tests, coverage gaps
    4. Risk Scoring - Comprehensive risk assessment
    """
    
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        
        # Dependency graph (from project_brain)
        self.dependencies = {}  # file -> set of dependencies
        self.reverse_deps = {}  # file -> set of dependents
        
        # Git history data
        self.file_history = {}  # file -> {commits, changes, bugs, authors}
        
        # Test mapping
        self.test_map = {}  # file -> set of test files
        self.reverse_test_map = {}  # test -> set of files it tests
        
        # Risk factors
        self.risk_factors = {
            'high_change_frequency': 0.3,    # File changes often
            'recent_bugs': 0.4,              # Recent bug fixes
            'many_dependents': 0.2,          # Many files depend on it
            'no_tests': 0.5,                 # No test coverage
            'complex_code': 0.2,             # High complexity
            'multiple_authors': 0.1,         # Many authors (coordination risk)
        }
    
    def load_dependencies(self, brain_dependencies: Dict):
        """Load dependency graph from project brain"""
        self.dependencies = {k: set(v) if isinstance(v, (list, set)) else v 
                           for k, v in brain_dependencies.items()}
        
        # Build reverse dependency map
        for file, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.reverse_deps:
                    self.reverse_deps[dep] = set()
                self.reverse_deps[dep].add(file)
    
    def analyze_git_history(self, days: int = 90):
        """Analyze git history for all files"""
        print(f"📊 Analyzing git history (last {days} days)...")
        
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get all commits with file changes
            cmd = f'git log --since="{since_date}" --pretty=format:"%H|%an|%ad|%s" --date=iso --name-only'
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  Git history not available")
                return
            
            current_commit = None
            
            for line in result.stdout.strip().split('\n'):
                if not line:
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
                        }
                else:
                    # File name
                    if current_commit:
                        file_path = line.strip()
                        if file_path not in self.file_history:
                            self.file_history[file_path] = {
                                'commits': [],
                                'change_count': 0,
                                'bug_fixes': 0,
                                'authors': set(),
                                'last_changed': None,
                            }
                        
                        self.file_history[file_path]['commits'].append(current_commit)
                        self.file_history[file_path]['change_count'] += 1
                        self.file_history[file_path]['authors'].add(current_commit['author'])
                        
                        # Detect bug fixes
                        msg_lower = current_commit['message'].lower()
                        if any(word in msg_lower for word in ['fix', 'bug', 'error', 'crash', 'issue']):
                            self.file_history[file_path]['bug_fixes'] += 1
                        
                        # Track last change
                        if not self.file_history[file_path]['last_changed']:
                            self.file_history[file_path]['last_changed'] = current_commit['date']
            
            print(f"✅ Analyzed history for {len(self.file_history)} files")
            
        except Exception as e:
            print(f"⚠️  Error analyzing git history: {e}")
    
    def map_tests(self):
        """Map files to their test files"""
        print("🧪 Mapping tests to source files...")
        
        # Find all test files
        test_files = []
        for file_path in self.dependencies.keys():
            if 'test' in file_path.lower() or file_path.startswith('test_'):
                test_files.append(file_path)
        
        # Map tests to source files
        for test_file in test_files:
            # Extract what this test is testing
            tested_files = self._infer_tested_files(test_file)
            
            self.reverse_test_map[test_file] = tested_files
            
            for source_file in tested_files:
                if source_file not in self.test_map:
                    self.test_map[source_file] = set()
                self.test_map[source_file].add(test_file)
        
        print(f"✅ Mapped {len(test_files)} test files")
    
    def _infer_tested_files(self, test_file: str) -> Set[str]:
        """Infer which files a test file is testing"""
        tested = set()
        
        # Strategy 1: test_foo.py tests foo.py
        if test_file.startswith('test_'):
            source_name = test_file[5:]  # Remove 'test_'
            for file_path in self.dependencies.keys():
                if file_path.endswith(source_name):
                    tested.add(file_path)
        
        # Strategy 2: Check imports in test file
        if test_file in self.dependencies:
            for dep in self.dependencies[test_file]:
                # If test imports a module, it's probably testing it
                if 'test' not in dep.lower():
                    tested.add(dep)
        
        return tested
    
    def calculate_complexity(self, file_path: str) -> int:
        """Calculate code complexity (simple metric)"""
        try:
            full_path = self.root / file_path
            if not full_path.exists() or not file_path.endswith('.py'):
                return 0
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple complexity metrics
            complexity = 0
            
            # Count functions/methods
            complexity += len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
            
            # Count classes
            complexity += len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE)) * 2
            
            # Count conditionals
            complexity += len(re.findall(r'\b(if|elif|else|for|while|try|except)\b', content))
            
            # Count async functions (more complex)
            complexity += len(re.findall(r'^\s*async\s+def\s+\w+', content, re.MULTILINE)) * 2
            
            return complexity
            
        except Exception:
            return 0
    
    def trace_dependencies(self, file_path: str, max_depth: int = 3) -> Dict:
        """
        Trace all dependencies of a file
        
        Returns:
        {
            'direct': [...],
            'indirect': [...],
            'dependents': [...],
            'indirect_dependents': [...]
        }
        """
        direct_deps = list(self.dependencies.get(file_path, set()))
        direct_dependents = list(self.reverse_deps.get(file_path, set()))
        
        # Trace indirect dependencies (BFS)
        indirect_deps = set()
        visited = set([file_path])
        queue = [(dep, 1) for dep in direct_deps]
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth >= max_depth:
                continue
            
            visited.add(current)
            indirect_deps.add(current)
            
            # Add dependencies of current
            for dep in self.dependencies.get(current, set()):
                if dep not in visited:
                    queue.append((dep, depth + 1))
        
        # Remove direct deps from indirect
        indirect_deps = indirect_deps - set(direct_deps)
        
        # Trace indirect dependents
        indirect_dependents = set()
        visited = set([file_path])
        queue = [(dep, 1) for dep in direct_dependents]
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth >= max_depth:
                continue
            
            visited.add(current)
            indirect_dependents.add(current)
            
            # Add dependents of current
            for dep in self.reverse_deps.get(current, set()):
                if dep not in visited:
                    queue.append((dep, depth + 1))
        
        # Remove direct dependents from indirect
        indirect_dependents = indirect_dependents - set(direct_dependents)
        
        return {
            'direct': direct_deps,
            'indirect': list(indirect_deps),
            'dependents': direct_dependents,
            'indirect_dependents': list(indirect_dependents),
        }
    
    def calculate_risk_score(self, file_path: str) -> Dict:
        """
        Calculate comprehensive risk score for modifying a file
        
        Returns:
        {
            'total_risk': 0.0-1.0,
            'risk_factors': {...},
            'risk_level': 'LOW'|'MEDIUM'|'HIGH'|'CRITICAL'
        }
        """
        risk_factors = {}
        total_risk = 0.0
        
        # Factor 1: Change frequency
        history = self.file_history.get(file_path, {})
        change_count = history.get('change_count', 0)
        if change_count > 10:
            risk_factors['high_change_frequency'] = self.risk_factors['high_change_frequency']
            total_risk += self.risk_factors['high_change_frequency']
        
        # Factor 2: Recent bugs
        bug_fixes = history.get('bug_fixes', 0)
        if bug_fixes > 0:
            risk_factors['recent_bugs'] = self.risk_factors['recent_bugs'] * min(bug_fixes / 5, 1.0)
            total_risk += risk_factors['recent_bugs']
        
        # Factor 3: Many dependents
        dependents_count = len(self.reverse_deps.get(file_path, set()))
        if dependents_count > 5:
            risk_factors['many_dependents'] = self.risk_factors['many_dependents'] * min(dependents_count / 10, 1.0)
            total_risk += risk_factors['many_dependents']
        
        # Factor 4: No tests
        has_tests = file_path in self.test_map and len(self.test_map[file_path]) > 0
        if not has_tests:
            risk_factors['no_tests'] = self.risk_factors['no_tests']
            total_risk += self.risk_factors['no_tests']
        
        # Factor 5: Code complexity
        complexity = self.calculate_complexity(file_path)
        if complexity > 50:
            risk_factors['complex_code'] = self.risk_factors['complex_code'] * min(complexity / 100, 1.0)
            total_risk += risk_factors['complex_code']
        
        # Factor 6: Multiple authors
        authors_count = len(history.get('authors', set()))
        if authors_count > 3:
            risk_factors['multiple_authors'] = self.risk_factors['multiple_authors']
            total_risk += self.risk_factors['multiple_authors']
        
        # Normalize to 0-1
        total_risk = min(total_risk, 1.0)
        
        # Determine risk level
        if total_risk < 0.3:
            risk_level = 'LOW'
        elif total_risk < 0.6:
            risk_level = 'MEDIUM'
        elif total_risk < 0.8:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        return {
            'total_risk': total_risk,
            'risk_factors': risk_factors,
            'risk_level': risk_level,
            'details': {
                'change_count': change_count,
                'bug_fixes': bug_fixes,
                'dependents_count': dependents_count,
                'has_tests': has_tests,
                'complexity': complexity,
                'authors_count': authors_count,
            }
        }
    
    def forecast_impact(self, file_path: str) -> Dict:
        """
        Comprehensive impact forecast for modifying a file
        
        Returns complete analysis including:
        - Dependencies affected
        - Risk score
        - Tests to run
        - Recent changes
        - Recommendations
        """
        print(f"\n🔮 Forecasting impact of modifying: {file_path}")
        
        # Trace dependencies
        deps = self.trace_dependencies(file_path)
        
        # Calculate risk
        risk = self.calculate_risk_score(file_path)
        
        # Get related tests
        related_tests = list(self.test_map.get(file_path, set()))
        
        # Get recent history
        history = self.file_history.get(file_path, {})
        recent_commits = history.get('commits', [])[:5]
        
        # Calculate total impact
        total_affected = (
            len(deps['direct']) +
            len(deps['indirect']) +
            len(deps['dependents']) +
            len(deps['indirect_dependents'])
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(file_path, deps, risk, related_tests)
        
        return {
            'file': file_path,
            'risk_score': risk['total_risk'],
            'risk_level': risk['risk_level'],
            'risk_factors': risk['risk_factors'],
            'risk_details': risk['details'],
            'dependencies': deps,
            'total_affected_files': total_affected,
            'related_tests': related_tests,
            'recent_commits': recent_commits,
            'recommendations': recommendations,
        }
    
    def _generate_recommendations(self, file_path: str, deps: Dict, risk: Dict, tests: List) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Test recommendations
        if not tests:
            recommendations.append("⚠️  CRITICAL: No tests found - write tests before modifying")
        else:
            recommendations.append(f"✅ Run {len(tests)} related test(s): {', '.join(tests[:3])}")
        
        # Dependency recommendations
        if len(deps['dependents']) > 5:
            recommendations.append(f"⚠️  {len(deps['dependents'])} files depend on this - review all dependents")
        
        # Risk recommendations
        if risk['risk_level'] in ['HIGH', 'CRITICAL']:
            recommendations.append("🚨 HIGH RISK - Consider pair programming or extra code review")
        
        if risk['details']['bug_fixes'] > 2:
            recommendations.append(f"⚠️  {risk['details']['bug_fixes']} recent bug fixes - this area is fragile")
        
        if risk['details']['complexity'] > 50:
            recommendations.append("💡 High complexity - consider refactoring before major changes")
        
        # Impact recommendations
        total_affected = len(deps['direct']) + len(deps['indirect']) + len(deps['dependents']) + len(deps['indirect_dependents'])
        if total_affected > 10:
            recommendations.append(f"📊 {total_affected} files affected - plan for comprehensive testing")
        
        return recommendations


def main():
    """CLI for change impact forecaster"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 brain_impact.py <file_path>")
        print('Example: python3 brain_impact.py backend/auth_service.py')
        return
    
    file_path = sys.argv[1]
    
    # Initialize
    project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
    forecaster = ChangeImpactForecaster(project_path)
    
    # Load brain index
    from project_brain import ProjectBrain
    brain = ProjectBrain(project_path)
    
    index_file = brain.root / "project_index.json"
    if index_file.exists():
        with open(index_file) as f:
            data = json.load(f)
            brain.dependencies = {k: set(v) for k, v in data['dependencies'].items()}
    
    # Load dependencies
    forecaster.load_dependencies(brain.dependencies)
    
    # Analyze git history
    forecaster.analyze_git_history()
    
    # Map tests
    forecaster.map_tests()
    
    # Forecast impact
    result = forecaster.forecast_impact(file_path)
    
    # Print results
    print("\n" + "=" * 70)
    print("🔮 CHANGE IMPACT FORECAST")
    print("=" * 70)
    
    # Risk assessment
    risk_emoji = {'LOW': '✅', 'MEDIUM': '⚠️', 'HIGH': '🚨', 'CRITICAL': '🔥'}
    print(f"\n{risk_emoji[result['risk_level']]} Risk Level: {result['risk_level']}")
    print(f"📊 Risk Score: {result['risk_score']:.2f}/1.00")
    
    if result['risk_factors']:
        print(f"\n⚠️  Risk Factors:")
        for factor, score in result['risk_factors'].items():
            print(f"   • {factor.replace('_', ' ').title()}: {score:.2f}")
    
    # Impact summary
    print(f"\n📈 Impact Summary:")
    print(f"   Total files affected: {result['total_affected_files']}")
    print(f"   Direct dependencies: {len(result['dependencies']['direct'])}")
    print(f"   Indirect dependencies: {len(result['dependencies']['indirect'])}")
    print(f"   Direct dependents: {len(result['dependencies']['dependents'])}")
    print(f"   Indirect dependents: {len(result['dependencies']['indirect_dependents'])}")
    
    # Tests
    if result['related_tests']:
        print(f"\n🧪 Related Tests ({len(result['related_tests'])}):")
        for test in result['related_tests'][:5]:
            print(f"   • {test}")
    else:
        print(f"\n🧪 Related Tests: None found ⚠️")
    
    # Recent changes
    if result['recent_commits']:
        print(f"\n📝 Recent Changes:")
        for commit in result['recent_commits'][:3]:
            print(f"   {commit['hash']} - {commit['message']}")
            print(f"   └─ {commit['author']} on {commit['date'][:10]}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

