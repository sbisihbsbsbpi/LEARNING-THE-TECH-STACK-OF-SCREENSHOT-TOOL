#!/usr/bin/env python3
"""
Quick script to check if Prime Video cookies exist in Chrome
"""

try:
    import rookiepy
    
    print("🔍 Checking Chrome for Amazon/Prime Video cookies...\n")
    
    # Try to get cookies from Chrome
    try:
        # Get all cookies from Chrome
        chrome_cookies = rookiepy.chrome()
        
        # Filter for Amazon/Prime Video domains
        amazon_domains = [
            'amazon.com', 'primevideo.com', 'amazon.in', 
            'amazon.co.uk', 'amazon.de', 'amazon.fr',
            'amazon.co.jp', 'amazon.ca', 'amazon.com.au'
        ]
        
        prime_cookies = []
        for cookie in chrome_cookies:
            domain = cookie.get('domain', '').lower()
            for amazon_domain in amazon_domains:
                if amazon_domain in domain:
                    prime_cookies.append(cookie)
                    break
        
        if prime_cookies:
            print(f"✅ Found {len(prime_cookies)} Amazon/Prime Video cookies in Chrome!\n")
            
            # Show unique domains
            unique_domains = set(c.get('domain', '') for c in prime_cookies)
            print("🌐 Domains:")
            for domain in sorted(unique_domains):
                count = sum(1 for c in prime_cookies if c.get('domain') == domain)
                print(f"   {domain}: {count} cookies")
            
            print("\n🔑 Sample cookies:")
            for cookie in prime_cookies[:5]:
                name = cookie.get('name', 'unknown')
                domain = cookie.get('domain', 'unknown')
                print(f"   {name} | {domain}")
            
            if len(prime_cookies) > 5:
                print(f"   ... and {len(prime_cookies) - 5} more")
            
            print("\n✅ Prime Video cookies are available!")
            print("💡 Re-extract cookies in the UI to get them!")
            
        else:
            print("❌ No Amazon/Prime Video cookies found in Chrome")
            print("\n🤔 Possible reasons:")
            print("   1. You're not logged in to Prime Video")
            print("   2. Chrome hasn't saved the cookies to disk yet")
            print("   3. You're using a different browser (not Chrome)")
            print("   4. Cookies are in a different Chrome profile")
            print("\n💡 Try:")
            print("   1. Make sure you're logged in to Prime Video in Chrome")
            print("   2. Close and reopen Chrome (forces cookie save)")
            print("   3. Or just browse Prime Video for a bit longer")
            print("   4. Then re-extract cookies")
    
    except Exception as e:
        print(f"❌ Error accessing Chrome cookies: {e}")
        print("\n💡 Make sure:")
        print("   1. Chrome is installed")
        print("   2. You have Chrome cookies")
        print("   3. Chrome is not running (close it first)")

except ImportError:
    print("❌ rookiepy not installed")
    print("Run: pip install rookiepy")

