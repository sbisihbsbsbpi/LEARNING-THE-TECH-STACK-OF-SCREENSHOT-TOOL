#!/usr/bin/env python3
"""
Organize files into misc-code folder
Moves documentation and test files to keep the project clean
"""

import shutil
from pathlib import Path

# Base directory
base_dir = Path(__file__).parent

# Create misc-code structure
misc_code = base_dir / "misc-code"
misc_code.mkdir(exist_ok=True)
(misc_code / "docs").mkdir(exist_ok=True)
(misc_code / "backend-tests").mkdir(exist_ok=True)
(misc_code / "backend-docs").mkdir(exist_ok=True)

# Files to move from root
root_docs = [
    "DEBUG_REPORT.md",
    "DEV_WORKFLOW.md",
    "LINE_NUMBERS_DEBUG.md",
    "SEGMENTED_CAPTURE_FIXES.md",
    "UI_ENHANCEMENTS.md",
    "UI_IMPROVEMENTS.md",
]

# Files to move from backend
backend_tests = [
    "test_improvements.py",
    "test_stealth.py",
    "test_stealth_2025.py",
    "check_stealth_install.py",
    "install_patchright.py",
]

backend_docs = [
    "PHASE1_CHANGES.md",
    "PHASE2_CHANGES.md",
    "PHASE3_CHANGES.md",
    "STEALTH_2025_IMPLEMENTATION.md",
    "STEALTH_ENHANCEMENTS_IMPLEMENTED.md",
]

# Directories to move
dirs_to_move = [
    "chrome-extension",
    "diagnostics",
]

print("🗂️  Organizing files into misc-code/...")
print()

# Move root documentation
print("📄 Moving root documentation files...")
for file in root_docs:
    src = base_dir / file
    if src.exists():
        dst = misc_code / "docs" / file
        shutil.move(str(src), str(dst))
        print(f"   ✅ Moved {file}")
    else:
        print(f"   ⏭️  Skipped {file} (not found)")

print()

# Move backend test files
print("🧪 Moving backend test files...")
backend_dir = base_dir / "backend"
for file in backend_tests:
    src = backend_dir / file
    if src.exists():
        dst = misc_code / "backend-tests" / file
        shutil.move(str(src), str(dst))
        print(f"   ✅ Moved {file}")
    else:
        print(f"   ⏭️  Skipped {file} (not found)")

print()

# Move backend documentation
print("📚 Moving backend documentation files...")
for file in backend_docs:
    src = backend_dir / file
    if src.exists():
        dst = misc_code / "backend-docs" / file
        shutil.move(str(src), str(dst))
        print(f"   ✅ Moved {file}")
    else:
        print(f"   ⏭️  Skipped {file} (not found)")

print()

# Move directories
print("📁 Moving directories...")
for dir_name in dirs_to_move:
    src = base_dir / dir_name
    if src.exists():
        dst = misc_code / dir_name
        if dst.exists():
            print(f"   ⏭️  Skipped {dir_name} (already exists in misc-code)")
        else:
            shutil.move(str(src), str(dst))
            print(f"   ✅ Moved {dir_name}/")
    else:
        print(f"   ⏭️  Skipped {dir_name} (not found)")

print()
print("✅ File organization complete!")
print()
print("📊 Summary:")
print(f"   - Documentation files: {len(list((misc_code / 'docs').glob('*.md')))}")
print(f"   - Backend test files: {len(list((misc_code / 'backend-tests').glob('*.py')))}")
print(f"   - Backend docs: {len(list((misc_code / 'backend-docs').glob('*.md')))}")
print(f"   - Separate tools: {len([d for d in misc_code.iterdir() if d.is_dir() and d.name not in ['docs', 'backend-tests', 'backend-docs']])}")
print()
print("🎯 Your project is now cleaner and more focused!")

