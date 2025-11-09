#!/usr/bin/env python3
"""
Simple script to create placeholder icons for the Chrome extension
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory
os.makedirs('icons', exist_ok=True)

# Icon sizes
sizes = [16, 48, 128]

# Colors
bg_color = (102, 126, 234)  # Purple gradient color
text_color = (255, 255, 255)  # White

for size in sizes:
    # Create image
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple lock icon using shapes
    if size == 16:
        # Small icon - just a simple rectangle
        draw.rectangle([4, 6, 12, 14], fill=text_color)
        draw.rectangle([6, 4, 10, 8], outline=text_color, width=1)
    elif size == 48:
        # Medium icon - lock shape
        # Lock body
        draw.rectangle([14, 22, 34, 42], fill=text_color)
        # Lock shackle
        draw.arc([18, 12, 30, 26], 0, 180, fill=text_color, width=3)
        # Keyhole
        draw.ellipse([22, 28, 26, 32], fill=bg_color)
        draw.rectangle([23, 31, 25, 36], fill=bg_color)
    else:  # 128
        # Large icon - detailed lock
        # Lock body
        draw.rectangle([36, 58, 92, 112], fill=text_color, outline=text_color)
        # Lock shackle
        draw.arc([48, 32, 80, 68], 0, 180, fill=text_color, width=8)
        # Keyhole
        draw.ellipse([58, 74, 70, 86], fill=bg_color)
        draw.rectangle([62, 84, 66, 98], fill=bg_color)
    
    # Save
    filename = f'icons/icon{size}.png'
    img.save(filename)
    print(f'✅ Created {filename}')

print('\n🎉 All icons created successfully!')
print('📁 Icons saved in: chrome-extension/icons/')

