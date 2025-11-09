#!/bin/bash

echo "🧪 Testing Context Continuity System"
echo "===================================="
echo ""

echo "1️⃣  Starting a work session..."
python3 brain_context.py start "Testing context continuity features"
echo ""

echo "2️⃣  Adding some notes..."
python3 brain_context.py note "Implemented graph intelligence with NetworkX"
python3 brain_context.py note "Added file watcher for real-time updates"
python3 brain_context.py note "Created visual dashboard with D3.js"
echo ""

echo "3️⃣  Tracking file edits..."
python3 brain_context.py edit "project_brain.py"
python3 brain_context.py edit "brain_cli.py"
python3 brain_context.py edit "brain_context.py"
echo ""

echo "4️⃣  Ending the session..."
python3 brain_context.py end "Successfully implemented context continuity system"
echo ""

echo "5️⃣  Showing the recap (simulating return after time away)..."
python3 brain_context.py recap
echo ""

echo "6️⃣  Showing recent sessions..."
python3 brain_context.py sessions
echo ""

echo "✅ Test complete!"

