#!/usr/bin/env python3
"""
Install patchright package
"""
import subprocess
import sys

def main():
    print("🔧 Installing patchright...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "patchright"])
        print("✅ Patchright installed successfully!")
        
        # Verify installation
        import patchright
        print(f"✅ Patchright version: {patchright.__version__}")
        
        # Install Chrome browser for patchright
        print("\n🌐 Installing Chrome browser for patchright...")
        subprocess.check_call([sys.executable, "-m", "patchright", "install", "chrome"])
        print("✅ Chrome browser installed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

