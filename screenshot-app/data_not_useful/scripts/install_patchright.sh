#!/bin/bash

# 🎯 Patchright Installation Script
# Installs Patchright and Chrome browser for maximum stealth

echo "🎯 Installing Patchright for maximum stealth..."
echo ""

# Step 1: Install Patchright
echo "📦 Step 1/3: Installing Patchright Python package..."
pip install patchright

if [ $? -eq 0 ]; then
    echo "✅ Patchright installed successfully!"
else
    echo "❌ Failed to install Patchright"
    exit 1
fi

echo ""

# Step 2: Install Chrome browser
echo "🌐 Step 2/3: Installing Chrome browser..."
patchright install chrome

if [ $? -eq 0 ]; then
    echo "✅ Chrome browser installed successfully!"
else
    echo "❌ Failed to install Chrome browser"
    exit 1
fi

echo ""

# Step 3: Verify installation
echo "🧪 Step 3/3: Verifying installation..."
python3 -c "from patchright.async_api import async_playwright; print('✅ Patchright is ready to use!')"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Restart your backend: cd backend && python3 main.py"
    echo "  2. Look for: '🎯 Using Patchright - CDP leaks patched at source level!'"
    echo "  3. Test with Zomato (enable both checkboxes)"
    echo ""
    echo "📚 Documentation: PATCHRIGHT_INTEGRATION.md"
else
    echo "❌ Verification failed"
    exit 1
fi

