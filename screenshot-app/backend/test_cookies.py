import json
import time

# Load auth state
with open('auth_state.json', 'r') as f:
    state = json.load(f)

print("=" * 80)
print("🔍 COOKIE ANALYSIS")
print("=" * 80)

cookies = state.get('cookies', [])
print(f"\n📊 Total cookies: {len(cookies)}\n")

# Group by domain
by_domain = {}
for cookie in cookies:
    domain = cookie.get('domain', 'unknown')
    if domain not in by_domain:
        by_domain[domain] = []
    by_domain[domain].append(cookie)

# Analyze each domain
for domain, domain_cookies in by_domain.items():
    print(f"\n🌐 Domain: {domain}")
    print(f"   📊 Cookies: {len(domain_cookies)}")
    
    for cookie in domain_cookies:
        name = cookie['name']
        expires = cookie.get('expires', -1)
        secure = cookie.get('secure', False)
        sameSite = cookie.get('sameSite', 'N/A')
        
        # Check if expired
        if expires == -1:
            expiry_status = "🔵 Session"
        elif expires < time.time():
            expiry_status = "❌ EXPIRED"
        else:
            days_left = int((expires - time.time()) / 86400)
            expiry_status = f"✅ Valid ({days_left} days)"
        
        # Check if auth-related
        is_auth = any(keyword in name.lower() for keyword in ['token', 'session', 'auth', 'sid', 'jsession'])
        auth_marker = "🔑" if is_auth else "  "
        
        print(f"   {auth_marker} {name}: secure={secure}, sameSite={sameSite}, {expiry_status}")

print("\n" + "=" * 80)
print("🎯 DIAGNOSIS")
print("=" * 80)

preprod_cookies = by_domain.get('preprodapp.tekioncloud.com', [])
employee_cookies = by_domain.get('employee.tekion.com', [])

print(f"\n✅ Cookies for preprodapp.tekioncloud.com: {len(preprod_cookies)}")
print(f"⚠️  Cookies for employee.tekion.com: {len(employee_cookies)}")

print("\n💡 ISSUE:")
print("   When navigating to preprodapp.tekioncloud.com, Playwright will ONLY send")
print("   cookies for that domain. The employee.tekion.com cookies (including")
print("   JSESSIONID) will NOT be sent, causing authentication to fail!")

print("\n🔧 SOLUTION:")
print("   The app needs to handle cross-domain authentication properly, OR")
print("   we need to use Real Browser Mode which handles this automatically.")

