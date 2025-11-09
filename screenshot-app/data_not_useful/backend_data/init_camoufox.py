#!/usr/bin/env python3
"""
Initialize Camoufox and browserforge dependencies.
This script downloads the required data files with SSL verification disabled.
"""

import ssl
import sys

# Disable SSL verification for downloading browserforge data files
# This is needed on macOS where Python SSL certificates may not be installed
ssl._create_default_https_context = ssl._create_unverified_context

try:
    print("📦 Initializing browserforge...")
    from browserforge.headers import HeaderGenerator
    print("✅ Browserforge initialized successfully!")
    
    print("🦊 Initializing Camoufox...")
    from camoufox.async_api import AsyncCamoufox
    print("✅ Camoufox initialized successfully!")
    
    print("\n🎉 All dependencies initialized! Camoufox is ready to use.")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error initializing dependencies: {e}")
    sys.exit(1)

