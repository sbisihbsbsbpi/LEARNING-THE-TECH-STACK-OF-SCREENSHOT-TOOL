"""
Integration Tests for Screenshot Tool
Tests end-to-end workflows and integration between components
"""

import pytest
import asyncio
import json
from pathlib import Path
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from screenshot_service import ScreenshotService
from quality_checker import QualityChecker

client = TestClient(app)

# ============================================
# TEST SUITE 1: End-to-End Workflows
# ============================================

class TestEndToEndWorkflows:
    """Test complete workflows from request to response"""
    
    @pytest.mark.asyncio
    async def test_complete_capture_workflow(self):
        """Test complete screenshot capture workflow"""
        # 1. Capture screenshot
        service = ScreenshotService()
        try:
            screenshot_path = await service.capture(
                url="https://example.com",
                viewport_width=1920,
                viewport_height=1080,
                full_page=False
            )
            
            assert screenshot_path is not None
            assert Path(screenshot_path).exists()
            
            # 2. Check quality
            checker = QualityChecker()
            quality_result = await checker.check(screenshot_path)
            
            assert "passed" in quality_result
            assert "score" in quality_result
            assert quality_result["score"] >= 0
            
            # 3. Cleanup
            Path(screenshot_path).unlink()
        finally:
            await service.close()
    
    @pytest.mark.asyncio
    async def test_batch_capture_workflow(self):
        """Test batch screenshot capture workflow"""
        urls = [
            "https://example.com",
            "https://httpbin.org/html"
        ]
        
        service = ScreenshotService()
        results = []
        
        try:
            for url in urls:
                screenshot_path = await service.capture(
                    url=url,
                    viewport_width=1920,
                    viewport_height=1080
                )
                results.append(screenshot_path)
            
            assert len(results) == len(urls)
            for path in results:
                assert path is not None
                assert Path(path).exists()
                Path(path).unlink()
        finally:
            await service.close()

# ============================================
# TEST SUITE 2: Error Recovery
# ============================================

class TestErrorRecovery:
    """Test error handling and recovery"""
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling for slow pages"""
        service = ScreenshotService()
        try:
            # Use a URL that might timeout
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    service.capture(
                        url="https://httpbin.org/delay/60",
                        viewport_width=1920,
                        viewport_height=1080
                    ),
                    timeout=5.0
                )
        finally:
            await service.close()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors"""
        service = ScreenshotService()
        try:
            with pytest.raises(Exception):
                await service.capture(
                    url="https://this-domain-does-not-exist-12345.com",
                    viewport_width=1920,
                    viewport_height=1080
                )
        finally:
            await service.close()

# ============================================
# TEST SUITE 3: Performance Tests
# ============================================

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_capture_performance(self):
        """Test screenshot capture performance"""
        import time
        
        service = ScreenshotService()
        try:
            start_time = time.time()
            
            screenshot_path = await service.capture(
                url="https://example.com",
                viewport_width=1920,
                viewport_height=1080,
                full_page=False
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time (60 seconds)
            assert duration < 60.0
            
            if screenshot_path and Path(screenshot_path).exists():
                Path(screenshot_path).unlink()
        finally:
            await service.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_captures(self):
        """Test concurrent screenshot captures"""
        service = ScreenshotService()
        
        async def capture_url(url):
            return await service.capture(
                url=url,
                viewport_width=1920,
                viewport_height=1080
            )
        
        try:
            urls = [
                "https://example.com",
                "https://httpbin.org/html"
            ]
            
            # Capture concurrently
            results = await asyncio.gather(
                *[capture_url(url) for url in urls],
                return_exceptions=True
            )
            
            # At least some should succeed
            successful = [r for r in results if not isinstance(r, Exception)]
            assert len(successful) > 0
            
            # Cleanup
            for path in successful:
                if path and Path(path).exists():
                    Path(path).unlink()
        finally:
            await service.close()

# ============================================
# TEST SUITE 4: Configuration Tests
# ============================================

class TestConfiguration:
    """Test configuration and settings"""
    
    def test_settings_loaded(self):
        """Test that settings are loaded correctly"""
        from config import settings
        
        assert settings.screenshots_dir is not None
        assert settings.auth_state_file is not None
        assert settings.allowed_origins_list is not None
    
    def test_directories_exist(self):
        """Test that required directories exist"""
        from config import settings
        
        # Screenshots directory should be created
        assert settings.screenshots_dir.exists()

# ============================================
# TEST SUITE 5: Stealth Features
# ============================================

class TestStealthFeatures:
    """Test stealth mode features"""
    
    @pytest.mark.asyncio
    async def test_stealth_mode_enabled(self):
        """Test stealth mode can be enabled"""
        service = ScreenshotService()
        try:
            screenshot_path = await service.capture(
                url="https://example.com",
                viewport_width=1920,
                viewport_height=1080,
                use_stealth=True
            )
            
            assert screenshot_path is not None
            if Path(screenshot_path).exists():
                Path(screenshot_path).unlink()
        finally:
            await service.close()
    
    @pytest.mark.asyncio
    async def test_browser_engine_selection(self):
        """Test browser engine selection"""
        service = ScreenshotService()
        try:
            # Test Playwright
            screenshot_path = await service.capture(
                url="https://example.com",
                browser_engine="playwright"
            )
            assert screenshot_path is not None
            if Path(screenshot_path).exists():
                Path(screenshot_path).unlink()
            
            # Test Camoufox (should fallback to Playwright if not available)
            screenshot_path = await service.capture(
                url="https://example.com",
                browser_engine="camoufox"
            )
            assert screenshot_path is not None
            if Path(screenshot_path).exists():
                Path(screenshot_path).unlink()
        finally:
            await service.close()

# ============================================
# TEST SUITE 6: Quality Checking
# ============================================

class TestQualityChecking:
    """Test quality checking functionality"""
    
    @pytest.mark.asyncio
    async def test_quality_check_valid_screenshot(self):
        """Test quality check on valid screenshot"""
        # First capture a screenshot
        service = ScreenshotService()
        try:
            screenshot_path = await service.capture(
                url="https://example.com",
                viewport_width=1920,
                viewport_height=1080
            )
            
            # Check quality
            checker = QualityChecker()
            result = await checker.check(screenshot_path)
            
            assert "passed" in result
            assert "score" in result
            assert "issues" in result
            assert result["score"] >= 0
            
            # Cleanup
            if Path(screenshot_path).exists():
                Path(screenshot_path).unlink()
        finally:
            await service.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

