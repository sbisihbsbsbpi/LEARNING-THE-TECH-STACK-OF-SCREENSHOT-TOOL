"""
🍪 Cookie Extractor - Best-in-Class Cookie Management
Supports both Playwright (Chromium) and Camoufox (Firefox)

Features:
- Automatic browser detection
- Intelligent fallback chains
- Cross-browser compatibility
- Cookie validation and expiry checking
- Secure storage state management
- Comprehensive error handling
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import shutil

# Try to import rookiepy (best option)
try:
    import rookiepy
    ROOKIEPY_AVAILABLE = True
    print("✅ rookiepy available - Best cookie extraction enabled!")
except ImportError:
    ROOKIEPY_AVAILABLE = False
    print("⚠️  rookiepy not installed. Install with: pip install rookiepy")
    print("   Falling back to manual cookie management...")


class CookieExtractor:
    """
    Best-in-class cookie extractor with support for:
    - Playwright (Chromium-based: Patchright, Rebrowser)
    - Camoufox (Firefox-based)
    - All major browsers (Chrome, Firefox, Edge, Safari, Brave, Opera)
    """
    
    def __init__(self, storage_dir: str = "browser_sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage state files
        self.playwright_storage = self.storage_dir / "playwright_storage_state.json"
        self.camoufox_profile = self.storage_dir / "camoufox_profile"
        
        print(f"🍪 Cookie Extractor initialized")
        print(f"   📁 Storage directory: {self.storage_dir}")
    
    # ========================================
    # BROWSER DETECTION
    # ========================================
    
    def detect_available_browsers(self) -> Dict[str, bool]:
        """
        Detect which browsers are available on the system
        
        Returns:
            Dict with browser names and availability status
        """
        if not ROOKIEPY_AVAILABLE:
            return {"error": "rookiepy not installed"}
        
        browsers = {
            "chrome": False,
            "firefox": False,
            "edge": False,
            "safari": False,
            "brave": False,
            "opera": False
        }
        
        # Try to extract from each browser (empty domain list = quick check)
        for browser_name in browsers.keys():
            try:
                method = getattr(rookiepy, browser_name, None)
                if method:
                    # Try to get cookies (will fail if browser not installed)
                    method([])
                    browsers[browser_name] = True
            except Exception:
                pass
        
        return browsers
    
    # ========================================
    # COOKIE EXTRACTION - PLAYWRIGHT (CHROMIUM)
    # ========================================
    
    def extract_for_playwright(
        self,
        domains: Optional[List[str]] = None,
        preferred_browser: str = "chrome"
    ) -> Tuple[List[Dict], str]:
        """
        Extract cookies optimized for Playwright (Chromium-based)
        
        Fallback chain:
        1. Preferred browser (default: Chrome)
        2. Edge (Chromium-based)
        3. Brave (Chromium-based)
        4. Any available browser
        
        Args:
            domains: List of domains to extract cookies for (e.g., ["zomato.com"])
            preferred_browser: Preferred browser to extract from
        
        Returns:
            Tuple of (cookies list, source browser name)
        """
        if not ROOKIEPY_AVAILABLE:
            raise ImportError("rookiepy not installed. Install with: pip install rookiepy")
        
        # Fallback chain for Chromium-based browsers
        chromium_browsers = [preferred_browser, "edge", "brave", "chrome"]
        
        for browser_name in chromium_browsers:
            try:
                method = getattr(rookiepy, browser_name, None)
                if not method:
                    continue
                
                print(f"🔍 Trying to extract cookies from {browser_name.title()}...")
                cookies = method(domains) if domains else method()
                
                if cookies:
                    print(f"✅ Extracted {len(cookies)} cookies from {browser_name.title()} (optimal for Playwright)")
                    return cookies, browser_name
            except Exception as e:
                print(f"   ⚠️  {browser_name.title()} not available: {str(e)[:50]}")
                continue
        
        # Last resort: try any browser
        try:
            print(f"🔍 Trying to extract from any available browser...")
            cookies = rookiepy.any(domains) if domains else rookiepy.any()
            if cookies:
                print(f"✅ Extracted {len(cookies)} cookies from available browser")
                return cookies, "any"
        except Exception as e:
            print(f"❌ Failed to extract cookies from any browser: {e}")
            return [], "none"
        
        return [], "none"
    
    # ========================================
    # COOKIE EXTRACTION - CAMOUFOX (FIREFOX)
    # ========================================
    
    def extract_for_camoufox(
        self,
        domains: Optional[List[str]] = None
    ) -> Tuple[List[Dict], str]:
        """
        Extract cookies optimized for Camoufox (Firefox-based)
        
        Fallback chain:
        1. Firefox (best match)
        2. Any available browser
        
        Args:
            domains: List of domains to extract cookies for
        
        Returns:
            Tuple of (cookies list, source browser name)
        """
        if not ROOKIEPY_AVAILABLE:
            raise ImportError("rookiepy not installed. Install with: pip install rookiepy")
        
        # Try Firefox first (best for Camoufox)
        try:
            print(f"🔍 Trying to extract cookies from Firefox...")
            cookies = rookiepy.firefox(domains) if domains else rookiepy.firefox()
            
            if cookies:
                print(f"✅ Extracted {len(cookies)} cookies from Firefox (optimal for Camoufox)")
                return cookies, "firefox"
        except Exception as e:
            print(f"   ⚠️  Firefox not available: {str(e)[:50]}")
        
        # Fallback: try any browser
        try:
            print(f"🔍 Trying to extract from any available browser...")
            cookies = rookiepy.any(domains) if domains else rookiepy.any()
            if cookies:
                print(f"✅ Extracted {len(cookies)} cookies from available browser")
                return cookies, "any"
        except Exception as e:
            print(f"❌ Failed to extract cookies from any browser: {e}")
            return [], "none"
        
        return [], "none"
    
    # ========================================
    # COOKIE VALIDATION
    # ========================================
    
    def validate_cookies(self, cookies: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Validate cookies and remove expired/invalid ones
        
        Returns:
            Tuple of (valid cookies, statistics)
        """
        now = int(time.time())
        valid_cookies = []
        stats = {
            "total": len(cookies),
            "valid": 0,
            "expired": 0,
            "invalid": 0
        }
        
        for cookie in cookies:
            # Check required fields
            if not cookie.get("name") or not cookie.get("value"):
                stats["invalid"] += 1
                continue
            
            # Check expiry
            expires = cookie.get("expires")
            # Skip expired cookies (but allow None/null which means session cookie)
            if expires is not None and expires != -1 and expires < now:
                stats["expired"] += 1
                continue
            
            valid_cookies.append(cookie)
            stats["valid"] += 1
        
        return valid_cookies, stats
    
    # ========================================
    # PLAYWRIGHT STORAGE STATE
    # ========================================
    
    def convert_to_playwright_format(self, cookies: List[Dict]) -> Dict:
        """
        Convert cookies to Playwright storage_state format
        
        Args:
            cookies: List of cookie dictionaries from rookiepy
        
        Returns:
            Playwright-compatible storage_state dictionary
        """
        playwright_cookies = []
        
        for cookie in cookies:
            playwright_cookie = {
                "name": cookie.get("name", ""),
                "value": cookie.get("value", ""),
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", "/"),
                "expires": cookie.get("expires", -1),
                "httpOnly": cookie.get("httpOnly", False),
                "secure": cookie.get("secure", False),
                "sameSite": cookie.get("sameSite", "Lax")
            }
            playwright_cookies.append(playwright_cookie)
        
        storage_state = {
            "cookies": playwright_cookies,
            "origins": [],
            "metadata": {
                "extracted_at": datetime.now().isoformat(),
                "cookie_count": len(playwright_cookies)
            }
        }
        
        return storage_state
    
    def save_playwright_storage_state(
        self,
        cookies: List[Dict],
        filename: Optional[str] = None
    ) -> str:
        """
        Save cookies as Playwright storage_state file
        
        Args:
            cookies: List of cookies
            filename: Optional custom filename
        
        Returns:
            Path to saved file
        """
        # Validate cookies first
        valid_cookies, stats = self.validate_cookies(cookies)
        
        print(f"📊 Cookie validation:")
        print(f"   Total: {stats['total']}, Valid: {stats['valid']}, "
              f"Expired: {stats['expired']}, Invalid: {stats['invalid']}")
        
        if not valid_cookies:
            raise ValueError("No valid cookies to save")
        
        # Convert to Playwright format
        storage_state = self.convert_to_playwright_format(valid_cookies)
        
        # Save to file
        filepath = self.storage_dir / (filename or "playwright_storage_state.json")
        with open(filepath, 'w') as f:
            json.dump(storage_state, f, indent=2)
        
        print(f"💾 Saved {len(valid_cookies)} cookies to {filepath}")
        return str(filepath)
    
    def load_playwright_storage_state(
        self,
        filename: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Load Playwright storage_state from file
        
        Args:
            filename: Optional custom filename
        
        Returns:
            Storage state dictionary or None if not found
        """
        filepath = self.storage_dir / (filename or "playwright_storage_state.json")
        
        if not filepath.exists():
            print(f"⚠️  Storage state file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                storage_state = json.load(f)
            
            # Validate cookies
            cookies = storage_state.get("cookies", [])
            valid_cookies, stats = self.validate_cookies(cookies)
            
            print(f"📂 Loaded storage state from {filepath}")
            print(f"   Valid: {stats['valid']}, Expired: {stats['expired']}")
            
            # Update with valid cookies only
            storage_state["cookies"] = valid_cookies
            
            return storage_state
        except Exception as e:
            print(f"❌ Failed to load storage state: {e}")
            return None

    # ========================================
    # CAMOUFOX PROFILE MANAGEMENT
    # ========================================

    def inject_cookies_to_camoufox_profile(
        self,
        cookies: List[Dict],
        profile_dir: Optional[str] = None
    ) -> str:
        """
        Inject cookies directly into Camoufox profile's cookies.sqlite

        Note: This is an ALTERNATIVE to persistent_context.
        Your current persistent_context implementation is better!
        Use this only if you need manual cookie injection.

        Args:
            cookies: List of cookies to inject
            profile_dir: Optional custom profile directory

        Returns:
            Path to profile directory
        """
        # Validate cookies first
        valid_cookies, stats = self.validate_cookies(cookies)

        print(f"📊 Cookie validation:")
        print(f"   Total: {stats['total']}, Valid: {stats['valid']}, "
              f"Expired: {stats['expired']}, Invalid: {stats['invalid']}")

        if not valid_cookies:
            raise ValueError("No valid cookies to inject")

        # Setup profile directory
        profile_path = Path(profile_dir) if profile_dir else self.camoufox_profile
        profile_path.mkdir(parents=True, exist_ok=True)

        cookies_db = profile_path / "cookies.sqlite"

        # Create cookies.sqlite database
        conn = sqlite3.connect(str(cookies_db))
        cursor = conn.cursor()

        # Create table (Firefox format)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moz_cookies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                value TEXT,
                host TEXT,
                path TEXT,
                expiry INTEGER,
                lastAccessed INTEGER,
                creationTime INTEGER,
                isSecure INTEGER,
                isHttpOnly INTEGER,
                sameSite INTEGER,
                rawSameSite INTEGER,
                schemeMap INTEGER
            )
        ''')

        # Insert cookies
        now_microseconds = int(time.time() * 1000000)

        for cookie in valid_cookies:
            # Convert sameSite to Firefox format
            same_site_map = {"None": 0, "Lax": 1, "Strict": 2}
            same_site = same_site_map.get(cookie.get("sameSite", "Lax"), 1)

            cursor.execute('''
                INSERT OR REPLACE INTO moz_cookies
                (name, value, host, path, expiry, lastAccessed, creationTime,
                 isSecure, isHttpOnly, sameSite, rawSameSite, schemeMap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cookie["name"],
                cookie["value"],
                cookie.get("domain", ""),
                cookie.get("path", "/"),
                cookie.get("expires", -1),
                now_microseconds,
                now_microseconds,
                1 if cookie.get("secure", False) else 0,
                1 if cookie.get("httpOnly", False) else 0,
                same_site,
                same_site,
                0  # schemeMap: 0 = http and https
            ))

        conn.commit()
        conn.close()

        print(f"✅ Injected {len(valid_cookies)} cookies into Camoufox profile")
        print(f"   📁 Profile: {profile_path}")

        return str(profile_path)

    def copy_camoufox_profile(
        self,
        source_profile: str,
        dest_profile: str,
        clean_dest: bool = True
    ) -> bool:
        """
        Copy Camoufox profile from source to destination

        This is useful for copying login profile to main profile
        (exactly what you're already doing!)

        Args:
            source_profile: Source profile directory
            dest_profile: Destination profile directory
            clean_dest: Whether to clean destination before copying

        Returns:
            True if successful
        """
        source_path = Path(source_profile)
        dest_path = Path(dest_profile)

        if not source_path.exists():
            print(f"❌ Source profile not found: {source_path}")
            return False

        try:
            # Clean destination if requested
            if clean_dest and dest_path.exists():
                print(f"🧹 Cleaning destination profile...")
                shutil.rmtree(dest_path)

            # Copy profile
            print(f"📋 Copying profile...")
            print(f"   From: {source_path}")
            print(f"   To: {dest_path}")

            shutil.copytree(source_path, dest_path, dirs_exist_ok=True)

            print(f"✅ Profile copied successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to copy profile: {e}")
            return False

    def validate_camoufox_profile(self, profile_dir: str) -> Dict:
        """
        Validate Camoufox profile and return statistics

        Args:
            profile_dir: Profile directory to validate

        Returns:
            Dictionary with validation results
        """
        profile_path = Path(profile_dir)

        stats = {
            "exists": profile_path.exists(),
            "has_cookies": False,
            "cookie_count": 0,
            "has_storage": False,
            "size_mb": 0
        }

        if not stats["exists"]:
            return stats

        # Check cookies.sqlite
        cookies_db = profile_path / "cookies.sqlite"
        if cookies_db.exists():
            stats["has_cookies"] = True
            try:
                conn = sqlite3.connect(str(cookies_db))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM moz_cookies")
                stats["cookie_count"] = cursor.fetchone()[0]
                conn.close()
            except Exception:
                pass

        # Check webappsstore.sqlite (localStorage)
        storage_db = profile_path / "webappsstore.sqlite"
        stats["has_storage"] = storage_db.exists()

        # Calculate total size
        total_size = sum(f.stat().st_size for f in profile_path.rglob('*') if f.is_file())
        stats["size_mb"] = round(total_size / (1024 * 1024), 2)

        return stats

    # ========================================
    # HIGH-LEVEL WORKFLOWS
    # ========================================

    def extract_and_save_for_playwright(
        self,
        domains: Optional[List[str]] = None,
        preferred_browser: str = "chrome",
        filename: Optional[str] = None
    ) -> Dict:
        """
        Complete workflow: Extract cookies and save for Playwright

        Args:
            domains: List of domains to extract
            preferred_browser: Preferred browser
            filename: Optional custom filename

        Returns:
            Dictionary with results
        """
        print(f"🚀 Starting Playwright cookie extraction workflow...")

        # Extract cookies
        cookies, source_browser = self.extract_for_playwright(domains, preferred_browser)

        if not cookies:
            return {
                "success": False,
                "error": "No cookies extracted",
                "source_browser": source_browser
            }

        # Save storage state
        try:
            filepath = self.save_playwright_storage_state(cookies, filename)

            return {
                "success": True,
                "filepath": filepath,
                "source_browser": source_browser,
                "cookie_count": len(cookies),
                "domains": list(set(c.get("domain", "") for c in cookies))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source_browser": source_browser
            }

    def extract_and_save_for_camoufox(
        self,
        domains: Optional[List[str]] = None,
        profile_dir: Optional[str] = None
    ) -> Dict:
        """
        Complete workflow: Extract cookies and save for Camoufox

        Note: Your persistent_context approach is better!
        Use this only if you need manual cookie injection.

        Args:
            domains: List of domains to extract
            profile_dir: Optional custom profile directory

        Returns:
            Dictionary with results
        """
        print(f"🚀 Starting Camoufox cookie extraction workflow...")

        # Extract cookies
        cookies, source_browser = self.extract_for_camoufox(domains)

        if not cookies:
            return {
                "success": False,
                "error": "No cookies extracted",
                "source_browser": source_browser
            }

        # Inject to profile
        try:
            profile_path = self.inject_cookies_to_camoufox_profile(cookies, profile_dir)

            return {
                "success": True,
                "profile_path": profile_path,
                "source_browser": source_browser,
                "cookie_count": len(cookies),
                "domains": list(set(c.get("domain", "") for c in cookies))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source_browser": source_browser
            }

