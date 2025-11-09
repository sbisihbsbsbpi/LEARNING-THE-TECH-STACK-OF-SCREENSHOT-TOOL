#!/bin/bash

echo "======================================================================="
echo "🤖 Running Bot Detection Tests"
echo "======================================================================="
echo ""

cd "/Users/tlreddy/Documents/project 1/screenshot-app"

echo "📋 Loading scenarios from bot_test_scenarios.json..."
python3 -c "
import json
with open('bot_test_scenarios.json', 'r') as f:
    data = json.load(f)
    print(f'Found {len(data[\"scenarios\"])} scenarios:')
    for i, s in enumerate(data['scenarios'], 1):
        print(f'  {i}. {s[\"name\"]} - {s[\"target_url\"]}')
"

echo ""
echo "🚀 Running tests..."
echo ""

python3 brain_bottest.py run

echo ""
echo "======================================================================="
echo "✅ Tests complete!"
echo "======================================================================="

