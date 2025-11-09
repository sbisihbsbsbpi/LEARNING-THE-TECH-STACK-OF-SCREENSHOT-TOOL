#!/usr/bin/env python3
"""
Cookie Analyzer - Inspect and analyze extracted cookies

Usage:
    python3 analyze_cookies.py                    # Show summary
    python3 analyze_cookies.py --domain zomato    # Filter by domain
    python3 analyze_cookies.py --auth             # Show only auth cookies
    python3 analyze_cookies.py --all              # Show all cookies
    python3 analyze_cookies.py --export csv       # Export to CSV
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse


def load_cookies(filepath="browser_sessions/playwright_storage_state.json"):
    """Load cookies from storage state file"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Cookie file not found: {filepath}")
        print(f"   Run cookie extraction first!")
        return None
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    return data.get('cookies', [])


def format_timestamp(timestamp):
    """Convert Unix timestamp to readable date"""
    if timestamp == -1 or timestamp is None:
        return "Session"
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "Invalid"


def is_auth_cookie(cookie):
    """Check if cookie is likely an authentication cookie"""
    name = cookie.get('name', '').lower()
    auth_keywords = ['token', 'session', 'auth', 'sid', 'jsession', 'login', 'user', 'jwt', 'bearer', 'csrf', 'xsrf']
    return any(keyword in name for keyword in auth_keywords)


def analyze_cookies(cookies, domain_filter=None, auth_only=False):
    """Analyze cookies and return statistics"""
    if not cookies:
        return None
    
    # Filter cookies
    filtered = cookies
    if domain_filter:
        filtered = [c for c in cookies if domain_filter.lower() in c.get('domain', '').lower()]
    if auth_only:
        filtered = [c for c in filtered if is_auth_cookie(c)]
    
    # Group by domain
    by_domain = defaultdict(list)
    for cookie in filtered:
        domain = cookie.get('domain', 'unknown')
        by_domain[domain].append(cookie)
    
    # Count secure/httpOnly
    secure_count = sum(1 for c in filtered if c.get('secure', False))
    httponly_count = sum(1 for c in filtered if c.get('httpOnly', False))
    session_count = sum(1 for c in filtered if c.get('expires') in [-1, None])
    
    # Find auth cookies
    auth_cookies = [c for c in filtered if is_auth_cookie(c)]
    
    return {
        'total': len(filtered),
        'by_domain': dict(by_domain),
        'secure_count': secure_count,
        'httponly_count': httponly_count,
        'session_count': session_count,
        'auth_cookies': auth_cookies,
        'domains': sorted(by_domain.keys())
    }


def print_summary(stats):
    """Print cookie summary"""
    if not stats:
        return
    
    print("\n" + "="*80)
    print("🍪 COOKIE ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\n📊 Statistics:")
    print(f"   Total Cookies: {stats['total']}")
    print(f"   Unique Domains: {len(stats['domains'])}")
    print(f"   Secure Cookies: {stats['secure_count']} ({stats['secure_count']/stats['total']*100:.1f}%)")
    print(f"   HttpOnly Cookies: {stats['httponly_count']} ({stats['httponly_count']/stats['total']*100:.1f}%)")
    print(f"   Session Cookies: {stats['session_count']} ({stats['session_count']/stats['total']*100:.1f}%)")
    print(f"   Auth Cookies: {len(stats['auth_cookies'])}")
    
    print(f"\n🌐 Top 10 Domains by Cookie Count:")
    domain_counts = [(domain, len(cookies)) for domain, cookies in stats['by_domain'].items()]
    domain_counts.sort(key=lambda x: x[1], reverse=True)
    for i, (domain, count) in enumerate(domain_counts[:10], 1):
        print(f"   {i:2d}. {domain:40s} ({count:3d} cookies)")
    
    if stats['auth_cookies']:
        print(f"\n🔑 Authentication Cookies ({len(stats['auth_cookies'])}):")
        for cookie in stats['auth_cookies'][:20]:  # Show first 20
            name = cookie.get('name', '')
            domain = cookie.get('domain', '')
            expires = format_timestamp(cookie.get('expires'))
            secure = "🔒" if cookie.get('secure') else "  "
            httponly = "🚫" if cookie.get('httpOnly') else "  "
            print(f"   {secure}{httponly} {name:30s} | {domain:30s} | Expires: {expires}")
        
        if len(stats['auth_cookies']) > 20:
            print(f"   ... and {len(stats['auth_cookies']) - 20} more")


def print_all_cookies(cookies, domain_filter=None):
    """Print all cookies in detail"""
    filtered = cookies
    if domain_filter:
        filtered = [c for c in cookies if domain_filter.lower() in c.get('domain', '').lower()]
    
    print("\n" + "="*80)
    print(f"🍪 ALL COOKIES ({len(filtered)} total)")
    print("="*80)
    
    for i, cookie in enumerate(filtered, 1):
        print(f"\n[{i}] {cookie.get('name', 'UNNAMED')}")
        print(f"    Domain:   {cookie.get('domain', 'N/A')}")
        print(f"    Path:     {cookie.get('path', '/')}")
        print(f"    Value:    {cookie.get('value', '')[:50]}{'...' if len(cookie.get('value', '')) > 50 else ''}")
        print(f"    Expires:  {format_timestamp(cookie.get('expires'))}")
        print(f"    Secure:   {'✅' if cookie.get('secure') else '❌'}")
        print(f"    HttpOnly: {'✅' if cookie.get('httpOnly') else '❌'}")
        print(f"    SameSite: {cookie.get('sameSite', 'None')}")


def export_to_csv(cookies, output_file="cookies.csv"):
    """Export cookies to CSV file"""
    import csv
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'name', 'value', 'domain', 'path', 'expires', 'expires_readable',
            'secure', 'httpOnly', 'sameSite', 'is_auth'
        ])
        writer.writeheader()
        
        for cookie in cookies:
            writer.writerow({
                'name': cookie.get('name', ''),
                'value': cookie.get('value', ''),
                'domain': cookie.get('domain', ''),
                'path': cookie.get('path', '/'),
                'expires': cookie.get('expires', -1),
                'expires_readable': format_timestamp(cookie.get('expires')),
                'secure': cookie.get('secure', False),
                'httpOnly': cookie.get('httpOnly', False),
                'sameSite': cookie.get('sameSite', 'None'),
                'is_auth': is_auth_cookie(cookie)
            })
    
    print(f"✅ Exported {len(cookies)} cookies to {output_file}")


def search_cookies(cookies, search_term):
    """Search cookies by name, domain, or value"""
    search_term = search_term.lower()
    results = []
    
    for cookie in cookies:
        if (search_term in cookie.get('name', '').lower() or
            search_term in cookie.get('domain', '').lower() or
            search_term in cookie.get('value', '').lower()):
            results.append(cookie)
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Analyze extracted cookies')
    parser.add_argument('--domain', '-d', help='Filter by domain (e.g., zomato, google)')
    parser.add_argument('--auth', '-a', action='store_true', help='Show only auth cookies')
    parser.add_argument('--all', action='store_true', help='Show all cookies in detail')
    parser.add_argument('--export', '-e', choices=['csv'], help='Export to format')
    parser.add_argument('--search', '-s', help='Search cookies by name/domain/value')
    parser.add_argument('--file', '-f', default='browser_sessions/playwright_storage_state.json',
                       help='Cookie file path')
    
    args = parser.parse_args()
    
    # Load cookies
    cookies = load_cookies(args.file)
    if not cookies:
        return 1
    
    print(f"📁 Loaded {len(cookies)} cookies from {args.file}")
    
    # Search mode
    if args.search:
        results = search_cookies(cookies, args.search)
        print(f"\n🔍 Search results for '{args.search}': {len(results)} cookies found")
        print_all_cookies(results)
        return 0
    
    # Export mode
    if args.export == 'csv':
        filtered = cookies
        if args.domain:
            filtered = [c for c in cookies if args.domain.lower() in c.get('domain', '').lower()]
        if args.auth:
            filtered = [c for c in filtered if is_auth_cookie(c)]
        
        filename = f"cookies_{args.domain if args.domain else 'all'}.csv"
        export_to_csv(filtered, filename)
        return 0
    
    # Show all mode
    if args.all:
        print_all_cookies(cookies, args.domain)
        return 0
    
    # Default: show summary
    stats = analyze_cookies(cookies, args.domain, args.auth)
    print_summary(stats)
    
    print("\n" + "="*80)
    print("💡 Tips:")
    print("   • Use --domain to filter by domain: python3 analyze_cookies.py --domain zomato")
    print("   • Use --auth to see only auth cookies: python3 analyze_cookies.py --auth")
    print("   • Use --all to see all cookies: python3 analyze_cookies.py --all")
    print("   • Use --search to search: python3 analyze_cookies.py --search token")
    print("   • Use --export csv to export: python3 analyze_cookies.py --export csv")
    print("="*80 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

