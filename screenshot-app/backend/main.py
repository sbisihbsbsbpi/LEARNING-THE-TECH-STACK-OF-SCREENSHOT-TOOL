"""
FastAPI Backend for Screenshot Tool
Handles screenshot capture, quality checks, and document generation
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware  # ⚡ OPTIMIZATION: Response compression
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict
import asyncio
import json
from datetime import datetime
import os
from pathlib import Path
from uuid import uuid4
from cachetools import TTLCache

from screenshot_service import ScreenshotService
from document_service import DocumentService
from quality_checker import QualityChecker
from logging_config import setup_logging, log_request_start, log_request_complete, log_cancellation
from config import settings  # ✅ PHASE 3: Centralized configuration
from cookie_extractor import CookieExtractor  # 🍪 Cookie management

# ✅ FIXED: Structured logging instead of print statements
logger = setup_logging(__name__)

app = FastAPI(title="Screenshot Tool API")

# ⚡ OPTIMIZATION: Enable GZip compression for responses (60-80% size reduction)
# Compresses responses larger than 1000 bytes (1KB)
# Automatic decompression by browser - zero frontend changes needed
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ✅ PHASE 3: CORS configuration from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # ✅ From config.py
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Services
screenshot_service = ScreenshotService()
document_service = DocumentService()
quality_checker = QualityChecker()
cookie_extractor = CookieExtractor()  # 🍪 Cookie management

# ✅ FIXED: Request-scoped cancellation tracking with TTL to prevent memory leaks
# Key: request_id (UUID), Value: {"cancelled": bool}
# TTL: 1 hour (3600 seconds) - automatically removes old entries
cancellation_contexts: TTLCache = TTLCache(maxsize=1000, ttl=3600)

# ✅ SECURITY: Path validation helper
def validate_screenshot_path(file_path: str) -> Path:
    """
    Validate file path to prevent directory traversal attacks.
    Ensures path is within screenshots directory.

    Args:
        file_path: Requested file path

    Returns:
        Validated Path object

    Raises:
        HTTPException: If path is invalid or outside allowed directory
    """
    try:
        # Resolve absolute paths
        requested_path = Path(file_path).resolve()
        screenshots_dir = settings.screenshots_dir.resolve()  # ✅ PHASE 3: From config

        # Check if path is within allowed directory
        if not requested_path.is_relative_to(screenshots_dir):
            raise ValueError("Path outside screenshots directory")

        # Check if file exists
        if not requested_path.exists():
            raise ValueError("File not found")

        return requested_path
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file path: {str(e)}"
        )

# Models
class URLRequest(BaseModel):
    urls: List[str]
    viewport_width: int = Field(default=1920, ge=800, le=7680, description="Viewport width (800-7680)")
    viewport_height: int = Field(default=1080, ge=600, le=4320, description="Viewport height (600-4320)")
    capture_mode: str = "viewport"  # "viewport", "fullpage", "segmented"
    use_stealth: bool = False
    use_real_browser: bool = False
    browser_engine: str = "playwright"  # "playwright" or "camoufox"
    base_url: str = ""  # Base URL for screenshot naming
    words_to_remove: str = ""  # Comma-separated words to remove from naming
    cookies: Optional[str] = ""  # JSON string of cookies for authentication
    local_storage: Optional[str] = ""  # JSON string of localStorage data for authentication
    # Advanced segmented settings
    segment_overlap: int = Field(default=20, ge=0, le=50, description="Percentage overlap (0-50%)")
    segment_scroll_delay: int = Field(default=1000, ge=0, le=10000, description="Scroll delay in ms (0-10000)")
    segment_max_segments: int = Field(default=50, ge=1, le=200, description="Max segments (1-200)")
    segment_skip_duplicates: bool = True  # Skip duplicate segments
    segment_smart_lazy_load: bool = True  # Wait for lazy-loaded content
    # ✅ NEW: Network event tracking
    track_network: bool = False  # Capture HTTP requests during page load
    # ✅ NEW: Per-request batch timeout
    batch_timeout: Optional[int] = Field(default=90, ge=10, le=300, description="Batch timeout in seconds (10-300)")
    # ✅ NEW: Max parallel URLs per text box (for Real Browser Mode)
    max_parallel_urls: int = Field(default=5, ge=1, le=10, description="Max parallel URLs (1-10, Real Browser Mode only)")

    @validator('urls')
    def validate_urls(cls, v):
        """
        ✅ SECURITY: Validate URLs to prevent SSRF and DoS attacks
        """
        if not v:
            raise ValueError('URL list cannot be empty')
        if len(v) > 500:
            raise ValueError('Too many URLs (max 500 per request)')

        for url in v:
            # Check protocol
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid URL protocol (must be http:// or https://): {url}')

            # Check length
            if len(url) > 2048:
                raise ValueError(f'URL too long (max 2048 characters): {url[:100]}...')

            # Block dangerous protocols
            dangerous_patterns = ['file://', 'javascript:', 'data:', 'ftp://', 'file:', 'localhost', '127.0.0.1', '0.0.0.0']
            url_lower = url.lower()
            for pattern in dangerous_patterns:
                if pattern in url_lower and not url_lower.startswith('http'):
                    raise ValueError(f'Dangerous URL pattern detected: {pattern}')

        return v

class ScreenshotResult(BaseModel):
    url: str
    status: str  # "success", "failed", "pending"
    screenshot_path: Optional[str] = None
    screenshot_paths: Optional[List[str]] = None  # For segmented captures
    segment_count: Optional[int] = None  # Number of segments captured
    error: Optional[str] = None
    quality_score: Optional[float] = None
    quality_issues: Optional[List[str]] = None
    timestamp: str

class DocumentRequest(BaseModel):
    screenshot_paths: List[str]
    output_path: str
    title: str = "Screenshot Report"

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        ✅ FIXED: Safe disconnect with error handling
        """
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            logger.warning("Attempted to remove WebSocket that was not in active connections")

    async def send_message(self, message: dict):
        """
        ✅ FIXED: Specific exception handling instead of bare except
        """
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except (WebSocketDisconnect, RuntimeError, Exception) as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                dead_connections.append(connection)

        # Remove dead connections
        for conn in dead_connections:
            try:
                self.active_connections.remove(conn)
            except ValueError:
                pass

manager = ConnectionManager()

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info("🚀 Screenshot Tool API starting up...")
    logger.info(f"📁 Output directory: {Path('screenshots').resolve()}")
    logger.info(f"🔐 Auth state file: {Path('auth_state.json').resolve()}")
    logger.info(f"🌐 CORS allowed origins: {settings.allowed_origins_list}")
    logger.info("💡 Performance docs auto-generate only when batch timeout changes")

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("🛑 Screenshot Tool API shutting down...")

# Routes
@app.get("/")
async def root():
    return {
        "name": "Screenshot Tool API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

def _group_urls_by_domain(urls: List[str]) -> Dict[str, List[str]]:
    """
    Group URLs by domain for smart batch processing.

    Returns:
        Dict mapping domain to list of URLs
    """
    from urllib.parse import urlparse

    domain_groups = {}
    for url in urls:
        try:
            domain = urlparse(url).netloc
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append(url)
        except Exception:
            # If URL parsing fails, treat as unique domain
            domain_groups[url] = [url]

    return domain_groups

def _create_smart_batches(urls: List[str], enable_batch: bool = True, max_parallel: int = 5, use_real_browser: bool = False) -> List[List[str]]:
    """
    Create smart batches based on domain detection and user settings.

    - Different domains: Process ALL URLs in parallel (unlimited batch size)
    - Same domain: Process ALL URLs in parallel (unlimited batch size)
    - Real Browser Mode: Use max_parallel setting (user-configurable)
    - Batch disabled: Batch size 1 (sequential)

    Args:
        urls: List of URLs to batch
        enable_batch: Whether to enable batch processing
        max_parallel: Maximum parallel URLs (for Real Browser Mode)
        use_real_browser: Whether using Real Browser Mode

    Returns:
        List of batches (each batch is a list of URLs)
    """
    if not enable_batch or not screenshot_service.ENABLE_BATCH_PROCESSING:
        # Sequential processing - one URL at a time
        return [[url] for url in urls]

    # ✅ NEW: For Real Browser Mode, use user-configured max_parallel setting
    if use_real_browser:
        # Create batches of max_parallel size
        batches = []
        for i in range(0, len(urls), max_parallel):
            batch = urls[i:i+max_parallel]
            batches.append(batch)
        return batches

    # Group URLs by domain (for headless mode)
    domain_groups = _group_urls_by_domain(urls)

    batches = []
    for domain, domain_urls in domain_groups.items():
        # Determine batch size based on domain
        if len(domain_urls) > 1:
            # Same domain - use smaller batch size to avoid rate limits
            batch_size = screenshot_service.SAME_DOMAIN_BATCH_SIZE
        else:
            # Different domains - use larger batch size
            batch_size = screenshot_service.DEFAULT_BATCH_SIZE

        # Create batches for this domain
        for i in range(0, len(domain_urls), batch_size):
            batch = domain_urls[i:i+batch_size]
            batches.append(batch)

    return batches

async def _capture_single_url(
    url: str,
    request: URLRequest,
    request_id: str,
    index: int,
    total: int,
    semaphore: asyncio.Semaphore
) -> ScreenshotResult:
    """
    Capture a single URL with semaphore-based concurrency control.

    Args:
        url: URL to capture
        request: URLRequest with capture settings
        request_id: Unique request ID for cancellation tracking
        index: URL index (for progress reporting)
        total: Total number of URLs
        semaphore: Semaphore for limiting concurrent captures

    Returns:
        ScreenshotResult with capture outcome
    """
    async with semaphore:
        # Check cancellation before starting
        if cancellation_contexts[request_id]["cancelled"]:
            return ScreenshotResult(
                url=url,
                status="cancelled",
                error="Operation cancelled by user",
                timestamp=datetime.now().isoformat()
            )

        try:
            # Send progress update
            await manager.send_message({
                "type": "progress",
                "current": index + 1,
                "total": total,
                "url": url,
                "status": "capturing",
                "request_id": request_id
            })

            # ✅ NEW: Use per-request batch_timeout if provided, otherwise use mode-based defaults
            if request.batch_timeout:
                capture_timeout = float(request.batch_timeout)
            elif request.use_real_browser:
                capture_timeout = 90.0  # Increased from 60s to 90s for height stabilization
            elif request.browser_engine == "camoufox":
                capture_timeout = 120.0  # Camoufox needs more time for first launch (downloads Firefox)
            elif request.use_stealth:
                capture_timeout = 90.0  # Increased for stealth mode
            elif request.capture_mode == "segmented":
                capture_timeout = 120.0
            else:
                capture_timeout = 35.0

            # Capture screenshot
            try:
                # ✅ NEW: Convert timeout to milliseconds for screenshot
                screenshot_timeout_ms = int(capture_timeout * 1000)

                if request.capture_mode == "segmented":
                    screenshot_paths = await asyncio.wait_for(
                        screenshot_service.capture_segmented(
                            url=url,
                            viewport_width=request.viewport_width,
                            viewport_height=request.viewport_height,
                            screenshot_timeout=screenshot_timeout_ms,  # ✅ NEW: Pass screenshot timeout
                            use_stealth=request.use_stealth,
                            use_real_browser=request.use_real_browser,
                            browser_engine=request.browser_engine,
                            base_url=request.base_url,
                            words_to_remove=request.words_to_remove,
                            cookies=request.cookies,
                            local_storage=request.local_storage,
                            overlap_percent=request.segment_overlap,
                            scroll_delay_ms=request.segment_scroll_delay,
                            max_segments=request.segment_max_segments,
                            skip_duplicates=request.segment_skip_duplicates,
                            smart_lazy_load=request.segment_smart_lazy_load,
                            track_network=request.track_network  # ✅ NEW: Pass network tracking setting
                        ),
                        timeout=capture_timeout
                    )
                    screenshot_path = screenshot_paths[0] if screenshot_paths else None
                else:
                    full_page = request.capture_mode == "fullpage"
                    screenshot_path = await asyncio.wait_for(
                        screenshot_service.capture(
                            url=url,
                            viewport_width=request.viewport_width,
                            viewport_height=request.viewport_height,
                            full_page=full_page,
                            screenshot_timeout=screenshot_timeout_ms,  # ✅ NEW: Pass screenshot timeout
                            use_stealth=request.use_stealth,
                            use_real_browser=request.use_real_browser,
                            browser_engine=request.browser_engine,
                            base_url=request.base_url,
                            words_to_remove=request.words_to_remove,
                            cookies=request.cookies,
                            local_storage=request.local_storage,
                            track_network=request.track_network  # ✅ NEW: Pass network tracking setting
                        ),
                        timeout=capture_timeout
                    )
                    screenshot_paths = None
            except asyncio.TimeoutError:
                mode = "real browser" if request.use_real_browser else "headless"
                raise Exception(f"Screenshot capture timed out after {capture_timeout}s ({mode} mode)")

            # Check cancellation after capture
            if cancellation_contexts[request_id]["cancelled"]:
                raise Exception("Operation cancelled by user")

            # Quality check
            quality_result = await quality_checker.check(screenshot_path)

            return ScreenshotResult(
                url=url,
                status="success" if quality_result["passed"] else "failed",
                screenshot_path=screenshot_path,
                screenshot_paths=screenshot_paths,
                segment_count=len(screenshot_paths) if screenshot_paths else None,
                quality_score=quality_result["score"],
                quality_issues=quality_result["issues"],
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            # Check if this was a cancellation
            if cancellation_contexts[request_id]["cancelled"] or "cancelled by user" in str(e).lower():
                return ScreenshotResult(
                    url=url,
                    status="cancelled",
                    error="Operation cancelled by user",
                    timestamp=datetime.now().isoformat()
                )
            else:
                # 🔍 DEBUG: Log the actual error
                logger.error(f"❌ Screenshot failed for {url}: {str(e)}")
                logger.error(f"   Error type: {type(e).__name__}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")

                return ScreenshotResult(
                    url=url,
                    status="failed",
                    error=str(e),
                    timestamp=datetime.now().isoformat()
                )


@app.post("/api/screenshots/capture")
async def capture_screenshots(request: URLRequest):
    """
    Capture screenshots for multiple URLs with smart batch processing.

    ⚡ OPTIMIZATION: Unlimited batch processing (process ALL URLs in parallel!)
    - Different domains: Process ALL URLs at once (unlimited batch size)
    - Same domain: Process ALL URLs at once (unlimited batch size)
    - Real Browser Mode: Sequential (1 at a time)
    - Feature flag: Set ENABLE_BATCH_PROCESSING = False to disable

    ✅ Backward compatible: Falls back to sequential if batch disabled
    """
    # ✅ FIXED: Create request-scoped cancellation flag with unique ID
    request_id = str(uuid4())
    cancellation_contexts[request_id] = {"cancelled": False}

    # ✅ FIXED: Log request start
    log_request_start(request_id, len(request.urls))
    start_time = datetime.now()

    # 🔍 DEBUG: Log base URL and words to remove
    logger.info(f"🔍 BASE URL RECEIVED: '{request.base_url}'")
    logger.info(f"🔍 WORDS TO REMOVE: '{request.words_to_remove}'")
    logger.info(f"🔍 URLS RECEIVED: {request.urls}")

    # ⚡ OPTIMIZATION: Create smart batches
    # Auto-detect: 1 URL = sequential, 2+ URLs = batch processing
    # This works in both Real Browser Mode and Headless Mode
    enable_batch = len(request.urls) > 1
    batches = _create_smart_batches(
        request.urls,
        enable_batch,
        max_parallel=request.max_parallel_urls,  # ✅ NEW: User-configurable
        use_real_browser=request.use_real_browser
    )

    if enable_batch and screenshot_service.ENABLE_BATCH_PROCESSING:
        logger.info(f"⚡ Smart batch processing enabled: {len(batches)} batches for {len(request.urls)} URLs")
        if request.use_real_browser:
            logger.info(f"   🌐 Real Browser Mode: Will open up to {request.max_parallel_urls} tabs at once")
    else:
        logger.info(f"📋 Sequential processing: {len(request.urls)} URLs")

    try:
        results = []
        url_index = 0

        # Process each batch
        for batch_num, batch in enumerate(batches, 1):
            # Check cancellation before each batch
            if cancellation_contexts[request_id]["cancelled"]:
                break

            if len(batch) > 1:
                logger.info(f"🚀 Processing batch {batch_num}/{len(batches)} ({len(batch)} URLs in parallel)...")

            # Create tasks for this batch
            batch_tasks = [
                _capture_single_url(
                    url, request, request_id,
                    url_index + i, len(request.urls),
                    asyncio.Semaphore(len(batch))  # Allow all URLs in batch to run in parallel
                )
                for i, url in enumerate(batch)
            ]

            # Execute batch in parallel
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            url_index += len(batch)

            # Send result updates for this batch
            for result in batch_results:
                await manager.send_message({
                    "type": "result",
                    "result": result.model_dump(),
                    "request_id": request_id
                })

        # ✅ FIXED: Log request completion
        duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results if r.status == "success")
        log_request_complete(request_id, success_count, len(request.urls), duration)

        return {
            "results": results,
            "cancelled": cancellation_contexts[request_id]["cancelled"],
            "request_id": request_id
        }

    finally:
        # ✅ FIXED: Cleanup request-scoped cancellation flag
        cancellation_contexts.pop(request_id, None)


@app.post("/api/screenshots/capture-sequential")
async def capture_screenshots_sequential(request: URLRequest):
    """
    Capture screenshots for multiple URLs sequentially (legacy endpoint).
    Use /api/screenshots/capture for parallel processing.
    """
    # ✅ FIXED: Create request-scoped cancellation flag with unique ID
    request_id = str(uuid4())
    cancellation_contexts[request_id] = {"cancelled": False}

    # ✅ FIXED: Log request start
    log_request_start(request_id, len(request.urls))
    start_time = datetime.now()

    results = []

    try:
        for i, url in enumerate(request.urls):
            # Check if operation was cancelled
            if cancellation_contexts[request_id]["cancelled"]:
                # Add remaining URLs as cancelled
                for remaining_url in request.urls[i:]:
                    results.append(ScreenshotResult(
                        url=remaining_url,
                        status="cancelled",
                        error="Operation cancelled by user",
                        timestamp=datetime.now().isoformat()
                    ))

                # ✅ FIXED: Log cancellation
                log_cancellation(request_id, i, len(request.urls))

                # Send cancellation message
                await manager.send_message({
                    "type": "cancelled",
                    "message": "Screenshot capture cancelled",
                    "completed": i,
                    "total": len(request.urls),
                    "request_id": request_id
                })
                break

            try:
                # Send progress update
                await manager.send_message({
                    "type": "progress",
                    "current": i + 1,
                    "total": len(request.urls),
                    "url": url,
                    "status": "capturing",
                    "request_id": request_id
                })

                # Check cancellation before starting capture
                if cancellation_contexts[request_id]["cancelled"]:
                    raise Exception("Operation cancelled by user")

                # Capture screenshot with timeout
                # Use longer timeout for real browser mode and stealth mode (needs more time to load)
                if request.use_real_browser:
                    capture_timeout = 90.0  # Real browser mode - increased from 60s to 90s for height stabilization
                elif request.browser_engine == "camoufox":
                    capture_timeout = 120.0  # Camoufox needs more time for first launch (downloads Firefox)
                elif request.use_stealth:
                    capture_timeout = 90.0  # Stealth mode (Cloudflare challenges take time)
                elif request.capture_mode == "segmented":
                    capture_timeout = 120.0  # Segmented mode (needs more time for multiple captures)
                else:
                    capture_timeout = 35.0  # Normal headless mode

                try:
                    # Handle different capture modes
                    if request.capture_mode == "segmented":
                        # Segmented capture returns list of paths
                        screenshot_paths = await asyncio.wait_for(
                            screenshot_service.capture_segmented(
                                url=url,
                                viewport_width=request.viewport_width,
                                viewport_height=request.viewport_height,
                                use_stealth=request.use_stealth,
                                use_real_browser=request.use_real_browser,
                                base_url=request.base_url,
                                words_to_remove=request.words_to_remove,
                                cookies=request.cookies,
                                local_storage=request.local_storage,
                                overlap_percent=request.segment_overlap,
                                scroll_delay_ms=request.segment_scroll_delay,
                                max_segments=request.segment_max_segments,
                                skip_duplicates=request.segment_skip_duplicates,
                                smart_lazy_load=request.segment_smart_lazy_load
                            ),
                            timeout=capture_timeout
                        )
                        screenshot_path = screenshot_paths[0] if screenshot_paths else None
                    else:
                        # Regular capture (viewport or fullpage)
                        full_page = request.capture_mode == "fullpage"
                        screenshot_path = await asyncio.wait_for(
                            screenshot_service.capture(
                                url=url,
                                viewport_width=request.viewport_width,
                                viewport_height=request.viewport_height,
                                full_page=full_page,
                                use_stealth=request.use_stealth,
                                use_real_browser=request.use_real_browser,
                                base_url=request.base_url,
                                words_to_remove=request.words_to_remove,
                                cookies=request.cookies,
                                local_storage=request.local_storage
                            ),
                            timeout=capture_timeout
                        )
                        screenshot_paths = None
                except asyncio.TimeoutError:
                    mode = "real browser" if request.use_real_browser else "headless"
                    raise Exception(f"Screenshot capture timed out after {capture_timeout}s ({mode} mode)")

                # Check cancellation after capture
                if cancellation_contexts[request_id]["cancelled"]:
                    raise Exception("Operation cancelled by user")

                # Quality check (use first screenshot for segmented mode)
                quality_result = await quality_checker.check(screenshot_path)

                result = ScreenshotResult(
                    url=url,
                    status="success" if quality_result["passed"] else "failed",
                    screenshot_path=screenshot_path,
                    screenshot_paths=screenshot_paths,
                    segment_count=len(screenshot_paths) if screenshot_paths else None,
                    quality_score=quality_result["score"],
                    quality_issues=quality_result["issues"],
                    timestamp=datetime.now().isoformat()
                )

            except Exception as e:
                # Check if this was a cancellation
                if cancellation_contexts[request_id]["cancelled"] or "cancelled by user" in str(e).lower():
                    result = ScreenshotResult(
                        url=url,
                        status="cancelled",
                        error="Operation cancelled by user",
                        timestamp=datetime.now().isoformat()
                    )
                else:
                    result = ScreenshotResult(
                        url=url,
                        status="failed",
                        error=str(e),
                        timestamp=datetime.now().isoformat()
                    )

            results.append(result)

            # Send result update
            await manager.send_message({
                "type": "result",
                "result": result.model_dump(),
                "request_id": request_id
            })

        # ✅ FIXED: Log request completion
        duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results if r.status == "success")
        log_request_complete(request_id, success_count, len(request.urls), duration)

        return {
            "results": results,
            "cancelled": cancellation_contexts[request_id]["cancelled"],
            "request_id": request_id
        }

    finally:
        # ✅ FIXED: Cleanup request-scoped cancellation flag
        cancellation_contexts.pop(request_id, None)

@app.post("/api/screenshots/cancel")
async def cancel_screenshots(request_id: Optional[str] = None):
    """Cancel ongoing screenshot capture operation"""
    # ✅ FIXED: Cancel specific request or all requests
    if request_id and request_id in cancellation_contexts:
        cancellation_contexts[request_id]["cancelled"] = True
        return {
            "status": "success",
            "message": f"Cancellation requested for request {request_id}"
        }
    elif not request_id:
        # Cancel all active requests (backward compatibility)
        for ctx in cancellation_contexts.values():
            ctx["cancelled"] = True
        return {
            "status": "success",
            "message": f"Cancellation requested for {len(cancellation_contexts)} active request(s)"
        }
    else:
        return {
            "status": "not_found",
            "message": "Request not found or already completed"
        }

@app.get("/api/screenshots/file/{file_path:path}")
async def get_screenshot_file(file_path: str):
    """Serve screenshot file for preview"""
    # ✅ FIXED: Validate path to prevent directory traversal
    validated_path = validate_screenshot_path(file_path)
    return FileResponse(str(validated_path))

@app.post("/api/screenshots/open-file")
async def open_file(path: str):
    """Open a screenshot file in the default image viewer"""
    import subprocess
    import platform

    # ✅ FIXED: Validate path to prevent directory traversal
    validated_path = validate_screenshot_path(path)

    try:
        # Open file based on OS
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(validated_path)])
        elif system == "Windows":
            os.startfile(str(validated_path))
        else:  # Linux
            subprocess.run(["xdg-open", str(validated_path)])

        return {"status": "success", "message": "File opened"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/screenshots/open-folder")
async def open_folder(path: str):
    """Open the folder containing the screenshot file"""
    import subprocess
    import platform

    # ✅ FIXED: Validate path to prevent directory traversal
    validated_path = validate_screenshot_path(path)
    folder_path = validated_path.parent

    try:
        # Open folder based on OS
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(folder_path)])
        elif system == "Windows":
            os.startfile(str(folder_path))
        else:  # Linux
            subprocess.run(["xdg-open", str(folder_path)])

        return {"status": "success", "message": "Folder opened"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/screenshots/retry")
async def retry_screenshot(url: str, viewport_width: int = 1920, viewport_height: int = 1080):
    """Retry capturing a single screenshot"""
    try:
        screenshot_path = await screenshot_service.capture(
            url=url,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            full_page=True
        )

        quality_result = await quality_checker.check(screenshot_path)

        return ScreenshotResult(
            url=url,
            status="success" if quality_result["passed"] else "failed",
            screenshot_path=screenshot_path,
            quality_score=quality_result["score"],
            quality_issues=quality_result["issues"],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return ScreenshotResult(
            url=url,
            status="failed",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/document/generate")
async def generate_document(request: DocumentRequest):
    """Generate Word document from screenshots"""
    try:
        output_path = await document_service.generate(
            screenshot_paths=request.screenshot_paths,
            output_path=request.output_path,
            title=request.title
        )

        return {
            "status": "success",
            "output_path": output_path
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

@app.post("/api/update-batch-timeout")
async def update_batch_timeout(request: dict):
    """
    Update batch timeout in performance_metrics.py and regenerate docs
    Only regenerates if the value actually changed
    """
    try:
        timeout = request.get("timeout")
        if timeout is None:
            return {"status": "error", "message": "Missing timeout parameter"}

        # Validate timeout
        if not isinstance(timeout, (int, float)) or timeout < 10 or timeout > 300:
            return {"status": "error", "message": "Timeout must be between 10 and 300 seconds"}

        # Read current metrics
        from performance_metrics import metrics
        current_timeout = metrics.batch_timeout

        # Check if value changed
        if abs(current_timeout - timeout) < 0.1:  # Float comparison with tolerance
            logger.info(f"⏱️ Batch timeout unchanged ({timeout}s), skipping doc generation")
            return {
                "status": "success",
                "message": "Timeout unchanged, no update needed",
                "changed": False
            }

        # Update performance_metrics.py
        metrics_file = Path(__file__).parent / "performance_metrics.py"
        content = metrics_file.read_text()

        # Replace the batch_timeout value
        import re
        new_content = re.sub(
            r'batch_timeout:\s*float\s*=\s*[\d.]+',
            f'batch_timeout: float = {timeout}',
            content
        )

        metrics_file.write_text(new_content)
        logger.info(f"⏱️ Updated batch_timeout: {current_timeout}s → {timeout}s")

        # Regenerate documentation
        from generate_docs import main as generate_docs
        generate_docs(verbose=False)
        logger.info("📊 Performance documentation regenerated")

        return {
            "status": "success",
            "message": f"Batch timeout updated from {current_timeout}s to {timeout}s",
            "changed": True,
            "old_value": current_timeout,
            "new_value": timeout
        }

    except Exception as e:
        logger.error(f"❌ Failed to update batch timeout: {e}")
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time progress updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Storage state file path
STORAGE_STATE_FILE = Path("auth_state.json")

class LoginRequest(BaseModel):
    url: str
    browser_engine: str = "playwright"  # "playwright" or "camoufox"

@app.post("/api/auth/start-login")
async def start_login(request: LoginRequest):
    """
    Open a browser window for manual login and save storage state
    """
    try:
        # Use screenshot service to open browser and wait for login
        # Pass browser_engine to determine which browser to use
        await screenshot_service.save_auth_state(
            request.url,
            str(STORAGE_STATE_FILE),
            browser_engine=request.browser_engine
        )

        return JSONResponse({
            "status": "success",
            "message": "Auth state saved successfully!",
            "file": str(STORAGE_STATE_FILE)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/status")
async def get_auth_status():
    """
    Check if saved auth state exists and get details
    """
    if STORAGE_STATE_FILE.exists():
        try:
            with open(STORAGE_STATE_FILE, 'r') as f:
                state = json.load(f)

            # Get basic info
            cookies = state.get('cookies', [])
            cookie_count = len(cookies)
            origins = state.get('origins', [])

            # Get localStorage count and items
            ls_count = 0
            ls_items = []
            for origin in origins:
                origin_ls = origin.get('localStorage', [])
                ls_count += len(origin_ls)
                ls_items.extend(origin_ls)

            # Extract auth-related cookies (for preview)
            auth_keywords = ['token', 'auth', 'session', 'sid', 'jsession', 'jwt', 'bearer', 'user', 'login']
            auth_cookies = []
            for cookie in cookies:
                name_lower = cookie.get('name', '').lower()
                if any(keyword in name_lower for keyword in auth_keywords):
                    auth_cookies.append({
                        'name': cookie.get('name'),
                        'domain': cookie.get('domain'),
                        'expires': cookie.get('expires', -1)
                    })

            # Extract auth-related localStorage items (for preview)
            auth_ls_items = []
            for item in ls_items:
                name_lower = item.get('name', '').lower()
                if any(keyword in name_lower for keyword in auth_keywords):
                    value = item.get('value', '')
                    # Truncate long values
                    truncated_value = value[:100] + '...' if len(value) > 100 else value
                    auth_ls_items.append({
                        'name': item.get('name'),
                        'value': truncated_value
                    })

            return JSONResponse({
                "exists": True,
                "cookie_count": cookie_count,
                "localStorage_count": ls_count,
                "cookies": auth_cookies[:10],  # Limit to 10 for preview
                "localStorage_items": auth_ls_items[:10],  # Limit to 10 for preview
                "file": str(STORAGE_STATE_FILE),
                "file_size": STORAGE_STATE_FILE.stat().st_size
            })
        except Exception as e:
            return JSONResponse({
                "exists": False,
                "error": str(e)
            })
    else:
        return JSONResponse({
            "exists": False
        })

@app.delete("/api/auth/clear")
async def clear_auth_state():
    """
    Delete saved auth state
    """
    try:
        if STORAGE_STATE_FILE.exists():
            STORAGE_STATE_FILE.unlink()
            return JSONResponse({
                "status": "success",
                "message": "Auth state cleared"
            })
        else:
            return JSONResponse({
                "status": "success",
                "message": "No auth state to clear"
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/save-from-extension")
async def save_auth_from_extension(storage_state: dict):
    """Save auth state from Chrome extension"""
    try:
        # Save to auth_state.json
        with open(STORAGE_STATE_FILE, 'w') as f:
            json.dump(storage_state, f, indent=2)

        # Get stats
        cookie_count = len(storage_state.get('cookies', []))
        ls_count = sum(len(origin.get('localStorage', [])) for origin in storage_state.get('origins', []))

        print(f"✅ Auth state saved from Chrome extension!")
        print(f"   📊 Cookies: {cookie_count}")
        print(f"   📊 localStorage items: {ls_count}")

        return {
            "success": True,
            "message": "Auth state saved successfully",
            "cookie_count": cookie_count,
            "localStorage_count": ls_count
        }
    except Exception as e:
        print(f"❌ Failed to save auth state from extension: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 🍪 COOKIE MANAGEMENT ENDPOINTS
# ========================================

class CookieExtractionRequest(BaseModel):
    """Request model for cookie extraction"""
    domains: Optional[List[str]] = None  # List of domains to extract (e.g., ["zomato.com"])
    browser: str = "auto"  # "chrome", "firefox", "edge", "safari", "brave", "opera", "auto"
    engine: str = "playwright"  # "playwright" or "camoufox"

@app.post("/api/cookies/extract")
async def extract_cookies(request: CookieExtractionRequest):
    """
    Extract cookies from browser and save for use in screenshots

    Supports both Playwright (Chromium) and Camoufox (Firefox)
    """
    try:
        logger.info(f"🍪 Extracting cookies for {request.engine}")
        logger.info(f"   Browser: {request.browser}, Domains: {request.domains}")

        if request.engine == "playwright":
            # Extract for Playwright (Chromium-based)
            result = cookie_extractor.extract_and_save_for_playwright(
                domains=request.domains,
                preferred_browser=request.browser if request.browser != "auto" else "chrome"
            )
        elif request.engine == "camoufox":
            # Extract for Camoufox (Firefox-based)
            result = cookie_extractor.extract_and_save_for_camoufox(
                domains=request.domains
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid engine: {request.engine}")

        if result["success"]:
            logger.info(f"✅ Cookies extracted successfully!")
            logger.info(f"   Source: {result['source_browser']}, Count: {result.get('cookie_count', 0)}")
            return result
        else:
            logger.error(f"❌ Cookie extraction failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

    except Exception as e:
        logger.error(f"❌ Cookie extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cookies/browsers")
async def detect_browsers():
    """
    Detect which browsers are available on the system
    """
    try:
        browsers = cookie_extractor.detect_available_browsers()

        available = [name for name, status in browsers.items() if status]

        logger.info(f"🔍 Browser detection complete")
        logger.info(f"   Available: {', '.join(available) if available else 'None'}")

        return {
            "browsers": browsers,
            "available": available,
            "recommended_playwright": "chrome" if browsers.get("chrome") else (
                "edge" if browsers.get("edge") else "any"
            ),
            "recommended_camoufox": "firefox" if browsers.get("firefox") else "any"
        }
    except Exception as e:
        logger.error(f"❌ Browser detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cookies/status")
async def get_cookie_status():
    """
    Get status of saved cookies for both Playwright and Camoufox
    """
    try:
        # Check Playwright storage state
        playwright_storage = cookie_extractor.load_playwright_storage_state()
        playwright_status = {
            "exists": playwright_storage is not None,
            "cookie_count": len(playwright_storage.get("cookies", [])) if playwright_storage else 0,
            "extracted_at": playwright_storage.get("metadata", {}).get("extracted_at") if playwright_storage else None
        }

        # Check Camoufox profile
        camoufox_stats = cookie_extractor.validate_camoufox_profile(
            str(cookie_extractor.camoufox_profile)
        )

        return {
            "playwright": playwright_status,
            "camoufox": camoufox_stats
        }
    except Exception as e:
        logger.error(f"❌ Cookie status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cookies/clear")
async def clear_cookies(engine: str = "all"):
    """
    Clear saved cookies

    Args:
        engine: "playwright", "camoufox", or "all"
    """
    try:
        cleared = []

        if engine in ["playwright", "all"]:
            # Clear Playwright storage state
            if cookie_extractor.playwright_storage.exists():
                cookie_extractor.playwright_storage.unlink()
                cleared.append("playwright")
                logger.info("🧹 Cleared Playwright cookies")

        if engine in ["camoufox", "all"]:
            # Clear Camoufox profile
            if cookie_extractor.camoufox_profile.exists():
                import shutil
                shutil.rmtree(cookie_extractor.camoufox_profile)
                cleared.append("camoufox")
                logger.info("🧹 Cleared Camoufox profile")

        return {
            "success": True,
            "cleared": cleared,
            "message": f"Cleared cookies for: {', '.join(cleared)}"
        }
    except Exception as e:
        logger.error(f"❌ Cookie clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cookies/analyze")
async def analyze_cookies(domain: str = None, auth_only: bool = False):
    """
    Analyze extracted cookies and return statistics

    Args:
        domain: Optional domain filter (e.g., "zomato")
        auth_only: If true, return only auth cookies
    """
    try:
        from collections import defaultdict

        # Load cookies
        storage_file = Path("browser_sessions/playwright_storage_state.json")
        if not storage_file.exists():
            return {
                "success": False,
                "error": "No cookies found. Extract cookies first."
            }

        with open(storage_file, 'r') as f:
            data = json.load(f)

        cookies = data.get('cookies', [])

        # Filter by domain
        if domain:
            cookies = [c for c in cookies if domain.lower() in c.get('domain', '').lower()]

        # Filter auth cookies
        def is_auth_cookie(cookie):
            name = cookie.get('name', '').lower()
            auth_keywords = ['token', 'session', 'auth', 'sid', 'jsession', 'login', 'user', 'jwt', 'bearer', 'csrf', 'xsrf']
            return any(keyword in name for keyword in auth_keywords)

        if auth_only:
            cookies = [c for c in cookies if is_auth_cookie(c)]

        # Group by domain
        by_domain = defaultdict(int)
        for cookie in cookies:
            domain_name = cookie.get('domain', 'unknown')
            by_domain[domain_name] += 1

        # Count statistics
        secure_count = sum(1 for c in cookies if c.get('secure', False))
        httponly_count = sum(1 for c in cookies if c.get('httpOnly', False))
        session_count = sum(1 for c in cookies if c.get('expires') in [-1, None])

        # Get auth cookies
        auth_cookies = [c for c in cookies if is_auth_cookie(c)]

        # Top domains
        top_domains = sorted(by_domain.items(), key=lambda x: x[1], reverse=True)[:10]

        # Format auth cookies for display
        auth_cookies_display = []
        for cookie in auth_cookies[:20]:  # Limit to 20
            auth_cookies_display.append({
                'name': cookie.get('name', ''),
                'value': cookie.get('value', ''),
                'domain': cookie.get('domain', ''),
                'path': cookie.get('path', '/'),
                'expires': cookie.get('expires'),
                'secure': cookie.get('secure', False),
                'httpOnly': cookie.get('httpOnly', False),
                'sameSite': cookie.get('sameSite', 'None'),
                'partitioned': cookie.get('partitioned', False)
            })

        return {
            "success": True,
            "total": len(cookies),
            "unique_domains": len(by_domain),
            "secure_count": secure_count,
            "httponly_count": httponly_count,
            "session_count": session_count,
            "auth_count": len(auth_cookies),
            "top_domains": [{"domain": d, "count": c} for d, c in top_domains],
            "auth_cookies": auth_cookies_display,
            "all_cookies": cookies if len(cookies) <= 100 else cookies[:100]  # Limit to 100 for performance
        }

    except Exception as e:
        logger.error(f"❌ Cookie analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/cookies/update")
async def update_cookie(cookie: dict):
    """
    Update a specific cookie in the saved cookies file

    Args:
        cookie: Cookie object with name, domain, value, etc.
    """
    try:
        # Load existing cookies from Playwright storage state
        playwright_cookies_file = Path("cookies_playwright.json")

        if not playwright_cookies_file.exists():
            raise HTTPException(status_code=404, detail="No cookies file found")

        with open(playwright_cookies_file, 'r') as f:
            storage_state = json.load(f)

        cookies = storage_state.get('cookies', [])

        # Find and update the cookie
        updated = False
        for i, c in enumerate(cookies):
            if c['name'] == cookie['name'] and c['domain'] == cookie['domain']:
                # Update the cookie while preserving structure
                cookies[i] = {
                    'name': cookie.get('name', c['name']),
                    'value': cookie.get('value', c['value']),
                    'domain': cookie.get('domain', c['domain']),
                    'path': cookie.get('path', c.get('path', '/')),
                    'expires': cookie.get('expires', c.get('expires', -1)),
                    'httpOnly': cookie.get('httpOnly', c.get('httpOnly', False)),
                    'secure': cookie.get('secure', c.get('secure', False)),
                    'sameSite': cookie.get('sameSite', c.get('sameSite', 'Lax')),
                    'partitioned': cookie.get('partitioned', c.get('partitioned', False))
                }
                updated = True
                break

        if not updated:
            raise HTTPException(status_code=404, detail=f"Cookie '{cookie['name']}' not found")

        # Save updated cookies
        storage_state['cookies'] = cookies
        with open(playwright_cookies_file, 'w') as f:
            json.dump(storage_state, f, indent=2)

        logger.info(f"✅ Cookie updated: {cookie['name']} for {cookie['domain']}")

        return JSONResponse({
            "success": True,
            "message": f"Cookie '{cookie['name']}' updated successfully"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Cookie update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cookies/delete")
async def delete_cookie(cookie: dict):
    """
    Delete a specific cookie from the saved cookies file

    Args:
        cookie: Object with 'name' and 'domain' to identify the cookie
    """
    try:
        # Load existing cookies from Playwright storage state
        playwright_cookies_file = Path("cookies_playwright.json")

        if not playwright_cookies_file.exists():
            raise HTTPException(status_code=404, detail="No cookies file found")

        with open(playwright_cookies_file, 'r') as f:
            storage_state = json.load(f)

        cookies = storage_state.get('cookies', [])
        original_count = len(cookies)

        # Filter out the cookie to delete
        cookies = [c for c in cookies if not (c['name'] == cookie['name'] and c['domain'] == cookie['domain'])]

        if len(cookies) == original_count:
            raise HTTPException(status_code=404, detail=f"Cookie '{cookie['name']}' not found")

        # Save updated cookies
        storage_state['cookies'] = cookies
        with open(playwright_cookies_file, 'w') as f:
            json.dump(storage_state, f, indent=2)

        logger.info(f"✅ Cookie deleted: {cookie['name']} for {cookie['domain']}")

        return JSONResponse({
            "success": True,
            "message": f"Cookie '{cookie['name']}' deleted successfully",
            "remaining_cookies": len(cookies)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Cookie delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/network/export-curl")
async def export_network_events_as_curl(request: dict):
    """
    Export captured network events as cURL commands

    Request body:
    {
        "network_events": [...]  # Array of network events
    }

    Returns:
    {
        "success": true,
        "curl_commands": [...],
        "count": 5,
        "file": "/path/to/curl_commands.sh"
    }
    """
    try:
        network_events = request.get('network_events', [])

        if not network_events:
            return {
                "success": False,
                "error": "No network events provided"
            }

        # Convert to cURL commands
        curl_commands = screenshot_service._convert_network_events_to_curl(network_events)

        if not curl_commands:
            return {
                "success": False,
                "error": "No API calls found in network events"
            }

        # Save to file
        curl_file = Path("screenshots/curl_commands.sh")
        curl_file.parent.mkdir(exist_ok=True)

        with open(curl_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# cURL commands exported from network events\n")
            f.write("# Generated by Screenshot Tool\n\n")
            for i, curl in enumerate(curl_commands, 1):
                f.write(f"# Request {i}\n")
                f.write(f"{curl}\n\n")

        return {
            "success": True,
            "curl_commands": curl_commands,
            "count": len(curl_commands),
            "file": str(curl_file)
        }

    except Exception as e:
        logger.error(f"❌ Export cURL error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/restart")
async def restart_backend():
    """
    Restart the backend server
    This endpoint triggers a server restart by touching the main.py file,
    which causes uvicorn's reload feature to restart the server.
    """
    try:
        import sys
        import signal

        logger.info("🔄 Backend restart requested")

        # Touch the main.py file to trigger uvicorn reload
        main_file = Path(__file__)
        main_file.touch()

        logger.info("✅ Backend restart triggered")

        return JSONResponse({
            "status": "success",
            "message": "Backend is restarting..."
        })
    except Exception as e:
        logger.error(f"❌ Failed to restart backend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/launch-debug-chrome")
async def launch_debug_chrome():
    """
    Launch Chrome with remote debugging enabled
    This endpoint runs the launcher script that opens Chrome with all profiles
    """
    try:
        import subprocess
        import os

        logger.info("🔴 Debug Chrome launch requested")

        # Path to the launcher script
        launcher_path = os.path.expanduser(
            "~/Library/Application Support/Google/Chrome-Debug/🔴 CLICK HERE TO LAUNCH DEBUG CHROME.command"
        )

        # Check if launcher exists
        if not os.path.exists(launcher_path):
            logger.error(f"❌ Launcher not found at: {launcher_path}")
            raise HTTPException(
                status_code=404,
                detail="Debug Chrome launcher not found. Please run setup-all-chrome-profiles.sh first."
            )

        # Check if Chrome is already running with remote debugging
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 9222))
            sock.close()

            if result == 0:
                logger.info("✅ Chrome already running with remote debugging on port 9222")
                return JSONResponse({
                    "status": "already_running",
                    "message": "Chrome is already running with remote debugging enabled",
                    "port": 9222
                })
        except Exception as e:
            logger.warning(f"⚠️ Error checking Chrome status: {str(e)}")

        # Launch Chrome in background
        logger.info(f"🚀 Launching debug Chrome from: {launcher_path}")

        # Run the launcher script in background
        subprocess.Popen(
            ["bash", launcher_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        logger.info("✅ Debug Chrome launch command sent")

        return JSONResponse({
            "status": "success",
            "message": "Debug Chrome is launching...",
            "port": 9222
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to launch debug Chrome: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

