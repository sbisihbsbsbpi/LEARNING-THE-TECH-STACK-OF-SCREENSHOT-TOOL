"""
Quick script to analyze auth_state.json contents
"""

import json
from pathlib import Path
from datetime import datetime

auth_state_path = Path("auth_state.json")

with open(auth_state_path, 'r') as f:
    auth_state = json.load(f)

print("=" * 80)
print("🔍 AUTH STATE ANALYSIS")
print("=" * 80)

# Cookies
cookies = auth_state.get('cookies', [])
print(f"\n📋 COOKIES ({len(cookies)} total):")
print("-" * 80)
for cookie in cookies:
    name = cookie['name']
    domain = cookie['domain']
    expires = cookie.get('expires', -1)
    
    if expires == -1:
        expires_str = "Session"
    else:
        try:
            expires_dt = datetime.fromtimestamp(expires)
            expires_str = expires_dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            expires_str = str(expires)
    
    value_preview = cookie['value'][:50] + "..." if len(cookie['value']) > 50 else cookie['value']
    print(f"  ✅ {name:20s} | {domain:35s} | Expires: {expires_str}")
    if name in ['JSESSIONID', 'idx', 'DT', 'tcookie']:
        print(f"     Value: {value_preview}")

# LocalStorage
print(f"\n💾 LOCALSTORAGE:")
print("-" * 80)
for origin in auth_state.get('origins', []):
    origin_url = origin['origin']
    ls_items = origin.get('localStorage', [])
    print(f"\n  Origin: {origin_url}")
    print(f"  Items: {len(ls_items)}")
    print()
    
    # Critical auth tokens
    critical_tokens = ['t_token', 't_user', 'dse_t_user', 'currentActiveDealerId', 
                       'currentActiveRoleId', 'currentActivePersona']
    
    for item in ls_items:
        name = item['name']
        value = item['value']
        
        if name in critical_tokens:
            value_preview = value[:80] + "..." if len(value) > 80 else value
            print(f"  🔑 {name:30s} | {value_preview}")
        else:
            print(f"  📝 {name:30s} | {len(value)} chars")

# Check JWT token expiry
print(f"\n🔐 JWT TOKEN ANALYSIS:")
print("-" * 80)
for origin in auth_state.get('origins', []):
    for item in origin.get('localStorage', []):
        if item['name'] == 't_token':
            token = item['value']
            # Decode JWT (just the payload, no verification)
            try:
                import base64
                parts = token.split('.')
                if len(parts) == 3:
                    # Add padding if needed
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.b64decode(payload)
                    payload_json = json.loads(decoded)
                    
                    print(f"  Token Issuer: {payload_json.get('iss', 'N/A')}")
                    print(f"  User ID: {payload_json.get('userId', 'N/A')}")
                    print(f"  Email: {payload_json.get('email', 'N/A')}")
                    
                    exp = payload_json.get('exp')
                    if exp:
                        exp_dt = datetime.fromtimestamp(exp)
                        now = datetime.now()
                        if exp_dt > now:
                            time_left = exp_dt - now
                            print(f"  ✅ Expires: {exp_dt.strftime('%Y-%m-%d %H:%M:%S')} ({time_left.total_seconds() / 3600:.1f} hours left)")
                        else:
                            print(f"  ❌ EXPIRED: {exp_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"  ⚠️  Could not decode JWT: {e}")

# Check tcookie
print(f"\n🍪 TCOOKIE ANALYSIS:")
print("-" * 80)
for cookie in cookies:
    if cookie['name'] == 'tcookie':
        import urllib.parse
        tcookie_decoded = urllib.parse.unquote(cookie['value'])
        try:
            tcookie_json = json.loads(tcookie_decoded)
            print(f"  Role ID: {tcookie_json.get('roleId', 'N/A')}")
            print(f"  User ID: {tcookie_json.get('userId', 'N/A')}")
            print(f"  Tenant: {tcookie_json.get('tenantname', 'N/A')}")
            print(f"  Dealer ID: {tcookie_json.get('dealerId', 'N/A')}")
            print(f"  Site ID: {tcookie_json.get('tek-siteId', 'N/A')}")
            print(f"  Locale: {tcookie_json.get('locale', 'N/A')}")
            print(f"  Application: {tcookie_json.get('applicationId', 'N/A')}")
        except Exception as e:
            print(f"  ⚠️  Could not decode tcookie: {e}")

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)

