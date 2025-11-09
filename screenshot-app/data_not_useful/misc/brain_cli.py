#!/usr/bin/env python3
"""
Project Brain CLI - Interactive file management assistant
Ask questions like "where is the screenshot code?" and get instant answers

Enhanced with OpenAI for semantic understanding (optional)
"""

import sys
import os
from project_brain import ProjectBrain
from brain_context import ContextContinuity
from brain_intent import IntentEngine
from brain_impact import ChangeImpactForecaster
from brain_config import SmartConfigFinder
from brain_error import ErrorContextReconstructor

def print_header():
    print("\n" + "="*70)
    print("🧠 PROJECT BRAIN - Intelligent File Assistant")
    print("="*70)
    print("Ask me anything about your project files!")
    print("Examples:")
    print("  • 'find screenshot code'")
    print("  • 'where is config?'")
    print("  • 'show production files'")
    print("  • 'what depends on screenshot_service?'")
    print("  • 'search quality'")
    print("\nType 'help' for commands, 'quit' to exit")
    print("="*70 + "\n")

def print_help():
    print("\n📖 Available Commands:")
    print("\n  🔍 Search & Discovery:")
    print("    find <intent>       - Find files by purpose (e.g., 'find screenshot')")
    print("    search <query>      - Smart search across all files")
    print("    ask <question>      - Ask AI semantic questions (requires OpenAI)")
    print("\n  🎯 Intent Engine:")
    print("    intent <purpose>    - Understand developer intent and find relevant code")
    print("                          (e.g., 'intent fix login lag', 'intent add payment')")

    print("\n  🔮 Change Impact Forecaster:")
    print("    impact <file>       - Predict what might break before modifying a file")
    print("                          (e.g., 'impact backend/auth_service.py')")

    print("\n  🧭 Smart Config Finder:")
    print("    config <key>        - Find where a config key is defined")
    print("                          (e.g., 'config paymentGatewayUrl')")
    print("    config list         - List all config keys")
    print("    config shadows      - Detect duplicate/conflicting configs")
    print("    config stats        - Show config statistics")

    print("\n  🧠 AI Error Context Reconstructor:")
    print("    error analyze <file> - Analyze error from file and find similar past errors")
    print("    error paste          - Paste error text and analyze")
    print("    error stats          - Show error statistics")
    print("    error confirm <id> <commit> - Confirm a fix worked for an error")
    print("\n  📊 Graph Intelligence (requires networkx):")
    print("    impact <file>       - Show impact radius of changing a file")
    print("    circular            - Find circular dependencies")
    print("    orphans             - Find orphaned files (no deps, no dependents)")
    print("    health              - Run comprehensive dependency health check")
    print("\n  🧠 Context Continuity:")
    print("    recap               - Show welcome back recap")
    print("    session start <desc> - Start a new work session")
    print("    session end <summary> - End current session")
    print("    note <text>         - Add a note to current session")
    print("    sessions            - Show recent sessions")
    print("\n  📁 Project Info:")
    print("    production          - Show all production code files")
    print("    deps <file>         - Show what a file depends on")
    print("    dependents <module> - Show what depends on a module")
    print("    summary             - Show project summary")
    print("\n  ⚙️  System:")
    print("    rescan              - Rescan the project")
    print("    help                - Show this help")
    print("    quit/exit           - Exit the program\n")

def format_file_result(result, show_score=False):
    """Format a file result for display"""
    file = result.get('file', result.get('rel_path', 'Unknown'))
    purpose = result.get('purpose', 'No purpose defined')
    category = result.get('category', 'unknown')
    
    # Color coding by category
    category_icons = {
        'production': '✅',
        'config': '⚙️',
        'test': '🧪',
        'docs': '📄',
        'archived': '📦',
        'runtime': '🔄',
        'other': '📁'
    }
    
    icon = category_icons.get(category, '📁')
    
    output = f"  {icon} {file}"
    if show_score and 'score' in result:
        output += f" (score: {result['score']})"
    output += f"\n     └─ {purpose}"
    
    if 'match_reason' in result:
        output += f"\n     └─ Match: {result['match_reason']}"
    
    if 'reasons' in result:
        output += f"\n     └─ Matches: {', '.join(result['reasons'])}"
    
    return output

def handle_command(brain, command, context=None, intent_engine=None, impact_forecaster=None, config_finder=None, error_reconstructor=None):
    """Process user commands"""
    command = command.strip().lower()
    
    if not command:
        return
    
    # Quit commands
    if command in ['quit', 'exit', 'q']:
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    
    # Help
    elif command == 'help':
        print_help()
    
    # Summary
    elif command == 'summary':
        brain.print_summary()
    
    # Rescan
    elif command == 'rescan':
        print("🔄 Rescanning project...")
        brain.scan_project()
        brain.save_index()
        print("✅ Rescan complete!")
    
    # Production files
    elif command == 'production':
        print("\n🎯 Production Files:")
        files = brain.find_production_files()
        if files:
            for f in files:
                info = brain.index[f]
                print(f"  ✅ {f}")
                print(f"     └─ {info['purpose']}")
        else:
            print("  No production files found")
    
    # Find by intent
    elif command.startswith('find '):
        intent = command[5:].strip()
        print(f"\n🔍 Finding files for: '{intent}'")
        results = brain.find_by_intent(intent)
        
        if results:
            for r in results[:10]:  # Limit to top 10
                print(format_file_result(r))
        else:
            print(f"  ❌ No files found for '{intent}'")
            print("  💡 Try: 'search {intent}' for broader results")
    
    # Search
    elif command.startswith('search '):
        query = command[7:].strip()
        print(f"\n🔍 Searching for: '{query}'")
        results = brain.search(query)
        
        if results:
            print(f"\n📊 Found {len(results)} results (showing top 10):\n")
            for r in results[:10]:
                print(format_file_result(r, show_score=True))
        else:
            print(f"  ❌ No results found for '{query}'")
    
    # Dependencies
    elif command.startswith('deps '):
        file_path = command[5:].strip()
        print(f"\n🔗 Dependencies for: {file_path}")
        deps = brain.find_dependencies(file_path)
        
        if deps:
            for dep in sorted(deps):
                print(f"  📦 {dep}")
        else:
            print(f"  ℹ️  No dependencies found (or file not in index)")
    
    # Dependents
    elif command.startswith('dependents '):
        module = command[11:].strip()
        print(f"\n🔗 Files that depend on: {module}")
        dependents = brain.find_dependents(module)

        if dependents:
            for dep in sorted(dependents):
                print(f"  📄 {dep}")
        else:
            print(f"  ℹ️  No dependents found")

    # Intent Engine
    elif command.startswith('intent '):
        if not intent_engine:
            print("⚠️  Intent engine not available")
            return

        user_intent = command[7:].strip()
        results = intent_engine.find_hotspots(user_intent)

        print("\n" + "=" * 70)
        print("🎯 INTENT ENGINE RESULTS")
        print("=" * 70)

        # Insights
        if results['insights']:
            print(f"\n💡 Insights:")
            for insight in results['insights']:
                print(f"   {insight}")

        # File matches
        if results['file_matches']:
            print(f"\n📄 Top File Matches:")
            for match in results['file_matches'][:5]:
                print(f"   {match['file']} (score: {match['score']:.1f})")
                print(f"      └─ {', '.join(match['reasons'])}")

        # Function matches
        if results['function_matches']:
            print(f"\n⚡ Top Function Matches:")
            for match in results['function_matches'][:5]:
                print(f"   {match['function']} (score: {match['score']:.1f})")
                print(f"      └─ {match['info']['signature']}")

        # Commit matches
        if results['commit_matches']:
            print(f"\n📝 Related Commits:")
            for match in results['commit_matches'][:5]:
                print(f"   {match['commit']} - {match['info']['message']}")
                print(f"      └─ {match['info']['date'][:10]}")

        print("\n" + "=" * 70)

    # Ask AI (semantic search)
    elif command.startswith('ask '):
        question = command[4:].strip()
        print(f"\n🤖 Asking AI: '{question}'")
        print("⏳ Thinking...\n")
        answer = brain.ask_ai(question)
        print(answer)

    # Change Impact Forecaster
    elif command.startswith('impact '):
        if not impact_forecaster:
            print("⚠️  Impact forecaster not available")
            return

        file_path = command[7:].strip()
        result = impact_forecaster.forecast_impact(file_path)

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

        print("\n" + "=" * 70)

    # Smart Config Finder
    elif command.startswith('config '):
        if not config_finder:
            print("⚠️  Config finder not available")
            return

        sub_command = command[7:].strip()

        if sub_command == 'list':
            # List all config keys
            keys = config_finder.get_all_keys()
            print(f"\n📋 All Config Keys ({len(keys)}):\n")
            for key in keys[:50]:  # Show first 50
                print(f"   • {key}")
            if len(keys) > 50:
                print(f"\n   ... and {len(keys) - 50} more")

        elif sub_command == 'shadows':
            # Detect shadow configs
            shadows = config_finder.detect_shadow_configs()

            print("\n" + "=" * 70)
            print("👥 SHADOW CONFIG DETECTION")
            print("=" * 70)

            # Duplicates
            if shadows['duplicates']:
                print(f"\n🔄 Duplicates ({len(shadows['duplicates'])}):")
                print("   (Same key, same value, different files)\n")
                for dup in shadows['duplicates'][:10]:
                    print(f"   Key: {dup['key']}")
                    print(f"   Value: {dup['value']}")
                    print(f"   Locations:")
                    for loc in dup['locations']:
                        print(f"      • {loc['file']} (line {loc['line']})")
                    print()
            else:
                print("\n✅ No duplicates found")

            # Conflicts
            if shadows['conflicts']:
                print(f"\n⚠️  Conflicts ({len(shadows['conflicts'])}):")
                print("   (Same key, different values)\n")
                for conf in shadows['conflicts'][:10]:
                    print(f"   Key: {conf['key']}")
                    print(f"   Values: {', '.join(conf['values'])}")
                    print(f"   Locations:")
                    for loc in conf['locations']:
                        print(f"      • {loc['file']}: {loc['value']} (line {loc['line']})")
                    print()
            else:
                print("\n✅ No conflicts found")

            print("=" * 70)

        elif sub_command == 'stats':
            # Show statistics
            stats = config_finder.get_stats()

            print("\n" + "=" * 70)
            print("📊 CONFIG STATISTICS")
            print("=" * 70)

            print(f"\n📈 Overview:")
            print(f"   Total unique keys: {stats['total_keys']}")
            print(f"   Total entries: {stats['total_entries']}")

            print(f"\n📁 By Type:")
            for type_name, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {type_name}: {count}")

            print(f"\n📄 Top Files:")
            for file_name, count in list(stats['by_file'].items())[:10]:
                print(f"   {file_name}: {count} entries")

            print("\n" + "=" * 70)

        else:
            # Find config
            results = config_finder.find_config(sub_command)

            print("\n" + "=" * 70)
            print(f"🧭 SMART CONFIG FINDER")
            print("=" * 70)
            print(f"\nQuery: {sub_command}")

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
                    print()

            print("=" * 70)

    # AI Error Context Reconstructor
    elif command.startswith('error '):
        if not error_reconstructor:
            print("⚠️  Error reconstructor not available")
            return

        sub_command = command[6:].strip()

        if sub_command == 'stats':
            # Show error statistics
            stats = error_reconstructor.get_error_stats()

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
                for item in stats['most_frequent'][:5]:
                    print(f"   {item['signature'][:60]}: {item['count']} times")

            print("\n" + "=" * 70)

        elif sub_command.startswith('analyze '):
            # Analyze error from file
            error_file = sub_command[8:].strip()

            try:
                with open(error_file, 'r') as f:
                    error_text = f.read()
            except FileNotFoundError:
                print(f"❌ Error file not found: {error_file}")
                return

            # Reconstruct context
            context = error_reconstructor.reconstruct_context(error_text)

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
                    print(f"\n   {i}. {similar['signature'][:60]}")
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
                    print(f"   • {commit['message'][:60]} ({commit['date'][:10]})")

            # Related tests
            if context['related_tests']:
                print(f"\n🧪 Related Tests ({len(context['related_tests'])}):")
                for test in context['related_tests'][:5]:
                    print(f"   • {test}")

            print("\n" + "=" * 70)

        elif sub_command == 'paste':
            # Paste error text
            print("\n📋 Paste your error text (press Ctrl+D when done):")
            print("=" * 70)

            error_lines = []
            try:
                while True:
                    line = input()
                    error_lines.append(line)
            except EOFError:
                pass

            error_text = '\n'.join(error_lines)

            if not error_text.strip():
                print("❌ No error text provided")
                return

            # Reconstruct context
            context = error_reconstructor.reconstruct_context(error_text)

            # Print results (same as analyze)
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

            # Similar errors
            if context['similar_errors']:
                print(f"\n🔍 Similar Past Errors ({len(context['similar_errors'])}):")
                for i, similar in enumerate(context['similar_errors'][:3], 1):
                    print(f"\n   {i}. {similar['signature'][:60]}")
                    print(f"      Similarity: {similar['similarity']:.2%}")
                    if similar['fixes']:
                        for fix in similar['fixes'][:1]:
                            print(f"      ✅ {fix['commit_message']}")

            # Fix suggestions
            if context['fix_suggestions']:
                print(f"\n💡 Fix Suggestions:")
                for i, suggestion in enumerate(context['fix_suggestions'][:3], 1):
                    print(f"   {i}. {suggestion['description']}")

            print("\n" + "=" * 70)

        elif sub_command.startswith('confirm '):
            # Confirm fix
            parts = sub_command[8:].strip().split()
            if len(parts) < 2:
                print("Usage: error confirm <error_id> <commit_hash> [description]")
                return

            try:
                error_id = int(parts[0])
                commit_hash = parts[1]
                fix_description = ' '.join(parts[2:]) if len(parts) > 2 else ""

                error_reconstructor.confirm_fix(error_id, commit_hash, fix_description)
                print(f"✅ Fix confirmed for error #{error_id}")
            except ValueError:
                print("❌ Invalid error ID")

    # Circular dependencies
    elif command == 'circular':
        print("\n🔄 Searching for circular dependencies...")
        cycles = brain.graph_query_circular_deps()

        if not cycles:
            print("  ✅ No circular dependencies found!")
        else:
            print(f"  ⚠️  Found {len(cycles)} circular dependencies:\n")
            for i, cycle in enumerate(cycles[:10], 1):
                print(f"  {i}. {' → '.join(cycle)} → {cycle[0]}")

    # Orphaned files
    elif command == 'orphans':
        print("\n🏝️  Finding orphaned files...")
        orphans = brain.graph_query_orphans()

        if not orphans:
            print("  ✅ No orphaned files found!")
        else:
            print(f"  📊 Found {len(orphans)} orphaned files:\n")
            for orphan in orphans[:20]:
                print(format_file_result(orphan))

    # Health check
    elif command == 'health':
        print("\n🏥 Running dependency health check...")
        print("⏳ Analyzing project...\n")
        health = brain.health_check()

        print("=" * 60)
        print("📊 DEPENDENCY HEALTH REPORT")
        print("=" * 60)

        if health['total_issues'] == 0:
            print("\n✅ Perfect health! No issues found.\n")
        else:
            print(f"\n⚠️  Found {health['total_issues']} issues\n")

            # Circular dependencies
            if health['circular_dependencies']:
                print(f"🔄 Circular Dependencies ({len(health['circular_dependencies'])}):")
                for i, cycle in enumerate(health['circular_dependencies'][:5], 1):
                    print(f"  {i}. {' → '.join(cycle)} → {cycle[0]}")
                print()

            # Orphaned files
            if health['orphaned_files']:
                print(f"🏝️  Orphaned Files ({len(health['orphaned_files'])}):")
                for orphan in health['orphaned_files'][:5]:
                    print(f"  📄 {orphan['file']}")
                print()

            # Large files
            if health['large_files']:
                print(f"📦 Large Files >100KB ({len(health['large_files'])}):")
                for large in health['large_files'][:5]:
                    print(f"  📄 {large['file']} ({large['size_kb']}KB)")
                print()

            # Missing dependencies
            if health['missing_dependencies']:
                print(f"❓ Unresolved Imports ({len(health['missing_dependencies'])}):")
                for missing in health['missing_dependencies'][:5]:
                    print(f"  📄 {missing['file']}")
                    print(f"     └─ Missing: {missing['missing_import']}")
                print()

        print("=" * 60)

    # Context continuity - recap
    elif command == 'recap':
        if context:
            context.print_recap()
        else:
            print("⚠️  Context continuity not available")

    # Context continuity - session start
    elif command.startswith('session start'):
        if context:
            description = command[13:].strip()
            context.start_session(description)
            context.save_context()
        else:
            print("⚠️  Context continuity not available")

    # Context continuity - session end
    elif command.startswith('session end'):
        if context:
            summary = command[11:].strip()
            context.end_session(summary)
        else:
            print("⚠️  Context continuity not available")

    # Context continuity - add note
    elif command.startswith('note '):
        if context:
            note = command[5:].strip()
            context.add_note(note)
            context.save_context()
        else:
            print("⚠️  Context continuity not available")

    # Context continuity - show sessions
    elif command == 'sessions':
        if context:
            sessions = context.get_recent_sessions(30)
            print(f"\n📊 Recent Sessions (Last 30 Days):\n")
            for session in sessions:
                print(f"Session #{session['id']} - {session['start_time'][:19]}")
                if session.get('description'):
                    print(f"  Description: {session['description']}")
                print(f"  Duration: {session.get('duration_minutes', 0)} minutes")
                print(f"  Files edited: {len(session.get('files_edited', []))}")
                print()
        else:
            print("⚠️  Context continuity not available")

    # Unknown command - try smart search
    else:
        print(f"\n🤔 Interpreting as search query: '{command}'")
        results = brain.search(command)

        if results:
            print(f"\n📊 Found {len(results)} results (showing top 5):\n")
            for r in results[:5]:
                print(format_file_result(r, show_score=True))
        else:
            print(f"  ❌ No results found")
            print("  💡 Type 'help' to see available commands")

def main():
    """Main interactive loop"""
    print_header()

    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        print("🤖 OpenAI API key found - AI features enabled!")
    else:
        print("ℹ️  No OpenAI API key found - AI features disabled")
        print("   Set OPENAI_API_KEY environment variable to enable")

    # Initialize brain
    print("🧠 Initializing Project Brain...")
    brain = ProjectBrain("/Users/tlreddy/Documents/project 1/screenshot-app", openai_api_key)

    # Initialize context continuity
    print("📚 Initializing Context Continuity...")
    context = ContextContinuity("/Users/tlreddy/Documents/project 1/screenshot-app")

    # Initialize intent engine
    print("🎯 Initializing Intent Engine...")
    intent_engine = IntentEngine("/Users/tlreddy/Documents/project 1/screenshot-app", openai_api_key)

    # Initialize impact forecaster
    print("🔮 Initializing Change Impact Forecaster...")
    impact_forecaster = ChangeImpactForecaster("/Users/tlreddy/Documents/project 1/screenshot-app")

    # Initialize config finder
    print("🧭 Initializing Smart Config Finder...")
    config_finder = SmartConfigFinder("/Users/tlreddy/Documents/project 1/screenshot-app", openai_api_key)

    # Initialize error reconstructor
    print("🧠 Initializing AI Error Context Reconstructor...")
    error_reconstructor = ErrorContextReconstructor("/Users/tlreddy/Documents/project 1/screenshot-app", openai_api_key)

    # Check if index exists
    index_file = brain.root / "project_index.json"
    if index_file.exists():
        print("📖 Loading existing index...")
        import json
        with open(index_file) as f:
            data = json.load(f)
            brain.index = data['index']
            brain.dependencies = {k: set(v) for k, v in data['dependencies'].items()}
            brain.file_hashes = data.get('file_hashes', {})
        print(f"✅ Loaded {len(brain.index)} files from index")
    else:
        print("🔍 Scanning project (first time)...")
        brain.scan_project()
        brain.save_index()

    # Build intent engine hotspot graph
    print("🔥 Building code hotspot graph...")
    intent_engine.build_hotspot_graph(brain.index)

    # Initialize impact forecaster
    print("📊 Loading dependencies for impact forecaster...")
    impact_forecaster.load_dependencies(brain.dependencies)
    print("📈 Analyzing git history...")
    impact_forecaster.analyze_git_history()
    print("🧪 Mapping tests...")
    impact_forecaster.map_tests()

    # Initialize config finder
    print("🗺️  Learning configuration topology...")
    config_finder.learn_config_topology()

    # Show welcome back recap
    print("\n" + "=" * 70)
    context.print_recap()

    print("\n✨ Ready! Ask me anything about your project.")
    if brain.openai_enabled:
        print("💡 Try: intent \"fix login lag\" or ask \"where is the screenshot code?\"\n")
    else:
        print("💡 Try: intent \"add payment support\" or find screenshot\n")
    
    # Interactive loop
    while True:
        try:
            command = input("🧠 > ").strip()
            handle_command(brain, command, context, intent_engine, impact_forecaster, config_finder, error_reconstructor)
            print()  # Blank line for readability

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Type 'help' for available commands\n")

if __name__ == "__main__":
    main()

