#!/usr/bin/env python3
"""
Quick test of the bot detection framework
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from brain_bottest import BotDetectionTester

def test_framework():
    """Test the framework"""
    print("=" * 70)
    print("🧪 Testing Bot Detection Framework")
    print("=" * 70)
    
    try:
        # Test 1: Initialize
        print("\n1️⃣  Initializing framework...")
        project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
        tester = BotDetectionTester(project_path)
        print(f"   ✅ Framework initialized")
        print(f"   📁 Root: {tester.root}")
        print(f"   📁 Artifacts: {tester.artifacts_dir}")
        
        # Test 2: Load scenarios
        print("\n2️⃣  Loading scenarios...")
        tester.load_scenarios()
        print(f"   ✅ Loaded {len(tester.scenarios)} scenarios")
        
        # Test 3: Get metrics
        print("\n3️⃣  Getting metrics...")
        metrics = tester.get_metrics_summary()
        print(f"   ✅ Metrics retrieved")
        print(f"   📊 Total tests: {metrics['total_tests']}")
        
        # Test 4: Check if we can generate report
        print("\n4️⃣  Checking report generation...")
        if tester.results:
            report_path = tester.generate_report()
            print(f"   ✅ Report generated: {report_path}")
        else:
            print(f"   ⚠️  No results to report (run tests first)")
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = test_framework()
    sys.exit(0 if success else 1)

