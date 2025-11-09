import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import "./styles.css";
import { useLocalStorage } from "./hooks/useLocalStorage";
import { useDebouncedLocalStorage } from "./hooks/useDebouncedLocalStorage";
import { ask } from "@tauri-apps/plugin-dialog";
import config, { apiUrl } from "./config"; // ✅ FIXED: Centralized configuration

interface ScreenshotResult {
  url: string;
  status: string;
  screenshot_path?: string | null;
  screenshot_paths?: string[] | null;
  segment_count?: number | null;
  error?: string | null;
  quality_score?: number | null;
  quality_issues?: string[] | null;
  timestamp: string;
}

function App() {
  // Load URLs from localStorage on mount (debounced for performance)
  const [urls, setUrls] = useDebouncedLocalStorage("screenshot-urls", "", 500);
  const [results, setResults] = useState<ScreenshotResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [logs, setLogs] = useState<string[]>([]);
  const [renderError, setRenderError] = useState<string | null>(null);

  // ✅ NEW FEATURE: Multiple text boxes for batch processing
  interface TextBox {
    id: string;
    sessionName: string;
    urls: string;
    batchTimeout?: number; // ✅ NEW: Each text box has its own timeout (optional for backward compatibility)
  }

  const [enableMultipleTextBoxes, setEnableMultipleTextBoxes] = useLocalStorage(
    "screenshot-enable-multiple-textboxes",
    true // ✅ CHECKED by default
  );

  // ✅ NEW: Parallel text box processing setting
  const [enableParallelTextBoxes, setEnableParallelTextBoxes] = useLocalStorage(
    "screenshot-enable-parallel-textboxes",
    true // ✅ CHECKED by default - process all text boxes in parallel
  );

  // ✅ NEW: Folder name for organizing Word documents
  const [wordDocFolderName, setWordDocFolderName] = useDebouncedLocalStorage(
    "screenshot-word-doc-folder-name",
    "", // Empty by default - saves directly to "ARC DEALERS SCREENSHOT WORD DOCS"
    500
  );

  const [textBoxes, setTextBoxes] = useDebouncedLocalStorage<TextBox[]>(
    "screenshot-textboxes",
    [
      { id: "textbox-1", sessionName: "", urls: "", batchTimeout: 90 },
      { id: "textbox-2", sessionName: "", urls: "", batchTimeout: 90 },
      { id: "textbox-3", sessionName: "", urls: "", batchTimeout: 90 },
    ], // ✅ Default 3 text boxes with 90s timeout each
    500
  );

  // ✅ MIGRATION: Add batchTimeout to old text boxes that don't have it
  useEffect(() => {
    const needsMigration = textBoxes.some(
      (tb) => tb.batchTimeout === undefined
    );
    if (needsMigration) {
      const migratedTextBoxes = textBoxes.map((tb) => ({
        ...tb,
        batchTimeout: tb.batchTimeout || 90, // Default to 90s if missing
      }));
      setTextBoxes(migratedTextBoxes);
    }
  }, []); // Run once on mount

  // Capture mode: "viewport", "fullpage", "segmented"
  const [captureMode, setCaptureModeState] = useLocalStorage(
    "screenshot-capturemode",
    "viewport"
  );

  const [useStealth, setUseStealthState] = useLocalStorage(
    "screenshot-stealth",
    false
  );
  const [useRealBrowser, setUseRealBrowserState] = useLocalStorage(
    "screenshot-realbrowser",
    false
  );

  // Network tracking: capture HTTP requests during page load
  const [trackNetwork, setTrackNetworkState] = useLocalStorage(
    "screenshot-track-network",
    false
  );

  // Browser engine: "playwright" or "camoufox"
  const [browserEngine, setBrowserEngineState] = useLocalStorage(
    "screenshot-browser-engine",
    "playwright"
  );

  // ✅ FIX: Wrapper functions will be defined after addLog is created
  // (moved to after addLog definition to avoid calling undefined function)

  // Base URL for screenshot naming
  const [baseUrl, setBaseUrl] = useLocalStorage("screenshot-base-url", "");

  // ✅ Word transformations for screenshot naming (enhanced with replacement support)
  interface WordTransformation {
    word: string; // The word to find (e.g., "Accounting", "dse-v2")
    replacement: string; // What to replace with: "" (remove), " " (space), or custom text
    type: "remove" | "space" | "custom"; // For UI styling and display
  }

  const [wordsToRemove, setWordsToRemove] = useDebouncedLocalStorage<
    WordTransformation[]
  >("screenshot-words-to-remove", [], 500);

  // Current input for adding new word transformation
  const [wordInput, setWordInput] = useState("");

  // ✅ Visual editor modal state
  const [showWordEditor, setShowWordEditor] = useState(false);
  const [editingWordIndex, setEditingWordIndex] = useState<number | null>(null);
  const [editorWord, setEditorWord] = useState("");
  const [editorReplacement, setEditorReplacement] = useState("");
  const [editorType, setEditorType] = useState<"remove" | "space" | "custom">(
    "space"
  );

  // Cookies for authentication (Okta, SSO, etc.) - debounced for performance
  const [cookies, setCookies] = useDebouncedLocalStorage(
    "screenshot-cookies",
    "",
    500
  );

  // localStorage data for authentication (JWT tokens, etc.) - debounced for performance
  const [localStorageData, setLocalStorageData] = useDebouncedLocalStorage(
    "screenshot-localstorage",
    "",
    500
  );

  // Saved auth state status
  const [authStateStatus, setAuthStateStatus] = useState<{
    exists: boolean;
    cookie_count?: number;
    localStorage_count?: number;
    cookies?: Array<{ name: string; domain: string; expires?: number }>;
    localStorage_items?: Array<{ name: string; value: string }>;
  }>({ exists: false });
  const [isLoginInProgress, setIsLoginInProgress] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [loginUrl, setLoginUrl] = useState(
    "https://preprodapp.tekioncloud.com/home"
  );
  const [showAuthPreview, setShowAuthPreview] = useState(false);

  // ✅ FIX: Custom confirmation dialog state (to replace browser confirm/alert)
  const [customDialog, setCustomDialog] = useState<{
    show: boolean;
    title: string;
    message: string;
    type: "alert" | "confirm";
    onConfirm?: () => void;
    onCancel?: () => void;
  }>({
    show: false,
    title: "",
    message: "",
    type: "alert",
  });

  // 🍪 Cookie import state
  const [cookieImportStatus, setCookieImportStatus] = useState<{
    playwright?: {
      exists: boolean;
      cookie_count: number;
      extracted_at?: string;
    };
    camoufox?: { exists: boolean; cookie_count: number; size_mb?: number };
  }>({});
  const [availableBrowsers, setAvailableBrowsers] = useState<string[]>([]);
  const [selectedBrowser, setSelectedBrowser] = useLocalStorage(
    "cookie-browser",
    "auto"
  );
  const [cookieDomains, setCookieDomains] = useLocalStorage(
    "cookie-domains",
    ""
  );
  const [isExtractingCookies, setIsExtractingCookies] = useState(false);

  // 🔍 Cookie analysis state
  const [cookieAnalysis, setCookieAnalysis] = useState<any>(null);
  const [isAnalyzingCookies, setIsAnalyzingCookies] = useState(false);
  const [analysisDomainFilter, setAnalysisDomainFilter] = useState("");
  const [showAuthCookiesOnly, setShowAuthCookiesOnly] = useState(false);
  const [showCookieAnalysis, setShowCookieAnalysis] = useState(false);

  // 🎯 Auth method expansion state (for button-based UI)
  const [expandedAuthMethod, setExpandedAuthMethod] = useState<string | null>(
    null
  );

  // 🍪 Cookie management state
  const [selectedCookie, setSelectedCookie] = useState<any>(null);
  const [showCookieEditor, setShowCookieEditor] = useState(false);
  const [editingCookie, setEditingCookie] = useState<any>(null);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportType, setExportType] = useState<"curl" | "playwright">("curl");
  const [exportOptions, setExportOptions] = useState({
    includeHeaders: true,
    includeMethod: true,
    includeUrl: true,
    url: "",
    method: "GET",
    prettyPrint: true,
    includeComments: false,
    explainEverything: false,
  });
  const [exportCode, setExportCode] = useState("");
  const [showSecurityAudit, setShowSecurityAudit] = useState(false);
  const [securityReport, setSecurityReport] = useState<any>(null);
  const [showFormatExport, setShowFormatExport] = useState(false);
  const [exportFormat, setExportFormat] = useState<string>("json");
  const [showFormatImport, setShowFormatImport] = useState(false);
  const [importFormat, setImportFormat] = useState<string>("json");

  // Regenerate export code when options change
  useEffect(() => {
    if (showExportModal) {
      const code =
        exportType === "curl"
          ? generateCurlCommand()
          : generatePlaywrightCode();
      setExportCode(code);
    }
  }, [exportOptions, showExportModal, exportType]);

  // Check auth state status on mount
  useEffect(() => {
    checkAuthStatus();
    checkCookieStatus();
    detectBrowsers();
  }, []);

  // ✅ Migrate old string[] format to new WordTransformation[] format (backward compatibility)
  useEffect(() => {
    const stored = localStorage.getItem("screenshot-words-to-remove");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Check if it's old format (array of strings)
        if (
          Array.isArray(parsed) &&
          parsed.length > 0 &&
          typeof parsed[0] === "string"
        ) {
          console.log(
            "🔄 Migrating old word format to new transformation format..."
          );
          const migrated: WordTransformation[] = parsed.map((word: string) => ({
            word,
            replacement: " ",
            type: "space" as const,
          }));
          setWordsToRemove(migrated);
          console.log(`✅ Migrated ${migrated.length} words to new format`);
        }
      } catch (e) {
        console.error("Failed to migrate word transformations:", e);
      }
    }
  }, []); // Run once on mount

  const checkAuthStatus = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/status");
      const data = await response.json();
      setAuthStateStatus(data);
    } catch (error) {
      console.error("Failed to check auth status:", error);
    }
  };

  // ✅ FIX: Custom dialog helpers (replace browser alert/confirm)
  const showCustomAlert = (title: string, message: string) => {
    return new Promise<void>((resolve) => {
      setCustomDialog({
        show: true,
        title,
        message,
        type: "alert",
        onConfirm: () => {
          setCustomDialog({
            show: false,
            title: "",
            message: "",
            type: "alert",
          });
          resolve();
        },
      });
    });
  };

  const showCustomConfirm = (title: string, message: string) => {
    return new Promise<boolean>((resolve) => {
      setCustomDialog({
        show: true,
        title,
        message,
        type: "confirm",
        onConfirm: () => {
          setCustomDialog({
            show: false,
            title: "",
            message: "",
            type: "alert",
          });
          resolve(true);
        },
        onCancel: () => {
          setCustomDialog({
            show: false,
            title: "",
            message: "",
            type: "alert",
          });
          resolve(false);
        },
      });
    });
  };

  // ✅ NEW: Unified notification system (replaces browser alert() and Notification API)
  // This function automatically detects the message type and shows appropriate icon/title
  const notify = (
    message: string,
    options?: {
      title?: string;
      type?: "success" | "error" | "warning" | "info";
    }
  ) => {
    // Auto-detect type from message if not specified
    let type = options?.type;
    if (!type) {
      if (message.includes("✅") || message.toLowerCase().includes("success")) {
        type = "success";
      } else if (
        message.includes("❌") ||
        message.toLowerCase().includes("error") ||
        message.toLowerCase().includes("failed")
      ) {
        type = "error";
      } else if (
        message.includes("⚠️") ||
        message.toLowerCase().includes("warning")
      ) {
        type = "warning";
      } else {
        type = "info";
      }
    }

    // Auto-generate title if not provided
    let title = options?.title;
    if (!title) {
      switch (type) {
        case "success":
          title = "✅ Success";
          break;
        case "error":
          title = "❌ Error";
          break;
        case "warning":
          title = "⚠️ Warning";
          break;
        default:
          title = "ℹ️ Information";
      }
    }

    // Show custom dialog (non-blocking, auto-resolves)
    return showCustomAlert(title, message);
  };

  // ✅ NEW: Custom alert wrapper (replaces browser alert())
  // Automatically uses notify() for all alert() calls
  const alert = (message: string) => {
    return notify(message);
  };

  const openLoginModal = () => {
    setShowLoginModal(true);
  };

  const startLogin = async () => {
    setShowLoginModal(false);
    if (!loginUrl.trim()) {
      alert("Please enter a URL");
      return;
    }

    setIsLoginInProgress(true);
    addLog("🔓 Opening browser for manual login...");
    addLog(`📍 Navigate to: ${loginUrl}`);
    addLog(
      `🌐 Browser engine: ${
        browserEngine === "camoufox"
          ? "🦊 Camoufox (with persistent profile)"
          : "🎭 Playwright"
      }`
    );
    addLog("⏳ Please log in and wait...");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/auth/start-login",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            url: loginUrl,
            browser_engine: browserEngine, // Send browser engine from settings
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        addLog("✅ Auth state saved successfully!");
        addLog(`📊 Cookies: ${authStateStatus.cookie_count || 0}`);
        addLog(`📊 localStorage: ${authStateStatus.localStorage_count || 0}`);
        alert(
          "✅ Login successful!\n\nYour auth state has been saved.\nFuture captures will automatically use this saved state."
        );
        await checkAuthStatus();
      } else {
        const error = await response.json();
        addLog(`❌ Failed to save auth state: ${error.detail}`);
        alert(`❌ Failed to save auth state:\n${error.detail}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
      alert(`❌ Error:\n${error.message}`);
    } finally {
      setIsLoginInProgress(false);
    }
  };

  // Alias for the new button-based UI
  const openLoginBrowser = () => {
    openLoginModal();
  };

  const clearAuthState = async () => {
    const confirmed = await ask(
      "Are you sure you want to clear the saved auth state?",
      { title: "Clear Auth State", type: "warning" }
    );
    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/clear", {
        method: "DELETE",
      });

      if (response.ok) {
        addLog("✅ Auth state cleared");
        alert("✅ Auth state cleared successfully!");
        await checkAuthStatus();
      } else {
        const error = await response.json();
        addLog(`❌ Failed to clear auth state: ${error.detail}`);
        alert(`❌ Failed to clear auth state:\n${error.detail}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
      alert(`❌ Error:\n${error.message}`);
    }
  };

  // 🍪 Cookie management functions
  const checkCookieStatus = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/cookies/status");
      const data = await response.json();
      setCookieImportStatus(data);
    } catch (error) {
      console.error("Failed to check cookie status:", error);
    }
  };

  const detectBrowsers = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/cookies/browsers"
      );
      const data = await response.json();
      setAvailableBrowsers(data.available || []);
    } catch (error) {
      console.error("Failed to detect browsers:", error);
    }
  };

  const extractCookies = async () => {
    setIsExtractingCookies(true);
    addLog("🍪 Extracting cookies from browser...");
    addLog(`   Browser: ${selectedBrowser}`);
    addLog(`   Engine: ${browserEngine}`);
    if (cookieDomains) {
      addLog(`   Domains: ${cookieDomains}`);
    }

    try {
      const domains = cookieDomains
        ? cookieDomains
            .split(",")
            .map((d) => d.trim())
            .filter((d) => d)
        : null;

      const response = await fetch(
        "http://127.0.0.1:8000/api/cookies/extract",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            domains,
            browser: selectedBrowser,
            engine: browserEngine,
          }),
        }
      );

      const result = await response.json();

      if (result.success) {
        addLog(`✅ Cookies extracted successfully!`);
        addLog(`   Source: ${result.source_browser}`);
        addLog(`   Count: ${result.cookie_count}`);
        if (result.domains && result.domains.length > 0) {
          addLog(`   Domains: ${result.domains.join(", ")}`);
        }
        alert(
          `✅ Cookies extracted successfully!\n\n` +
            `Source: ${result.source_browser}\n` +
            `Count: ${result.cookie_count}\n` +
            `Engine: ${browserEngine}\n\n` +
            `Future captures will automatically use these cookies!`
        );
        await checkCookieStatus();
      } else {
        addLog(`❌ Failed to extract cookies: ${result.error}`);
        alert(`❌ Failed to extract cookies:\n${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
      alert(`❌ Error:\n${error.message}`);
    } finally {
      setIsExtractingCookies(false);
    }
  };

  const clearCookies = async () => {
    const confirmed = await ask(
      "Are you sure you want to clear imported cookies?",
      { title: "Clear Cookies", type: "warning" }
    );
    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/cookies/clear?engine=${browserEngine}`,
        { method: "DELETE" }
      );

      const result = await response.json();

      if (result.success) {
        addLog(`✅ Cookies cleared for ${browserEngine}`);
        alert(`✅ Cookies cleared successfully!`);
        await checkCookieStatus();
      } else {
        addLog(`❌ Failed to clear cookies`);
        alert(`❌ Failed to clear cookies`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
      alert(`❌ Error:\n${error.message}`);
    }
  };

  const analyzeCookies = async () => {
    setIsAnalyzingCookies(true);
    addLog("🔍 Analyzing cookies...");

    try {
      const params = new URLSearchParams();
      if (analysisDomainFilter) {
        params.append("domain", analysisDomainFilter);
      }
      if (showAuthCookiesOnly) {
        params.append("auth_only", "true");
      }

      const response = await fetch(
        `http://127.0.0.1:8000/api/cookies/analyze?${params}`
      );
      const result = await response.json();

      if (result.success) {
        setCookieAnalysis(result);
        setShowCookieAnalysis(true);
        addLog(`✅ Analysis complete: ${result.total} cookies analyzed`);
      } else {
        addLog(`❌ ${result.error}`);
        alert(result.error);
      }
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
      alert(`❌ Error:\n${error.message}`);
    } finally {
      setIsAnalyzingCookies(false);
    }
  };

  // 🍪 Cookie Management Functions
  const viewCookie = (cookie: any) => {
    setSelectedCookie(cookie);
    setEditingCookie({ ...cookie });
    setShowCookieEditor(true);
  };

  const updateCookie = async () => {
    if (!editingCookie) return;

    try {
      const response = await fetch("http://127.0.0.1:8000/api/cookies/update", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editingCookie),
      });

      if (response.ok) {
        addLog(`✅ Cookie updated: ${editingCookie.name}`);
        setShowCookieEditor(false);
        await analyzeCookies(); // Refresh the analysis
        await checkCookieStatus(); // Refresh cookie status
      } else {
        const error = await response.json();
        addLog(`❌ Failed to update cookie: ${error.detail}`);
        alert(`❌ Failed to update cookie:\n${error.detail}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
      alert(`❌ Error:\n${error.message}`);
    }
  };

  const deleteCookie = async (cookie: any) => {
    // ✅ FIX: Use browser confirm directly (more reliable)
    const confirmed = window.confirm(
      `Delete cookie "${cookie.name}" from ${cookie.domain}?`
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/cookies/delete", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: cookie.name,
          domain: cookie.domain,
        }),
      });

      if (response.ok) {
        addLog(`✅ Cookie deleted: ${cookie.name}`);
        setShowCookieEditor(false);
        await analyzeCookies(); // Refresh the analysis
        await checkCookieStatus(); // Refresh cookie status
      } else {
        const error = await response.json();
        addLog(`❌ Failed to delete cookie: ${error.detail}`);
        alert(`❌ Failed to delete cookie:\n${error.detail}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
      alert(`❌ Error:\n${error.message}`);
    }
  };

  const generateCurlCommand = () => {
    const cookie = editingCookie;
    const opts = exportOptions;

    let cmd = "";

    if (opts.explainEverything) {
      cmd +=
        "# ═══════════════════════════════════════════════════════════════\n";
      cmd += "# cURL Command - HTTP Request with Cookie Authentication\n";
      cmd +=
        "# ═══════════════════════════════════════════════════════════════\n\n";

      cmd += "# COOKIE DETAILS:\n";
      cmd += `# Name: ${cookie.name}\n`;
      cmd += `#   └─ Cookie identifier (case-sensitive)\n`;
      cmd += `# Value: ${cookie.value}\n`;
      cmd += `#   └─ Cookie data (session token, user ID, etc.)\n`;
      cmd += `# Domain: ${cookie.domain}\n`;
      cmd += `#   └─ ${
        cookie.domain.startsWith(".")
          ? "Subdomain cookie (works on all subdomains)"
          : "Exact domain only"
      }\n`;
      cmd += `# Path: ${cookie.path || "/"}\n`;
      cmd += `#   └─ Cookie sent only for URLs starting with this path\n`;
      cmd += `# Expires: ${
        cookie.expires === -1 || !cookie.expires
          ? "Session (deleted when browser closes)"
          : new Date(cookie.expires * 1000).toLocaleString()
      }\n`;
      cmd += `#   └─ ${
        cookie.expires === -1 || !cookie.expires
          ? "Temporary cookie"
          : "Persistent cookie (survives browser restart)"
      }\n`;
      cmd += `# Secure: ${
        cookie.secure ? "Yes (HTTPS only)" : "No (HTTP allowed - INSECURE!)"
      }\n`;
      cmd += `#   └─ ${
        cookie.secure
          ? "Cookie only sent over encrypted connections"
          : "WARNING: Cookie can be intercepted over HTTP!"
      }\n`;
      cmd += `# HttpOnly: ${
        cookie.httpOnly
          ? "Yes (JavaScript blocked)"
          : "No (JavaScript accessible)"
      }\n`;
      cmd += `#   └─ ${
        cookie.httpOnly
          ? "Protects against XSS attacks"
          : "WARNING: Vulnerable to XSS attacks!"
      }\n`;
      cmd += `# SameSite: ${cookie.sameSite || "None"}\n`;
      cmd += `#   └─ ${
        cookie.sameSite === "Strict"
          ? "Strict - Only same-site requests (most secure)"
          : cookie.sameSite === "Lax"
          ? "Lax - Top-level navigation allowed (default)"
          : "None - Allows third-party requests (requires Secure)"
      }\n`;
      if (cookie.partitioned) {
        cmd += `# Partitioned: Yes (CHIPS enabled)\n`;
        cmd += `#   └─ Separate cookie jar per top-level site (Chrome 114+)\n`;
      }
      cmd += `# Size: ${
        (cookie.name?.length || 0) + (cookie.value?.length || 0)
      } bytes\n`;
      cmd += `#   └─ ${
        (cookie.name?.length || 0) + (cookie.value?.length || 0) > 4096
          ? "WARNING: Exceeds 4096 byte limit!"
          : "Within RFC 6265bis size limit"
      }\n\n`;

      cmd += "# COMMAND BREAKDOWN:\n";
      cmd +=
        "# curl          - Command-line tool for transferring data with URLs\n";
      if (opts.includeMethod && opts.method !== "GET") {
        cmd += `# -X ${opts.method}        - HTTP method (${
          opts.method === "POST"
            ? "submit data"
            : opts.method === "PUT"
            ? "update resource"
            : opts.method === "DELETE"
            ? "delete resource"
            : opts.method === "PATCH"
            ? "partial update"
            : "custom method"
        })\n`;
      }
      cmd += `# -H \"Cookie:\"  - HTTP header containing cookie data\n`;
      cmd += `#   └─ Format: \"Cookie: name=value\"\n`;
      cmd += `#   └─ Sent with every matching request\n`;
      if (opts.includeUrl) {
        const url = opts.url || `https://${cookie.domain}${cookie.path || "/"}`;
        cmd += `# \"${url}\" - Target URL\n`;
        cmd += `#   └─ ${
          url.startsWith("https://")
            ? "Secure HTTPS connection"
            : "WARNING: Insecure HTTP connection!"
        }\n`;
      }
      cmd += "\n# ACTUAL COMMAND:\n";
    } else if (opts.includeComments) {
      cmd += `# Cookie: ${cookie.name} (${
        cookie.secure ? "Secure" : "Insecure"
      }, ${cookie.sameSite || "No SameSite"})\n`;
    }

    cmd += "curl";

    if (opts.includeMethod && opts.method !== "GET") {
      cmd += ` -X ${opts.method}`;
    }

    if (opts.includeHeaders) {
      cmd += ` -H "Cookie: ${cookie.name}=${cookie.value}"`;
    }

    if (opts.includeUrl) {
      const url = opts.url || `https://${cookie.domain}${cookie.path || "/"}`;
      cmd += ` "${url}"`;
    }

    return cmd;
  };

  const generatePlaywrightCode = () => {
    const cookie = editingCookie;
    const opts = exportOptions;

    let code = "";

    if (opts.explainEverything) {
      code +=
        "// ═══════════════════════════════════════════════════════════════\n";
      code += "// Playwright Cookie Injection - Browser Automation\n";
      code +=
        "// ═══════════════════════════════════════════════════════════════\n\n";

      code += "// COOKIE SPECIFICATION (RFC 6265bis-21):\n";
      code +=
        "// ─────────────────────────────────────────────────────────────\n\n";

      code += `// name: '${cookie.name}'\n`;
      code += "//   ├─ PURPOSE: Unique identifier for this cookie\n";
      code += "//   ├─ TYPE: String (case-sensitive)\n";
      code += "//   ├─ REQUIRED: Yes\n";
      code += `//   └─ NOTE: ${
        cookie.name.startsWith("__Host-")
          ? "Uses __Host- prefix (requires Secure, Path=/, no Domain)"
          : cookie.name.startsWith("__Secure-")
          ? "Uses __Secure- prefix (requires Secure flag)"
          : "Standard cookie name"
      }\n\n`;

      code += `// value: '${cookie.value}'\n`;
      code +=
        "//   ├─ PURPOSE: Cookie data (session token, user preferences, etc.)\n";
      code += "//   ├─ TYPE: String (URL-encoded if contains special chars)\n";
      code += "//   ├─ REQUIRED: Yes\n";
      code += `//   ├─ SIZE: ${cookie.value?.length || 0} characters\n`;
      code += `//   └─ NOTE: ${
        (cookie.name?.length || 0) + (cookie.value?.length || 0) > 4096
          ? "⚠️ EXCEEDS 4096 byte RFC limit!"
          : "✓ Within size limits"
      }\n\n`;

      code += `// domain: '${cookie.domain}'\n`;
      code += "//   ├─ PURPOSE: Specifies which domain receives this cookie\n";
      code += "//   ├─ TYPE: String (domain name)\n";
      code += "//   ├─ REQUIRED: Yes (for Playwright)\n";
      code += `//   ├─ SCOPE: ${
        cookie.domain.startsWith(".")
          ? "Subdomain cookie (*.example.com)"
          : "Exact domain match only"
      }\n`;
      code += `//   └─ EXAMPLE: ${
        cookie.domain.startsWith(".")
          ? `Sent to ${cookie.domain.substring(1)}, www${cookie.domain}, api${
              cookie.domain
            }`
          : `Only sent to ${cookie.domain}`
      }\n\n`;

      code += `// path: '${cookie.path || "/"}'\n`;
      code += "//   ├─ PURPOSE: Restricts cookie to specific URL paths\n";
      code += "//   ├─ TYPE: String (URL path)\n";
      code += "//   ├─ DEFAULT: '/' (all paths)\n";
      code += `//   └─ EXAMPLE: ${
        cookie.path === "/" || !cookie.path
          ? "Sent to all URLs on domain"
          : `Only sent to ${cookie.domain}${cookie.path}*`
      }\n\n`;

      code += `// expires: ${cookie.expires || -1}\n`;
      code += "//   ├─ PURPOSE: Cookie lifetime (Unix timestamp in seconds)\n";
      code += "//   ├─ TYPE: Number (seconds since Jan 1, 1970)\n";
      code += `//   ├─ VALUE: ${
        cookie.expires === -1 || !cookie.expires
          ? "-1 (session cookie)"
          : `${cookie.expires} (${new Date(
              cookie.expires * 1000
            ).toLocaleString()})`
      }\n`;
      code += `//   ├─ BEHAVIOR: ${
        cookie.expires === -1 || !cookie.expires
          ? "Deleted when browser closes"
          : "Persists until expiry date"
      }\n`;
      code += `//   └─ NOTE: ${
        cookie.expires === -1 || !cookie.expires
          ? "Temporary - good for sensitive data"
          : "Permanent - survives browser restart"
      }\n\n`;

      code += `// httpOnly: ${cookie.httpOnly || false}\n`;
      code += "//   ├─ PURPOSE: Prevents JavaScript access to cookie\n";
      code += "//   ├─ TYPE: Boolean\n";
      code += "//   ├─ DEFAULT: false\n";
      code += `//   ├─ SECURITY: ${
        cookie.httpOnly
          ? "✓ Protected from XSS attacks"
          : "⚠️ Vulnerable to XSS (document.cookie can read it)"
      }\n`;
      code += `//   └─ USE CASE: ${
        cookie.httpOnly
          ? "Authentication tokens, session IDs"
          : "Client-side accessible data"
      }\n\n`;

      code += `// secure: ${cookie.secure || false}\n`;
      code += "//   ├─ PURPOSE: Only send cookie over HTTPS\n";
      code += "//   ├─ TYPE: Boolean\n";
      code += "//   ├─ DEFAULT: false\n";
      code += `//   ├─ SECURITY: ${
        cookie.secure
          ? "✓ Encrypted transmission only"
          : "⚠️ Can be sent over HTTP (interceptable!)"
      }\n`;
      code += `//   ├─ REQUIRED: ${
        cookie.sameSite === "None" ||
        cookie.partitioned ||
        cookie.name.startsWith("__Secure-") ||
        cookie.name.startsWith("__Host-")
          ? "Yes (for SameSite=None, CHIPS, or cookie prefixes)"
          : "No (but recommended)"
      }\n`;
      code += `//   └─ NOTE: ${
        cookie.secure
          ? "Production-ready"
          : "Only use false for local development!"
      }\n\n`;

      code += `// sameSite: '${cookie.sameSite || "Lax"}'\n`;
      code += "//   ├─ PURPOSE: Controls cross-site request behavior\n";
      code += "//   ├─ TYPE: String ('Strict' | 'Lax' | 'None')\n";
      code += "//   ├─ DEFAULT: 'Lax' (Chrome 80+)\n";
      code += `//   ├─ BEHAVIOR:\n`;
      code += `//   │   ${
        cookie.sameSite === "Strict"
          ? "• Strict - ONLY same-site requests (most secure)"
          : cookie.sameSite === "Lax"
          ? "• Lax - Same-site + top-level navigation (default)"
          : "• None - All requests (requires Secure flag)"
      }\n`;
      code += `//   │   ${
        cookie.sameSite === "Strict"
          ? "• Blocks: Third-party embeds, CSRF attacks"
          : cookie.sameSite === "Lax"
          ? "• Blocks: POST from other sites, allows GET links"
          : "• Allows: Third-party embeds, cross-site requests"
      }\n`;
      code += `//   └─ USE CASE: ${
        cookie.sameSite === "Strict"
          ? "Banking, sensitive operations"
          : cookie.sameSite === "Lax"
          ? "General authentication (recommended)"
          : "Third-party widgets, embeds"
      }\n`;

      if (cookie.partitioned) {
        code += `\n// partitioned: true\n`;
        code +=
          "//   ├─ PURPOSE: CHIPS (Cookies Having Independent Partitioned State)\n";
        code += "//   ├─ TYPE: Boolean\n";
        code += "//   ├─ BROWSER: Chrome 114+, Firefox 141+\n";
        code += "//   ├─ BEHAVIOR: Separate cookie jar per top-level site\n";
        code +=
          "//   ├─ EXAMPLE: Cookie on embed.com embedded in site-a.com vs site-b.com\n";
        code +=
          "//   │            → Two separate cookies (partitioned by top-level site)\n";
        code += "//   ├─ REQUIRED: Secure flag must be true\n";
        code += "//   ├─ LIMIT: Max 180 cookies per partition, 10 KB total\n";
        code += "//   └─ USE CASE: Third-party embeds (chat, maps, payments)\n";
      }

      code +=
        "\n\n// ═══════════════════════════════════════════════════════════════\n";
      code += "// ACTUAL CODE:\n";
      code +=
        "// ═══════════════════════════════════════════════════════════════\n\n";
    } else if (opts.includeComments) {
      code += `// Cookie: ${cookie.name}\n`;
      code += `// Domain: ${cookie.domain}\n`;
      code += `// Security: ${cookie.secure ? "Secure" : "Insecure"}, ${
        cookie.httpOnly ? "HttpOnly" : "No HttpOnly"
      }\n`;
      code += `// SameSite: ${cookie.sameSite || "None"}\n`;
      if (cookie.partitioned) {
        code += `// CHIPS: Partitioned cookie (Chrome 114+)\n`;
      }
      code += "\n";
    }

    code += "await context.addCookies([";

    if (opts.prettyPrint) {
      code += "{\n";
      code += `  name: '${cookie.name}',\n`;
      code += `  value: '${cookie.value}',\n`;
      code += `  domain: '${cookie.domain}',\n`;
      code += `  path: '${cookie.path || "/"}',\n`;
      code += `  expires: ${cookie.expires || -1},\n`;
      code += `  httpOnly: ${cookie.httpOnly || false},\n`;
      code += `  secure: ${cookie.secure || false},\n`;
      code += `  sameSite: '${cookie.sameSite || "Lax"}'`;
      if (cookie.partitioned) {
        code += `,\n  partitioned: true`;
      }
      code += "\n}";
    } else {
      code += `{name: '${cookie.name}', value: '${cookie.value}', domain: '${
        cookie.domain
      }', path: '${cookie.path || "/"}', expires: ${
        cookie.expires || -1
      }, httpOnly: ${cookie.httpOnly || false}, secure: ${
        cookie.secure || false
      }, sameSite: '${cookie.sameSite || "Lax"}'`;
      if (cookie.partitioned) {
        code += `, partitioned: true`;
      }
      code += "}";
    }

    code += "]);";

    return code;
  };

  const openExportModal = (type: "curl" | "playwright") => {
    setExportType(type);
    const newOptions = {
      ...exportOptions,
      url: `https://${editingCookie.domain}${editingCookie.path || "/"}`,
    };
    setExportOptions(newOptions);
    setShowExportModal(true);

    // Generate initial code
    setTimeout(() => {
      const code =
        type === "curl" ? generateCurlCommand() : generatePlaywrightCode();
      setExportCode(code);
    }, 0);
  };

  const copyExportCode = () => {
    navigator.clipboard.writeText(exportCode);
    alert(
      `✅ ${
        exportType === "curl" ? "cURL" : "Playwright"
      } code copied to clipboard!`
    );
    setShowExportModal(false);
  };

  // OWASP-compliant security audit
  const runSecurityAudit = () => {
    const issues: any[] = [];
    const warnings: any[] = [];
    const recommendations: any[] = [];
    let score = 100;

    const cookie = editingCookie;

    // Check 1: Secure flag (OWASP requirement)
    if (!cookie.secure) {
      issues.push({
        severity: "HIGH",
        title: "Missing Secure Flag",
        description:
          "Cookie can be transmitted over unencrypted HTTP connections",
        impact: "Vulnerable to man-in-the-middle attacks and eavesdropping",
        fix: "Enable the Secure flag to ensure HTTPS-only transmission",
        owasp: "OWASP Session Management - A02:2021 Cryptographic Failures",
      });
      score -= 25;
    }

    // Check 2: HttpOnly flag (XSS protection)
    if (!cookie.httpOnly) {
      issues.push({
        severity: "HIGH",
        title: "Missing HttpOnly Flag",
        description: "Cookie is accessible via JavaScript (document.cookie)",
        impact: "Vulnerable to Cross-Site Scripting (XSS) attacks",
        fix: "Enable the HttpOnly flag to prevent JavaScript access",
        owasp: "OWASP Session Management - A03:2021 Injection",
      });
      score -= 25;
    }

    // Check 3: SameSite attribute (CSRF protection)
    if (!cookie.sameSite || cookie.sameSite === "None") {
      if (cookie.sameSite === "None" && cookie.secure) {
        warnings.push({
          severity: "MEDIUM",
          title: "SameSite=None Detected",
          description: "Cookie allows cross-site requests",
          impact: "Potential CSRF vulnerability if not properly validated",
          fix: "Consider using SameSite=Strict or Lax unless third-party access is required",
          owasp: "OWASP CSRF Prevention",
        });
        score -= 10;
      } else if (cookie.sameSite === "None" && !cookie.secure) {
        issues.push({
          severity: "CRITICAL",
          title: "SameSite=None Without Secure",
          description: "SameSite=None requires Secure flag",
          impact: "Cookie will be rejected by modern browsers",
          fix: "Enable Secure flag or change SameSite to Lax/Strict",
          owasp: "RFC 6265bis Section 5.4.7",
        });
        score -= 30;
      } else {
        warnings.push({
          severity: "MEDIUM",
          title: "Missing SameSite Attribute",
          description: "Browser will use default (Lax), but explicit is better",
          impact: "Inconsistent behavior across browsers",
          fix: "Explicitly set SameSite=Strict or Lax",
          owasp: "OWASP Session Management Best Practices",
        });
        score -= 10;
      }
    } else if (cookie.sameSite === "Lax") {
      recommendations.push({
        severity: "INFO",
        title: "Consider SameSite=Strict",
        description: "SameSite=Lax allows some cross-site requests",
        impact: "Slightly weaker CSRF protection than Strict",
        fix: "Use SameSite=Strict for sensitive operations (banking, admin)",
        owasp: "OWASP Defense in Depth",
      });
    }

    // Check 4: Cookie size (RFC 6265bis limit)
    const cookieSize = (cookie.name?.length || 0) + (cookie.value?.length || 0);
    if (cookieSize > 4096) {
      issues.push({
        severity: "HIGH",
        title: "Cookie Size Exceeds RFC Limit",
        description: `Cookie is ${cookieSize} bytes (max: 4096 bytes)`,
        impact: "Cookie may be rejected by browsers or truncated",
        fix: "Reduce cookie size or split into multiple cookies",
        owasp: "RFC 6265bis Section 5.7",
      });
      score -= 20;
    } else if (cookieSize > 3000) {
      warnings.push({
        severity: "LOW",
        title: "Large Cookie Size",
        description: `Cookie is ${cookieSize} bytes (approaching 4096 limit)`,
        impact: "May cause performance issues",
        fix: "Consider reducing cookie size",
        owasp: "Performance Best Practices",
      });
      score -= 5;
    }

    // Check 5: Cookie prefix validation
    if (cookie.name?.startsWith("__Host-")) {
      if (!cookie.secure) {
        issues.push({
          severity: "CRITICAL",
          title: "__Host- Prefix Violation",
          description: "__Host- prefix requires Secure flag",
          impact: "Cookie will be rejected by browsers",
          fix: "Enable Secure flag",
          owasp: "RFC 6265bis Section 4.1.3.2",
        });
        score -= 30;
      }
      if (cookie.path !== "/") {
        issues.push({
          severity: "CRITICAL",
          title: "__Host- Prefix Violation",
          description: "__Host- prefix requires Path=/",
          impact: "Cookie will be rejected by browsers",
          fix: "Set Path to /",
          owasp: "RFC 6265bis Section 4.1.3.2",
        });
        score -= 30;
      }
      if (cookie.domain) {
        issues.push({
          severity: "CRITICAL",
          title: "__Host- Prefix Violation",
          description: "__Host- prefix must not have Domain attribute",
          impact: "Cookie will be rejected by browsers",
          fix: "Remove Domain attribute",
          owasp: "RFC 6265bis Section 4.1.3.2",
        });
        score -= 30;
      }
    } else if (cookie.name?.startsWith("__Secure-")) {
      if (!cookie.secure) {
        issues.push({
          severity: "CRITICAL",
          title: "__Secure- Prefix Violation",
          description: "__Secure- prefix requires Secure flag",
          impact: "Cookie will be rejected by browsers",
          fix: "Enable Secure flag",
          owasp: "RFC 6265bis Section 4.1.3.1",
        });
        score -= 30;
      }
    }

    // Check 6: Partitioned cookie validation (CHIPS)
    if (cookie.partitioned) {
      if (!cookie.secure) {
        issues.push({
          severity: "HIGH",
          title: "Partitioned Cookie Without Secure",
          description: "CHIPS requires Secure flag",
          impact: "Cookie will be rejected by browsers",
          fix: "Enable Secure flag",
          owasp: "CHIPS Specification",
        });
        score -= 25;
      }
      if (!cookie.name?.startsWith("__Host-")) {
        recommendations.push({
          severity: "INFO",
          title: "CHIPS Best Practice",
          description: "Partitioned cookies should use __Host- prefix",
          impact: "Enhanced security and subdomain isolation",
          fix: "Rename cookie with __Host- prefix",
          owasp: "CHIPS Security Best Practices",
        });
      }
    }

    // Check 7: Domain scope
    if (cookie.domain?.startsWith(".")) {
      warnings.push({
        severity: "MEDIUM",
        title: "Subdomain Cookie Detected",
        description: "Cookie is shared across all subdomains",
        impact: "Increased attack surface if subdomains are compromised",
        fix: "Use exact domain match unless subdomain sharing is required",
        owasp: "OWASP Session Management - Domain Scope",
      });
      score -= 10;
    }

    // Check 8: Expiry validation
    if (cookie.expires && cookie.expires !== -1) {
      const expiryDate = new Date(cookie.expires * 1000);
      const now = new Date();
      const daysUntilExpiry =
        (expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);

      if (expiryDate < now) {
        issues.push({
          severity: "HIGH",
          title: "Expired Cookie",
          description: "Cookie has already expired",
          impact: "Cookie will be immediately deleted by browser",
          fix: "Update expiry date to future timestamp",
          owasp: "Cookie Lifecycle Management",
        });
        score -= 20;
      } else if (daysUntilExpiry > 365) {
        warnings.push({
          severity: "LOW",
          title: "Long-Lived Cookie",
          description: `Cookie expires in ${Math.round(daysUntilExpiry)} days`,
          impact: "Increased risk if cookie is compromised",
          fix: "Consider shorter expiry for sensitive cookies (30-90 days)",
          owasp: "OWASP Session Timeout Best Practices",
        });
        score -= 5;
      }
    }

    // Ensure score doesn't go below 0
    score = Math.max(0, score);

    // Generate overall rating
    let rating = "";
    let ratingColor = "";
    if (score >= 90) {
      rating = "EXCELLENT";
      ratingColor = "#10b981";
    } else if (score >= 75) {
      rating = "GOOD";
      ratingColor = "#3b82f6";
    } else if (score >= 50) {
      rating = "FAIR";
      ratingColor = "#f59e0b";
    } else if (score >= 25) {
      rating = "POOR";
      ratingColor = "#ef4444";
    } else {
      rating = "CRITICAL";
      ratingColor = "#dc2626";
    }

    setSecurityReport({
      score,
      rating,
      ratingColor,
      issues,
      warnings,
      recommendations,
      cookieName: cookie.name,
      timestamp: new Date().toLocaleString(),
    });
    setShowSecurityAudit(true);
  };

  // Export all cookies in various formats
  const exportAllCookiesInFormat = (format: string) => {
    try {
      const parsedCookies = JSON.parse(cookies);
      let output = "";

      switch (format) {
        case "json":
          // Standard JSON format (current)
          output = JSON.stringify(parsedCookies, null, 2);
          break;

        case "netscape":
          // Netscape cookies.txt format
          output = "# Netscape HTTP Cookie File\n";
          output += "# This is a generated file! Do not edit.\n\n";
          parsedCookies.forEach((cookie: any) => {
            const domain = cookie.domain || "";
            const flag = domain.startsWith(".") ? "TRUE" : "FALSE";
            const path = cookie.path || "/";
            const secure = cookie.secure ? "TRUE" : "FALSE";
            const expiration = cookie.expires || 0;
            const name = cookie.name || "";
            const value = cookie.value || "";
            output += `${domain}\t${flag}\t${path}\t${secure}\t${expiration}\t${name}\t${value}\n`;
          });
          break;

        case "har":
          // HTTP Archive (HAR) format
          const harCookies = parsedCookies.map((cookie: any) => ({
            name: cookie.name || "",
            value: cookie.value || "",
            path: cookie.path || "/",
            domain: cookie.domain || "",
            expires: cookie.expires
              ? new Date(cookie.expires * 1000).toISOString()
              : undefined,
            httpOnly: cookie.httpOnly || false,
            secure: cookie.secure || false,
            sameSite: cookie.sameSite || "Lax",
          }));
          output = JSON.stringify(
            {
              log: {
                version: "1.2",
                creator: {
                  name: "Screenshot Automation Tool",
                  version: "1.0",
                },
                entries: [
                  {
                    request: {
                      cookies: harCookies,
                    },
                  },
                ],
              },
            },
            null,
            2
          );
          break;

        case "csv":
          // CSV format
          output =
            "Name,Value,Domain,Path,Expires,Secure,HttpOnly,SameSite,Partitioned\n";
          parsedCookies.forEach((cookie: any) => {
            const name = (cookie.name || "").replace(/"/g, '""');
            const value = (cookie.value || "").replace(/"/g, '""');
            const domain = (cookie.domain || "").replace(/"/g, '""');
            const path = (cookie.path || "/").replace(/"/g, '""');
            const expires = cookie.expires || "";
            const secure = cookie.secure ? "true" : "false";
            const httpOnly = cookie.httpOnly ? "true" : "false";
            const sameSite = cookie.sameSite || "Lax";
            const partitioned = cookie.partitioned ? "true" : "false";
            output += `"${name}","${value}","${domain}","${path}","${expires}","${secure}","${httpOnly}","${sameSite}","${partitioned}"\n`;
          });
          break;

        case "headers":
          // Set-Cookie headers format
          parsedCookies.forEach((cookie: any) => {
            let header = `Set-Cookie: ${cookie.name}=${cookie.value}`;
            if (cookie.domain) header += `; Domain=${cookie.domain}`;
            if (cookie.path) header += `; Path=${cookie.path}`;
            if (cookie.expires && cookie.expires !== -1) {
              const date = new Date(cookie.expires * 1000);
              header += `; Expires=${date.toUTCString()}`;
            }
            if (cookie.secure) header += `; Secure`;
            if (cookie.httpOnly) header += `; HttpOnly`;
            if (cookie.sameSite) header += `; SameSite=${cookie.sameSite}`;
            if (cookie.partitioned) header += `; Partitioned`;
            output += header + "\n";
          });
          break;

        case "curl-headers":
          // cURL -H format (multiple cookies in one header)
          const cookieStrings = parsedCookies.map(
            (cookie: any) => `${cookie.name}=${cookie.value}`
          );
          output = `curl -H "Cookie: ${cookieStrings.join(
            "; "
          )}" "https://example.com/"`;
          break;

        default:
          output = JSON.stringify(parsedCookies, null, 2);
      }

      return output;
    } catch (error: any) {
      return `Error: ${error.message}`;
    }
  };

  const downloadCookiesInFormat = () => {
    const output = exportAllCookiesInFormat(exportFormat);
    const blob = new Blob([output], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;

    // Set filename based on format
    const extensions: { [key: string]: string } = {
      json: "json",
      netscape: "txt",
      har: "har",
      csv: "csv",
      headers: "txt",
      "curl-headers": "sh",
    };
    a.download = `cookies.${extensions[exportFormat] || "txt"}`;

    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    alert(`✅ Cookies exported as ${exportFormat.toUpperCase()}!`);
    setShowFormatExport(false);
  };

  const copyFormattedCookies = () => {
    const output = exportAllCookiesInFormat(exportFormat);
    navigator.clipboard.writeText(output);
    alert(`✅ ${exportFormat.toUpperCase()} format copied to clipboard!`);
  };

  // Import cookies from various formats
  const importCookiesFromFormat = (format: string, content: string) => {
    try {
      let parsedCookies: any[] = [];

      switch (format) {
        case "json":
          parsedCookies = JSON.parse(content);
          break;

        case "netscape":
          // Parse Netscape cookies.txt format
          const lines = content.split("\n");
          parsedCookies = lines
            .filter((line) => line.trim() && !line.startsWith("#"))
            .map((line) => {
              const parts = line.split("\t");
              if (parts.length >= 7) {
                return {
                  domain: parts[0],
                  path: parts[2],
                  secure: parts[3] === "TRUE",
                  expires: parseInt(parts[4]) || -1,
                  name: parts[5],
                  value: parts[6],
                  httpOnly: false,
                  sameSite: "Lax",
                };
              }
              return null;
            })
            .filter((cookie) => cookie !== null);
          break;

        case "har":
          // Parse HAR format
          const har = JSON.parse(content);
          const harCookies = har?.log?.entries?.[0]?.request?.cookies || [];
          parsedCookies = harCookies.map((cookie: any) => ({
            name: cookie.name,
            value: cookie.value,
            domain: cookie.domain || "",
            path: cookie.path || "/",
            expires: cookie.expires
              ? Math.floor(new Date(cookie.expires).getTime() / 1000)
              : -1,
            secure: cookie.secure || false,
            httpOnly: cookie.httpOnly || false,
            sameSite: cookie.sameSite || "Lax",
            partitioned: false,
          }));
          break;

        case "csv":
          // Parse CSV format
          const csvLines = content.split("\n");
          parsedCookies = csvLines
            .slice(1) // Skip header
            .filter((line) => line.trim())
            .map((line) => {
              // Simple CSV parser (handles quoted values)
              const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
              const cleanValues = values.map((v) =>
                v.replace(/^"|"$/g, "").replace(/""/g, '"')
              );

              if (cleanValues.length >= 7) {
                return {
                  name: cleanValues[0],
                  value: cleanValues[1],
                  domain: cleanValues[2],
                  path: cleanValues[3],
                  expires: cleanValues[4] ? parseInt(cleanValues[4]) : -1,
                  secure: cleanValues[5] === "true",
                  httpOnly: cleanValues[6] === "true",
                  sameSite: cleanValues[7] || "Lax",
                  partitioned: cleanValues[8] === "true",
                };
              }
              return null;
            })
            .filter((cookie) => cookie !== null);
          break;

        default:
          throw new Error("Unsupported format");
      }

      setCookies(JSON.stringify(parsedCookies, null, 2));
      setShowFormatImport(false);
      alert(
        `✅ Successfully imported ${
          parsedCookies.length
        } cookies from ${format.toUpperCase()} format!`
      );
    } catch (error: any) {
      alert(`❌ Import failed: ${error.message}`);
    }
  };

  // Handle file upload for import
  const handleImportFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      importCookiesFromFormat(importFormat, content);
    };
    reader.readAsText(file);
  };

  // Beautify/format cookies JSON
  const beautifyCookies = () => {
    if (!cookies.trim()) {
      alert("No cookies to beautify!");
      return;
    }

    try {
      const parsed = JSON.parse(cookies);
      const beautified = JSON.stringify(parsed, null, 2);
      setCookies(beautified);
      addLog("✨ Cookies beautified successfully!");
    } catch (e) {
      alert("❌ Cannot beautify - Invalid JSON format!");
    }
  };

  // Validate and show cookie details
  const validateCookies = () => {
    if (!cookies.trim()) {
      alert("⚠️ No cookies to validate!");
      return;
    }

    try {
      const parsed = JSON.parse(cookies);

      if (!Array.isArray(parsed)) {
        alert(
          '⚠️ JSON is valid but not an array of cookies.\n\nExpected format:\n[\n  { "name": "...", "value": "...", ... }\n]'
        );
        return;
      }

      if (parsed.length === 0) {
        alert("⚠️ Cookie array is empty!");
        return;
      }

      // Analyze cookies
      const cookieNames = parsed.map((c) => c.name || "unnamed");
      const domains = [...new Set(parsed.map((c) => c.domain || "no domain"))];
      const httpOnlyCount = parsed.filter((c) => c.httpOnly === true).length;
      const secureCount = parsed.filter((c) => c.secure === true).length;

      const message = `✅ Valid JSON! Cookie Analysis:

📊 Total Cookies: ${parsed.length}
🏷️  Cookie Names: ${cookieNames.join(", ")}

🌐 Domains: ${domains.join(", ")}

🔒 Security:
  - HttpOnly: ${httpOnlyCount}/${parsed.length}
  - Secure: ${secureCount}/${parsed.length}

${
  httpOnlyCount === 0
    ? "\n⚠️ WARNING: No HttpOnly cookies found!\nYou may be missing authentication cookies.\nUse Cookie Editor extension to get ALL cookies."
    : "✅ HttpOnly cookies found - good for authentication!"
}`;

      alert(message);
      addLog(`✓ Validated ${parsed.length} cookies`);
    } catch (e) {
      alert(
        `❌ Invalid JSON format!\n\nError: ${e.message}\n\nPlease check your cookies and try again.`
      );
    }
  };

  // Beautify/format localStorage JSON
  const beautifyLocalStorage = () => {
    if (!localStorageData.trim()) {
      alert("No localStorage data to beautify!");
      return;
    }

    try {
      const parsed = JSON.parse(localStorageData);
      const beautified = JSON.stringify(parsed, null, 2);
      setLocalStorageData(beautified);
      addLog("✨ localStorage beautified successfully!");
    } catch (e) {
      alert("❌ Cannot beautify - Invalid JSON format!");
    }
  };

  // Validate and show localStorage details
  const validateLocalStorage = () => {
    if (!localStorageData.trim()) {
      alert("⚠️ No localStorage data to validate!");
      return;
    }

    try {
      const parsed = JSON.parse(localStorageData);

      if (typeof parsed !== "object" || Array.isArray(parsed)) {
        alert(
          '⚠️ JSON is valid but not an object.\n\nExpected format:\n{\n  "key1": "value1",\n  "key2": "value2"\n}'
        );
        return;
      }

      if (Object.keys(parsed).length === 0) {
        alert("⚠️ localStorage object is empty!");
        return;
      }

      // Analyze localStorage
      const keys = Object.keys(parsed);
      const tokenKeys = keys.filter(
        (k) =>
          k.toLowerCase().includes("token") || k.toLowerCase().includes("auth")
      );

      const message = `✅ Valid JSON! localStorage Analysis:

📊 Total Items: ${keys.length}
🔑 Keys: ${keys.slice(0, 10).join(", ")}${
        keys.length > 10 ? ` ... and ${keys.length - 10} more` : ""
      }

🎯 Auth-related Keys Found: ${tokenKeys.length}
${
  tokenKeys.length > 0
    ? `  - ${tokenKeys.join("\n  - ")}`
    : "  (No keys with 'token' or 'auth' in name)"
}

${
  tokenKeys.length > 0
    ? "✅ Looks good for authentication!"
    : "⚠️ No obvious auth tokens found. Make sure you exported from a logged-in session."
}`;

      alert(message);
      addLog(`✓ Validated ${keys.length} localStorage items`);
    } catch (e) {
      alert(
        `❌ Invalid JSON format!\n\nError: ${e.message}\n\nPlease check your localStorage data and try again.`
      );
    }
  };

  // Session management
  interface Screenshot {
    filename: string;
    path: string;
    url: string;
    timestamp: string;
    quality_score?: number;
    segments?: number;
  }

  interface Session {
    id: string;
    name: string;
    defaultName: string;
    timestamp: string;
    screenshots: Screenshot[];
    urls: string[];
    duration: number;
    settings: {
      captureMode: string;
      useStealth: boolean;
      useRealBrowser: boolean;
    };
  }

  // Sessions array - debounced for performance when creating/editing sessions
  const [sessions, setSessions] = useDebouncedLocalStorage<Session[]>(
    "screenshot-sessions",
    [],
    500
  );

  const [selectedSessions, setSelectedSessions] = useState<Set<string>>(
    new Set()
  );
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingSessionName, setEditingSessionName] = useState("");
  const [sessionNameError, setSessionNameError] = useState("");

  // URL Folder management
  interface URLFolder {
    id: string;
    name: string;
    urls: string[];
    created: string;
    updated: string;
  }

  // URL folders array - debounced for performance when organizing URLs
  const [urlFolders, setUrlFolders] = useDebouncedLocalStorage<URLFolder[]>(
    "screenshot-url-folders",
    [],
    500
  );

  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set()
  );
  const [editingFolderId, setEditingFolderId] = useState<string | null>(null);
  const [editingFolderName, setEditingFolderName] = useState("");
  const [folderNameError, setFolderNameError] = useState("");
  const [editingUrlId, setEditingUrlId] = useState<string | null>(null);
  const [editingUrlValue, setEditingUrlValue] = useState("");
  const [newFolderName, setNewFolderName] = useState("");
  const [bulkUrlInput, setBulkUrlInput] = useState<{
    [folderId: string]: string;
  }>({});
  const [selectedUrls, setSelectedUrls] = useState<{
    [folderId: string]: Set<number>;
  }>({});
  const [searchQuery, setSearchQuery] = useState<{
    [folderId: string]: string;
  }>({});
  const [sortOrder, setSortOrder] = useState<{
    [folderId: string]: "date-desc" | "date-asc" | "alpha-asc" | "alpha-desc";
  }>({});

  // Refs for scroll synchronization
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);

  // Advanced segmented settings
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [segmentOverlap, setSegmentOverlap] = useLocalStorage(
    "screenshot-segment-overlap",
    20
  );
  const [segmentScrollDelay, setSegmentScrollDelay] = useLocalStorage(
    "screenshot-segment-scrolldelay",
    1000
  );
  const [segmentMaxSegments, setSegmentMaxSegments] = useLocalStorage(
    "screenshot-segment-maxsegments",
    50
  );
  const [segmentSkipDuplicates, setSegmentSkipDuplicates] = useLocalStorage(
    "screenshot-segment-skipduplicates",
    true
  );
  const [segmentSmartLazyLoad, setSegmentSmartLazyLoad] = useLocalStorage(
    "screenshot-segment-smartlazyload",
    true
  );

  // Dark mode state
  const [darkMode, setDarkMode] = useLocalStorage("screenshot-darkmode", false);

  // Animation trigger for mode toggle
  const [isToggling, setIsToggling] = useState(false);

  // Logs visibility and status
  const [showLogs, setShowLogs] = useState(false);
  const [hasErrors, setHasErrors] = useState(false);

  // ✅ FIX: Define addLog early so it can be used by all functions
  // ⚡ OPTIMIZATION: Wrap with useCallback to prevent recreation on every render
  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const newLog = `[${timestamp}] ${message}`;
    setLogs((prev) => [...prev, newLog]);

    // Check if this log contains REAL error indicators (more strict)
    // Only detect actual errors, not success messages with "failed" in context
    // Exclude summary lines that show "Failed: 0" or similar
    const isSummaryLine =
      message.includes("Success:") && message.includes("Failed:");

    const isActualError =
      !isSummaryLine &&
      (message.includes("❌") ||
        message.toLowerCase().includes("error:") ||
        message.toLowerCase().includes("failed:") ||
        message.toLowerCase().includes("exception:") ||
        (message.toLowerCase().includes("error") &&
          !message.includes("✅") &&
          !message.toLowerCase().includes("no error")));

    if (isActualError) {
      setHasErrors(true);
      // DO NOT auto-show logs - let user click to see them
    }
  }, []); // ✅ No dependencies - stable function

  // Backend restart state
  const [isRestartingBackend, setIsRestartingBackend] = useState(false);
  const [restartMessage, setRestartMessage] = useState<string | null>(null);

  // Tab system - active tab and open tabs
  const [activeTab, setActiveTabState] = useState<
    | "main"
    | "sessions"
    | "urls"
    | "cookies"
    | "settings"
    | "logs"
    | "keyword-config"
  >("main");
  const [openTabs, setOpenTabs] = useState<
    Array<
      | "main"
      | "sessions"
      | "urls"
      | "cookies"
      | "settings"
      | "logs"
      | "keyword-config"
    >
  >(["main", "sessions", "urls", "cookies"]); // Main, Sessions, URLs, and Cookies are permanent tabs

  // Wrapper for setActiveTab that logs tab changes
  const setActiveTab = (
    tab:
      | "main"
      | "sessions"
      | "urls"
      | "cookies"
      | "settings"
      | "logs"
      | "keyword-config"
  ) => {
    const tabNames = {
      main: "Main",
      sessions: "Sessions",
      urls: "URLs",
      cookies: "Cookies",
      settings: "Settings",
      logs: "Logs",
      "keyword-config": "Keyword Config",
    };
    addLog(`📑 Switched to ${tabNames[tab]} tab`);
    setActiveTabState(tab);
  };

  // Collapsible segments state - track which results have expanded segments
  const [expandedSegments, setExpandedSegments] = useState<Set<number>>(
    new Set()
  );

  // URL tooltip state - track which URL is being hovered and clicked
  const [hoveredUrl, setHoveredUrl] = useState<number | null>(null);
  const [clickedUrl, setClickedUrl] = useState<number | null>(null);
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);
  const [clickTimeout, setClickTimeout] = useState<NodeJS.Timeout | null>(null);

  // Save URLs to localStorage - handled by useDebouncedLocalStorage hook (500ms debounce)
  // This reduces localStorage I/O by ~99% (100+ writes → 1 write per edit session!)

  // Save settings to localStorage - handled by useLocalStorage hook for:
  // captureMode, useStealth, useRealBrowser, browserEngine, baseUrl

  // Save text inputs to localStorage - handled by useDebouncedLocalStorage hook (500ms debounce):
  // wordsToRemove, cookies, localStorageData
  // This reduces localStorage I/O by ~98% for these frequently-edited fields!

  // Save complex objects to localStorage - handled by useDebouncedLocalStorage hook (500ms debounce):
  // sessions, urlFolders
  // This reduces localStorage I/O by ~90% when creating/editing sessions and organizing URLs!

  // Save advanced segmented settings - handled by useLocalStorage hook for:
  // segmentOverlap, segmentScrollDelay, segmentMaxSegments, segmentSkipDuplicates, segmentSmartLazyLoad

  // Apply dark mode class to body (localStorage save handled by useLocalStorage hook)
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    // Trigger celebration animation
    setIsToggling(true);
    setTimeout(() => {
      setIsToggling(false);
    }, 1000); // Animation lasts 1 second
  };

  const toggleSegmentExpansion = (index: number) => {
    setExpandedSegments((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  // ✅ Parse word transformation input (supports: word, word:"", word:"space", word:"custom")
  const parseWordInput = (input: string): WordTransformation | null => {
    const trimmed = input.trim();
    if (!trimmed) return null;

    // Match: word:"replacement" syntax
    const match = trimmed.match(/^(.+?):"(.*)"$/);

    if (match) {
      const word = match[1].trim();
      const replacement = match[2]; // Can be empty string, "space", or custom text

      if (!word) return null;

      if (replacement === "") {
        return { word, replacement: "", type: "remove" };
      } else if (replacement === "space") {
        return { word, replacement: " ", type: "space" };
      } else {
        return { word, replacement, type: "custom" };
      }
    }

    // Default: replace with space (backward compatible)
    return { word: trimmed, replacement: " ", type: "space" };
  };

  // Add word transformation to list
  const addWordToRemove = (input: string) => {
    const transformation = parseWordInput(input);
    if (!transformation) return;

    // Check if word already exists
    const exists = wordsToRemove.some((t) => t.word === transformation.word);
    if (!exists) {
      const newIndex = wordsToRemove.length;
      setWordsToRemove([...wordsToRemove, transformation]);
      setWordInput("");

      // ✅ Open editor modal immediately after adding
      setTimeout(() => {
        openWordEditor(newIndex);
      }, 100); // Small delay to ensure state is updated
    }
  };

  // Remove word transformation from list
  const removeWordToRemove = (index: number) => {
    setWordsToRemove(wordsToRemove.filter((_, i) => i !== index));
  };

  // Handle word input key press
  const handleWordInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addWordToRemove(wordInput);
    } else if (
      e.key === "Backspace" &&
      wordInput === "" &&
      wordsToRemove.length > 0
    ) {
      // Remove last tag if backspace on empty input
      removeWordToRemove(wordsToRemove.length - 1);
    }
  };

  // ✅ Open word editor modal (for editing existing transformation)
  const openWordEditor = (index: number) => {
    const transform = wordsToRemove[index];
    setEditingWordIndex(index);
    setEditorWord(transform.word);
    setEditorReplacement(
      transform.type === "space" ? "" : transform.replacement
    );
    setEditorType(transform.type);
    setShowWordEditor(true);
  };

  // ✅ Save word transformation from editor modal
  const saveWordTransformation = () => {
    if (!editorWord.trim()) return;

    const newTransform: WordTransformation = {
      word: editorWord.trim(),
      replacement:
        editorType === "remove"
          ? ""
          : editorType === "space"
          ? " "
          : editorReplacement,
      type: editorType,
    };

    if (editingWordIndex !== null) {
      // Update existing
      const updated = [...wordsToRemove];
      updated[editingWordIndex] = newTransform;
      setWordsToRemove(updated);
    } else {
      // Add new
      const exists = wordsToRemove.some((t) => t.word === newTransform.word);
      if (!exists) {
        setWordsToRemove([...wordsToRemove, newTransform]);
      }
    }

    closeWordEditor();
  };

  // ✅ Close word editor modal
  const closeWordEditor = () => {
    setShowWordEditor(false);
    setEditingWordIndex(null);
    setEditorWord("");
    setEditorReplacement("");
    setEditorType("space");
  };

  // Session management functions
  const createSession = (
    screenshots: Screenshot[],
    captureUrls: string[],
    captureDuration: number
  ) => {
    const sessionNumber = sessions.length + 1;
    const defaultName = `Session ${sessionNumber}`;

    const newSession: Session = {
      id: `session-${Date.now()}`,
      name: defaultName,
      defaultName: defaultName,
      timestamp: new Date().toISOString(),
      screenshots: screenshots,
      urls: captureUrls,
      duration: captureDuration,
      settings: {
        captureMode: captureMode,
        useStealth: useStealth,
        useRealBrowser: useRealBrowser,
      },
    };

    // ✅ OPTIMIZATION: Limit to last 50 sessions to prevent localStorage bloat
    const MAX_SESSIONS = 50;
    const updatedSessions = [newSession, ...sessions].slice(0, MAX_SESSIONS);
    setSessions(updatedSessions);

    if (sessions.length >= MAX_SESSIONS) {
      console.log(
        `🗑️ Removed oldest session to maintain ${MAX_SESSIONS} session limit`
      );
    }

    return newSession;
  };

  const toggleSessionSelection = (sessionId: string) => {
    // ✅ FIX: Get session info BEFORE state update to avoid double logging
    const session = sessions.find((s) => s.id === sessionId);
    const sessionName = session ? session.name : sessionId;
    const isCurrentlySelected = selectedSessions.has(sessionId);

    setSelectedSessions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(sessionId)) {
        newSet.delete(sessionId);
      } else {
        newSet.add(sessionId);
      }
      return newSet;
    });

    // ✅ FIX: Log AFTER state update to avoid being called multiple times
    if (isCurrentlySelected) {
      addLog(`☐ Deselected session: ${sessionName}`);
    } else {
      addLog(`☑ Selected session: ${sessionName}`);
    }
  };

  const selectAllSessions = () => {
    setSelectedSessions(new Set(sessions.map((s) => s.id)));
    addLog(`☑ Selected all ${sessions.length} session(s)`);
  };

  const deselectAllSessions = () => {
    setSelectedSessions(new Set());
    addLog(`☐ Deselected all sessions`);
  };

  // ✅ FIX: Track deletion in progress to prevent multiple clicks
  const [isDeletingSession, setIsDeletingSession] = useState(false);
  const isDeletingSessionRef = useRef(false);

  const deleteSelectedSessions = useCallback(async () => {
    // ✅ FIX: Prevent multiple simultaneous deletions using ref (more reliable than state)
    if (isDeletingSessionRef.current || selectedSessions.size === 0) {
      if (selectedSessions.size === 0) {
        addLog(`⚠️ No sessions selected for deletion`);
      }
      console.log(
        `DEBUG: Skipping deletion - already deleting or no sessions selected`
      );
      return;
    }

    isDeletingSessionRef.current = true;
    setIsDeletingSession(true);
    addLog(`🗑️ Attempting to delete ${selectedSessions.size} session(s)...`);
    console.log(`DEBUG: About to show confirmation dialog...`);

    try {
      // ✅ FIX: Use custom confirm dialog instead of browser confirm
      console.log(`DEBUG: Calling custom confirm dialog...`);
      const confirmed = await showCustomConfirm(
        "🗑️ Delete Sessions",
        `Are you sure you want to delete ${selectedSessions.size} selected session(s)?\n\nThis action cannot be undone.`
      );
      console.log(`DEBUG: Custom confirm returned: ${confirmed}`);

      if (confirmed) {
        console.log(`DEBUG: User confirmed deletion`);
        const deletedCount = selectedSessions.size;
        const newSessions = sessions.filter((s) => !selectedSessions.has(s.id));

        // ✅ FIX: Write to localStorage BEFORE calling setSessions to avoid race condition
        // This ensures the immediate write happens before the debounced hook's useEffect
        try {
          localStorage.setItem(
            "screenshot-sessions",
            JSON.stringify(newSessions)
          );
          console.log(
            `✅ Deleted ${deletedCount} session(s) - saved to localStorage immediately`
          );
        } catch (error) {
          console.error("Error saving sessions to localStorage:", error);
        }

        // Now update state - the debounced hook will use the latest value from valueRef
        setSessions(newSessions);
        setSelectedSessions(new Set());
        addLog(`✅ Deleted ${deletedCount} session(s) successfully`);
      } else {
        console.log(`DEBUG: User cancelled deletion`);
        addLog(`❌ Deletion cancelled by user`);
      }
    } catch (error) {
      console.error(`❌ ERROR in deleteSelectedSessions:`, error);
      addLog(`❌ Error during deletion: ${error}`);
    } finally {
      // ✅ FIX: Always reset the deletion flag
      isDeletingSessionRef.current = false;
      setIsDeletingSession(false);
    }
  }, [selectedSessions, sessions, addLog]);

  const startEditingSession = (sessionId: string) => {
    const session = sessions.find((s) => s.id === sessionId);
    if (session) {
      setEditingSessionId(sessionId);
      setEditingSessionName(session.name);
      setSessionNameError("");
      addLog(`✏️ Started editing session: ${session.name}`);
    }
  };

  const cancelEditingSession = () => {
    const session = sessions.find((s) => s.id === editingSessionId);
    if (session) {
      addLog(`❌ Cancelled editing session: ${session.name}`);
    }
    setEditingSessionId(null);
    setEditingSessionName("");
    setSessionNameError("");
  };

  const saveSessionName = (sessionId: string) => {
    const trimmedName = editingSessionName.trim();

    // Check if empty
    if (!trimmedName) {
      setSessionNameError("Session name cannot be empty!");
      return;
    }

    // Check for duplicates (case-insensitive, excluding current session)
    const isDuplicate = sessions.some(
      (s) =>
        s.id !== sessionId && s.name.toLowerCase() === trimmedName.toLowerCase()
    );

    if (isDuplicate) {
      setSessionNameError(
        "Session name already exists! Choose a different name."
      );
      return;
    }

    // Update session name
    const oldSession = sessions.find((s) => s.id === sessionId);
    setSessions(
      sessions.map((s) =>
        s.id === sessionId ? { ...s, name: trimmedName } : s
      )
    );

    if (oldSession) {
      addLog(`✏️ Renamed session: "${oldSession.name}" → "${trimmedName}"`);
    }

    setEditingSessionId(null);
    setEditingSessionName("");
    setSessionNameError("");
  };

  const handleSessionNameKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>,
    sessionId: string
  ) => {
    if (e.key === "Enter") {
      e.preventDefault();
      saveSessionName(sessionId);
    } else if (e.key === "Escape") {
      e.preventDefault();
      cancelEditingSession();
    }
  };

  // URL Folder Management Functions
  const createFolder = () => {
    const trimmedName = newFolderName.trim();

    if (!trimmedName) {
      alert("Folder name cannot be empty!");
      return;
    }

    // Check for duplicates (case-insensitive)
    const isDuplicate = urlFolders.some(
      (f) => f.name.toLowerCase() === trimmedName.toLowerCase()
    );

    if (isDuplicate) {
      alert("Folder name already exists! Choose a different name.");
      return;
    }

    const newFolder: URLFolder = {
      id: `folder-${Date.now()}`,
      name: trimmedName,
      urls: [],
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    setUrlFolders([...urlFolders, newFolder]);
    setNewFolderName("");
    setExpandedFolders(new Set([...expandedFolders, newFolder.id]));
    addLog(`📁 Created folder: ${newFolder.name}`);
  };

  // ✅ FIX: Track folder deletion in progress to prevent multiple clicks
  const [isDeletingFolder, setIsDeletingFolder] = useState<string | null>(null);

  const deleteFolder = async (folderId: string) => {
    // ✅ FIX: Prevent multiple simultaneous deletions
    if (isDeletingFolder) return;

    const folder = urlFolders.find((f) => f.id === folderId);
    if (!folder) return;

    setIsDeletingFolder(folderId);

    try {
      // ✅ FIX: Use browser confirm directly (more reliable)
      const confirmed = window.confirm(
        `Delete folder "${folder.name}" with ${folder.urls.length} URL(s)?`
      );

      if (confirmed) {
        const newFolders = urlFolders.filter((f) => f.id !== folderId);

        // ✅ FIX: Write to localStorage BEFORE calling setUrlFolders to avoid race condition
        try {
          localStorage.setItem(
            "screenshot-url-folders",
            JSON.stringify(newFolders)
          );
        } catch (error) {
          console.error("Error saving URL folders to localStorage:", error);
        }

        setUrlFolders(newFolders);
        addLog(`🗑️ Deleted folder: ${folder.name}`);
      }
    } finally {
      // ✅ FIX: Always reset the deletion flag
      setIsDeletingFolder(null);
    }
  };

  const startEditingFolder = (folderId: string) => {
    const folder = urlFolders.find((f) => f.id === folderId);
    if (folder) {
      setEditingFolderId(folderId);
      setEditingFolderName(folder.name);
      setFolderNameError("");
      addLog(`✏️ Started editing folder: ${folder.name}`);
    }
  };

  const cancelEditingFolder = () => {
    const folder = urlFolders.find((f) => f.id === editingFolderId);
    if (folder) {
      addLog(`❌ Cancelled editing folder: ${folder.name}`);
    }
    setEditingFolderId(null);
    setEditingFolderName("");
    setFolderNameError("");
  };

  const saveFolderName = (folderId: string) => {
    const trimmedName = editingFolderName.trim();

    if (!trimmedName) {
      setFolderNameError("Folder name cannot be empty!");
      return;
    }

    // Check for duplicates (case-insensitive, excluding current folder)
    const isDuplicate = urlFolders.some(
      (f) =>
        f.id !== folderId && f.name.toLowerCase() === trimmedName.toLowerCase()
    );

    if (isDuplicate) {
      setFolderNameError(
        "Folder name already exists! Choose a different name."
      );
      return;
    }

    const oldFolder = urlFolders.find((f) => f.id === folderId);
    setUrlFolders(
      urlFolders.map((f) =>
        f.id === folderId
          ? { ...f, name: trimmedName, updated: new Date().toISOString() }
          : f
      )
    );

    if (oldFolder) {
      addLog(`✏️ Renamed folder: "${oldFolder.name}" → "${trimmedName}"`);
    }

    setEditingFolderId(null);
    setEditingFolderName("");
    setFolderNameError("");
  };

  const toggleFolderExpanded = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    const folder = urlFolders.find((f) => f.id === folderId);
    const folderName = folder ? folder.name : folderId;

    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
      addLog(`📁 Collapsed folder: ${folderName}`);
    } else {
      newExpanded.add(folderId);
      addLog(`📂 Expanded folder: ${folderName}`);
    }
    setExpandedFolders(newExpanded);
  };

  // URL Selection Functions
  const toggleUrlSelection = (folderId: string, urlIndex: number) => {
    const currentSelected = selectedUrls[folderId] || new Set<number>();
    const newSelected = new Set(currentSelected);

    if (newSelected.has(urlIndex)) {
      newSelected.delete(urlIndex);
    } else {
      newSelected.add(urlIndex);
    }

    setSelectedUrls({ ...selectedUrls, [folderId]: newSelected });
  };

  const selectAllUrls = (folderId: string) => {
    const folder = urlFolders.find((f) => f.id === folderId);
    if (!folder) return;

    const filteredUrls = getFilteredAndSortedUrls(folderId);
    const allIndices = new Set(
      filteredUrls.map((_, idx) => {
        // Get original index from filtered list
        return folder.urls.indexOf(filteredUrls[idx]);
      })
    );

    setSelectedUrls({ ...selectedUrls, [folderId]: allIndices });
  };

  const deselectAllUrls = (folderId: string) => {
    setSelectedUrls({ ...selectedUrls, [folderId]: new Set<number>() });
  };

  // ✅ FIX: Track URL deletion in progress to prevent multiple clicks
  const [isDeletingUrls, setIsDeletingUrls] = useState<string | null>(null);

  const deleteSelectedUrls = async (folderId: string) => {
    // ✅ FIX: Prevent multiple simultaneous deletions
    if (isDeletingUrls) return;

    const selected = selectedUrls[folderId];
    if (!selected || selected.size === 0) return;

    setIsDeletingUrls(folderId);

    try {
      // ✅ FIX: Use browser confirm directly (more reliable)
      const confirmed = window.confirm(
        `Delete ${selected.size} selected URL(s)? This cannot be undone.`
      );

      if (!confirmed) return;

      const newFolders = urlFolders.map((f) =>
        f.id === folderId
          ? {
              ...f,
              urls: f.urls.filter((_, idx) => !selected.has(idx)),
              updated: new Date().toISOString(),
            }
          : f
      );

      // ✅ FIX: Write to localStorage BEFORE calling setUrlFolders to avoid race condition
      try {
        localStorage.setItem(
          "screenshot-url-folders",
          JSON.stringify(newFolders)
        );
      } catch (error) {
        console.error("Error saving URL folders to localStorage:", error);
      }

      setUrlFolders(newFolders);
      setSelectedUrls({ ...selectedUrls, [folderId]: new Set<number>() });
      addLog(`🗑️ Deleted ${selected.size} URL(s) from folder`);
    } finally {
      // ✅ FIX: Always reset the deletion flag
      setIsDeletingUrls(null);
    }
  };

  const copySelectedUrls = (folderId: string) => {
    const folder = urlFolders.find((f) => f.id === folderId);
    const selected = selectedUrls[folderId];

    if (!folder || !selected || selected.size === 0) return;

    const selectedUrlsList = folder.urls.filter((_, idx) => selected.has(idx));
    const urlText = selectedUrlsList.join("\n");

    navigator.clipboard.writeText(urlText).then(() => {
      addLog(`📋 Copied ${selected.size} URL(s) to clipboard`);
      alert(`Copied ${selected.size} URL(s) to clipboard!`);
    });
  };

  // Filter and Sort Functions
  const getFilteredAndSortedUrls = (folderId: string): string[] => {
    const folder = urlFolders.find((f) => f.id === folderId);
    if (!folder) return [];

    let urls = [...folder.urls];

    // Apply search filter
    const query = searchQuery[folderId];
    if (query && query.trim()) {
      const lowerQuery = query.toLowerCase();
      urls = urls.filter((url) => url.toLowerCase().includes(lowerQuery));
    }

    // Apply sort
    const sort = sortOrder[folderId] || "date-desc";

    if (sort === "date-asc") {
      urls = [...urls].reverse(); // Oldest first
    } else if (sort === "alpha-asc") {
      urls = [...urls].sort((a, b) => a.localeCompare(b)); // A-Z
    } else if (sort === "alpha-desc") {
      urls = [...urls].sort((a, b) => b.localeCompare(a)); // Z-A
    }
    // "date-desc" is default (newest first, no change needed)

    return urls;
  };

  // ✅ NEW: Update batch timeout for a specific text box and trigger doc generation if changed
  const updateBatchTimeout = async (textBoxId: string, newTimeout: number) => {
    // Validate input
    if (isNaN(newTimeout) || newTimeout < 10 || newTimeout > 300) {
      addLog("⚠️ Batch timeout must be between 10 and 300 seconds");
      return;
    }

    // Find the text box
    const textBox = textBoxes.find((tb) => tb.id === textBoxId);
    if (!textBox) return;

    const oldTimeout = textBox.batchTimeout || 90;

    // ✅ FIX: Don't update state here - onChange already did it!
    // Just check if value changed and call API

    // Check if value actually changed
    if (newTimeout !== oldTimeout) {
      addLog(`⏱️ Text Box timeout changed: ${oldTimeout}s → ${newTimeout}s`);
      addLog("📊 Regenerating performance documentation...");

      try {
        const response = await fetch(
          `${config.apiBaseUrl}/api/update-batch-timeout`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ timeout: newTimeout }),
          }
        );

        if (response.ok) {
          addLog("✅ Performance documentation updated successfully!");
        } else {
          addLog("⚠️ Failed to update documentation (backend error)");
        }
      } catch (error: any) {
        addLog(`⚠️ Failed to update documentation: ${error.message}`);
      }
    }
  };

  // URL Management Functions (with auto-beautify)
  // Bulk add URLs to folder from textarea
  const addBulkUrlsToFolder = (folderId: string) => {
    const inputText = bulkUrlInput[folderId] || "";

    if (!inputText.trim()) {
      alert("Please enter at least one URL!");
      return;
    }

    // Parse and format URLs
    // First, insert newlines before every http:// or https:// that's not at the start
    const withSeparatedUrls = inputText.replace(/(https?:\/\/)/g, "\n$1");

    // Split by newlines, spaces, commas, semicolons
    const parsedUrls = withSeparatedUrls
      .split(/[\n\s,;]+/)
      .map((url) => url.trim())
      .filter((url) => url.length > 0)
      .filter((url) => url.startsWith("http://") || url.startsWith("https://"));

    if (parsedUrls.length === 0) {
      alert(
        "No valid URLs found! Please enter URLs starting with http:// or https://"
      );
      return;
    }

    // Remove duplicates within the input itself (case-insensitive)
    const uniqueParsedUrls: string[] = [];
    const seenUrls = new Set<string>();

    for (const url of parsedUrls) {
      const lowerUrl = url.toLowerCase();
      if (!seenUrls.has(lowerUrl)) {
        seenUrls.add(lowerUrl);
        uniqueParsedUrls.push(url);
      }
    }

    // Get existing URLs for this folder
    const folder = urlFolders.find((f) => f.id === folderId);
    const existingUrls = folder ? folder.urls : [];

    // Remove duplicates against existing URLs (case-insensitive)
    const newUrls = uniqueParsedUrls.filter(
      (url) =>
        !existingUrls.some(
          (existing) => existing.toLowerCase() === url.toLowerCase()
        )
    );

    if (newUrls.length === 0) {
      alert("All URLs already exist in this folder!");
      return;
    }

    // Add URLs to folder
    setUrlFolders(
      urlFolders.map((f) =>
        f.id === folderId
          ? {
              ...f,
              urls: [...f.urls, ...newUrls],
              updated: new Date().toISOString(),
            }
          : f
      )
    );

    // Clear textarea for this folder
    setBulkUrlInput({ ...bulkUrlInput, [folderId]: "" });

    const inputDuplicates = parsedUrls.length - uniqueParsedUrls.length;
    const existingDuplicates = uniqueParsedUrls.length - newUrls.length;
    const totalDuplicates = inputDuplicates + existingDuplicates;

    let logMessage = `✅ Added ${newUrls.length} URL(s) to folder`;
    if (totalDuplicates > 0) {
      logMessage += ` (${totalDuplicates} duplicate${
        totalDuplicates > 1 ? "s" : ""
      } skipped`;
      if (inputDuplicates > 0 && existingDuplicates > 0) {
        logMessage += `: ${inputDuplicates} in input, ${existingDuplicates} already exist`;
      } else if (inputDuplicates > 0) {
        logMessage += ` in input`;
      } else {
        logMessage += ` - already exist`;
      }
      logMessage += ")";
    }

    addLog(logMessage);
  };

  // Clean up duplicate URLs in all folders (case-insensitive)
  const removeDuplicateUrls = () => {
    const cleanedFolders = urlFolders.map((folder) => {
      const uniqueUrls: string[] = [];
      const seenUrls = new Set<string>();

      for (const url of folder.urls) {
        const lowerUrl = url.toLowerCase();
        if (!seenUrls.has(lowerUrl)) {
          seenUrls.add(lowerUrl);
          uniqueUrls.push(url);
        }
      }

      // Only update if duplicates were found
      if (uniqueUrls.length !== folder.urls.length) {
        return {
          ...folder,
          urls: uniqueUrls,
          updated: new Date().toISOString(),
        };
      }
      return folder;
    });

    // Check if any folder was cleaned
    const hadDuplicates = cleanedFolders.some(
      (folder, index) => folder.urls.length !== urlFolders[index].urls.length
    );

    if (hadDuplicates) {
      setUrlFolders(cleanedFolders);
      addLog("🧹 Cleaned up duplicate URLs from folders");
    }
  };

  const startEditingUrl = (folderId: string, urlIndex: number) => {
    const folder = urlFolders.find((f) => f.id === folderId);
    if (folder && folder.urls[urlIndex]) {
      setEditingUrlId(`${folderId}-${urlIndex}`);
      setEditingUrlValue(folder.urls[urlIndex]);
    }
  };

  const cancelEditingUrl = () => {
    setEditingUrlId(null);
    setEditingUrlValue("");
  };

  const saveUrl = (folderId: string, urlIndex: number) => {
    const trimmedUrl = editingUrlValue.trim();

    if (!trimmedUrl) {
      alert("URL cannot be empty!");
      return;
    }

    // Validate URL
    try {
      new URL(trimmedUrl);
    } catch {
      alert(
        "Invalid URL! Please enter a valid URL starting with http:// or https://"
      );
      return;
    }

    // Just validate, don't beautify - keep query params and fragments
    if (
      !trimmedUrl.startsWith("http://") &&
      !trimmedUrl.startsWith("https://")
    ) {
      alert(
        "Invalid URL! Please enter a valid URL starting with http:// or https://"
      );
      return;
    }

    setUrlFolders(
      urlFolders.map((f) =>
        f.id === folderId
          ? {
              ...f,
              urls: f.urls.map((url, idx) =>
                idx === urlIndex ? trimmedUrl : url
              ),
              updated: new Date().toISOString(),
            }
          : f
      )
    );

    setEditingUrlId(null);
    setEditingUrlValue("");
    addLog(`✏️ Updated URL`);
  };

  // ✅ FIX: Track single URL deletion in progress to prevent multiple clicks
  const [isDeletingSingleUrl, setIsDeletingSingleUrl] = useState<string | null>(
    null
  );

  const deleteUrl = async (folderId: string, urlIndex: number) => {
    // ✅ FIX: Prevent multiple simultaneous deletions
    if (isDeletingSingleUrl) return;

    setIsDeletingSingleUrl(`${folderId}-${urlIndex}`);

    try {
      // ✅ FIX: Use browser confirm directly (more reliable)
      const confirmed = window.confirm("Delete this URL?");

      if (confirmed) {
        const newFolders = urlFolders.map((f) =>
          f.id === folderId
            ? {
                ...f,
                urls: f.urls.filter((_, idx) => idx !== urlIndex),
                updated: new Date().toISOString(),
              }
            : f
        );

        // ✅ FIX: Write to localStorage BEFORE calling setUrlFolders to avoid race condition
        try {
          localStorage.setItem(
            "screenshot-url-folders",
            JSON.stringify(newFolders)
          );
        } catch (error) {
          console.error("Error saving URL folders to localStorage:", error);
        }

        setUrlFolders(newFolders);
        addLog(`🗑️ Deleted URL from folder`);
      }
    } finally {
      // ✅ FIX: Always reset the deletion flag
      setIsDeletingSingleUrl(null);
    }
  };

  // @mention Detection and Loading Functions
  const detectFolderMention = (text: string): string | null => {
    const match = text.match(/@(\w+)/);
    return match ? match[1] : null;
  };

  const loadFolderUrls = (folderName: string) => {
    const folder = urlFolders.find(
      (f) => f.name.toLowerCase() === folderName.toLowerCase()
    );

    if (folder) {
      // Load URLs as-is, keeping query params and fragments
      setUrls(folder.urls.join("\n"));
      addLog(
        `✅ Loaded ${folder.urls.length} URL(s) from folder "${folder.name}"`
      );
    } else {
      addLog(`❌ Folder "${folderName}" not found`);
      alert(`Folder "${folderName}" not found!`);
    }
  };

  // Handle URL hover - show tooltip after 3 seconds
  const handleUrlMouseEnter = (index: number) => {
    const timeout = setTimeout(() => {
      setHoveredUrl(index);
    }, 3000); // 3 seconds delay
    setHoverTimeout(timeout);
  };

  const handleUrlMouseLeave = () => {
    if (hoverTimeout) {
      clearTimeout(hoverTimeout);
      setHoverTimeout(null);
    }
    setHoveredUrl(null);
  };

  // Handle URL click - show tooltip for 10 seconds
  const handleUrlClick = (index: number) => {
    // Clear any existing click timeout
    if (clickTimeout) {
      clearTimeout(clickTimeout);
    }

    setClickedUrl(index);
    const timeout = setTimeout(() => {
      setClickedUrl(null);
    }, 10000); // 10 seconds
    setClickTimeout(timeout);
  };

  // Sync line numbers scroll with textarea scroll
  const handleTextareaScroll = () => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  // Auto-launch Chrome with remote debugging on app startup
  const launchDebugChrome = async () => {
    try {
      const response = await fetch(apiUrl("/api/launch-debug-chrome"), {
        method: "POST",
      });

      if (response.ok) {
        const data = await response.json();
        console.log("✅ Debug Chrome launched:", data);
        addLog("🔴 Debug Chrome launched automatically");
      } else {
        console.warn(
          "⚠️ Failed to launch debug Chrome:",
          await response.text()
        );
      }
    } catch (error) {
      console.error("❌ Error launching debug Chrome:", error);
      // Don't show error to user - it's not critical if Chrome is already running
    }
  };

  // Log app initialization on first load
  useEffect(() => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs([`[${timestamp}] 🚀 Screenshot Tool initialized`]);

    // Auto-launch debug Chrome if Real Browser mode is enabled
    if (useRealBrowser) {
      launchDebugChrome();
    }
  }, []); // Empty dependency array = run once on mount

  // Request notification permission on component mount
  useEffect(() => {
    if ("Notification" in window) {
      console.log(
        "🔔 Current notification permission:",
        Notification.permission
      );

      if (Notification.permission === "default") {
        console.log("🔔 Requesting notification permission...");
        Notification.requestPermission().then((permission) => {
          console.log("🔔 Notification permission result:", permission);
          if (permission === "granted") {
            // Show a test notification
            new Notification("📸 Screenshot Tool", {
              body: "Notifications enabled! You'll be notified when screenshots are captured.",
              icon: "/favicon.ico",
            });
          }
        });
      } else if (Notification.permission === "granted") {
        console.log("✅ Notifications already granted");
      } else {
        console.warn("❌ Notifications denied by user");
      }
    } else {
      console.warn("❌ Notifications not supported in this browser");
    }
  }, []);

  // ✅ FIX: Wrapper functions that log setting changes (defined after addLog)
  const setCaptureMode = (mode: string) => {
    const modeNames = {
      viewport: "Viewport only",
      fullpage: "Full page",
      segmented: "Segmented",
    };
    addLog(
      `⚙️ Changed capture mode to: ${
        modeNames[mode as keyof typeof modeNames] || mode
      }`
    );
    setCaptureModeState(mode);
  };

  const setUseStealth = (enabled: boolean) => {
    addLog(`⚙️ ${enabled ? "Enabled" : "Disabled"} stealth mode`);
    setUseStealthState(enabled);
  };

  const setUseRealBrowser = (enabled: boolean) => {
    addLog(`⚙️ ${enabled ? "Enabled" : "Disabled"} real browser mode`);
    setUseRealBrowserState(enabled);
  };

  const setTrackNetwork = (enabled: boolean) => {
    addLog(`⚙️ ${enabled ? "Enabled" : "Disabled"} network event tracking`);
    setTrackNetworkState(enabled);
  };

  const setBrowserEngine = (engine: string) => {
    const engineNames = {
      playwright: "Playwright",
      camoufox: "Camoufox",
    };
    addLog(
      `⚙️ Changed browser engine to: ${
        engineNames[engine as keyof typeof engineNames] || engine
      }`
    );
    setBrowserEngineState(engine);
  };

  // ⚡ OPTIMIZATION: Wrap with useCallback to prevent recreation
  const clearLogs = useCallback(() => {
    setLogs([]);
    setHasErrors(false); // Reset error status when clearing logs
    setShowLogs(false); // Hide logs panel when clearing
  }, []); // ✅ No dependencies

  // ⚡ OPTIMIZATION: Wrap with useCallback to prevent recreation
  const toggleLogs = useCallback(() => {
    setShowLogs((prev) => !prev);
  }, []); // ✅ No dependencies

  // Count actual errors in logs (for badge display)
  const getErrorCount = () => {
    return logs.filter((log) => {
      const message = log.substring(log.indexOf("]") + 1).trim(); // Remove timestamp

      // Exclude summary lines that show "Failed: 0" or similar
      if (message.includes("Success:") && message.includes("Failed:")) {
        return false; // This is a summary line, not an error
      }

      return (
        message.includes("❌") ||
        message.toLowerCase().includes("error:") ||
        message.toLowerCase().includes("failed:") ||
        message.toLowerCase().includes("exception:") ||
        (message.toLowerCase().includes("error") &&
          !message.includes("✅") &&
          !message.toLowerCase().includes("no error"))
      );
    }).length;
  };

  // Tab management functions
  const openSettingsTab = () => {
    if (!openTabs.includes("settings")) {
      setOpenTabs([...openTabs, "settings"]);
    }
    setActiveTab("settings");
  };

  const closeSettingsTab = () => {
    setOpenTabs(openTabs.filter((tab) => tab !== "settings"));
    setActiveTab("main");
  };

  const openLogsTab = () => {
    if (!openTabs.includes("logs")) {
      setOpenTabs([...openTabs, "logs"]);
    }
    setActiveTab("logs");
  };

  const closeLogsTab = () => {
    setOpenTabs(openTabs.filter((tab) => tab !== "logs"));
    setActiveTab("main");
  };

  const openKeywordConfigTab = () => {
    if (!openTabs.includes("keyword-config")) {
      setOpenTabs([...openTabs, "keyword-config"]);
    }
    setActiveTab("keyword-config");
  };

  const closeKeywordConfigTab = () => {
    setOpenTabs(openTabs.filter((tab) => tab !== "keyword-config"));
    setActiveTab("main");
  };

  // Main, Sessions, URLs, and Cookies tabs are now permanent (always open), so no open/close functions needed

  const switchTab = (
    tab: "main" | "sessions" | "urls" | "cookies" | "settings" | "logs"
  ) => {
    setActiveTab(tab);
  };

  // Restart backend
  const restartBackend = async () => {
    setIsRestartingBackend(true);
    setRestartMessage("🔄 Restarting backend...");
    addLog("🔄 Restarting backend server...");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/restart", {
        method: "POST",
      });

      if (response.ok) {
        setRestartMessage("✅ Backend restarted successfully!");
        addLog("✅ Backend restarted successfully!");

        // Clear message after 3 seconds
        setTimeout(() => {
          setRestartMessage(null);
        }, 3000);
      } else {
        const error = await response.text();
        setRestartMessage(`❌ Failed to restart: ${error}`);
        addLog(`❌ Failed to restart backend: ${error}`);
      }
    } catch (error) {
      setRestartMessage(
        "❌ Backend not responding. Please restart manually using: cd backend && python3 main.py"
      );
      addLog(
        `❌ Failed to connect to backend: ${error}. Please restart manually.`
      );
    } finally {
      setIsRestartingBackend(false);
    }
  };

  // Beautify URLs - clean up formatting
  const beautifyUrls = () => {
    if (!urls.trim()) return;

    // First, insert newlines before every http:// or https:// that's not at the start
    const withSeparatedUrls = urls.replace(/(https?:\/\/)/g, "\n$1");

    // Split by newlines, spaces, commas, semicolons
    const allUrls = withSeparatedUrls
      .split(/[\n\s,;]+/)
      .map((url) => url.trim())
      .filter((url) => url.length > 0)
      .filter((url) => url.startsWith("http://") || url.startsWith("https://")); // Only valid URLs

    // Join with newlines (one URL per line)
    const beautified = allUrls.join("\n");
    setUrls(beautified);

    addLog(`✨ Beautified ${allUrls.length} URL(s)`);
  };

  // Helper function to validate and clean a string of URLs (doesn't beautify, just validates)
  const validateUrlString = (urlString: string): string => {
    if (!urlString.trim()) return "";

    // First, insert newlines before every http:// or https:// that's not at the start
    const withSeparatedUrls = urlString.replace(/(https?:\/\/)/g, "\n$1");

    // Split by newlines, spaces, commas, semicolons
    const allUrls = withSeparatedUrls
      .split(/[\n\s,;]+/)
      .map((url) => url.trim())
      .filter((url) => url.length > 0)
      .filter((url) => url.startsWith("http://") || url.startsWith("https://")); // Only valid URLs

    // Join with newlines (one URL per line) - KEEPS query params and fragments
    return allUrls.join("\n");
  };

  // Helper function to validate an array of URLs (doesn't beautify, just validates)
  const validateUrlArray = (urls: string[]): string[] => {
    return urls
      .map((url) => url.trim())
      .filter((url) => url.length > 0)
      .filter((url) => url.startsWith("http://") || url.startsWith("https://"));
  };

  // ✅ NEW FEATURE: Multiple text boxes management
  const addTextBox = () => {
    const newTextBox: TextBox = {
      id: `textbox-${Date.now()}`,
      sessionName: "",
      urls: "",
      batchTimeout: 90, // ✅ Default timeout for new text boxes
    };
    setTextBoxes([...textBoxes, newTextBox]);
    addLog(`➕ Added new text box`);
  };

  const removeTextBox = (id: string) => {
    if (textBoxes.length <= 1) {
      alert("Cannot remove the last text box!");
      return;
    }
    setTextBoxes(textBoxes.filter((box) => box.id !== id));
    addLog(`➖ Removed text box`);
  };

  const updateTextBox = (
    id: string,
    field: "sessionName" | "urls",
    value: string
  ) => {
    setTextBoxes(
      textBoxes.map((box) => (box.id === id ? { ...box, [field]: value } : box))
    );
  };

  // ✅ NEW FEATURE: Beautify all text boxes
  const beautifyAllTextBoxes = () => {
    let totalUrls = 0;
    const beautifiedTextBoxes = textBoxes.map((box) => {
      if (!box.urls.trim()) return box;

      // First, insert newlines before every http:// or https:// that's not at the start
      const withSeparatedUrls = box.urls.replace(/(https?:\/\/)/g, "\n$1");

      // Split by newlines, spaces, commas, semicolons
      const allUrls = withSeparatedUrls
        .split(/[\n\s,;]+/)
        .map((url) => url.trim())
        .filter((url) => url.length > 0)
        .filter(
          (url) => url.startsWith("http://") || url.startsWith("https://")
        ); // Only valid URLs

      totalUrls += allUrls.length;

      // Join with newlines (one URL per line)
      const beautified = allUrls.join("\n");
      return { ...box, urls: beautified };
    });

    setTextBoxes(beautifiedTextBoxes);
    addLog(
      `✨ Beautified ${totalUrls} URL(s) across ${textBoxes.length} text box(es)`
    );
  };

  // ✅ NEW FEATURE: Format timestamp for display
  const formatTimestamp = (isoString: string): string => {
    const date = new Date(isoString);
    const options: Intl.DateTimeFormatOptions = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    };
    return date.toLocaleString("en-US", options).replace(",", " at");
  };

  const copyLogs = async () => {
    try {
      const logsText = logs.join("\n");
      await navigator.clipboard.writeText(logsText);
      addLog("📋 Logs copied to clipboard!");
      // Show a temporary success message
      setTimeout(() => {
        setLogs((prev) =>
          prev.filter((log) => !log.includes("Logs copied to clipboard"))
        );
      }, 2000);
    } catch (error) {
      console.error("Failed to copy logs:", error);
      alert("Failed to copy logs to clipboard");
    }
  };

  // ========================================
  // 🔔 NOTIFICATION HELPERS
  // ========================================

  // ✅ NEW: Custom notification system (replaces browser Notification API)
  // Uses custom dialog instead of system notifications for better UX
  const showNotification = (title: string, body: string) => {
    // Use custom notification dialog instead of browser notifications
    console.log("🔔 Custom notification:", title, body);

    // Auto-detect notification type from title/body
    let type: "success" | "error" | "warning" | "info" = "info";
    const combined = `${title} ${body}`.toLowerCase();

    if (
      combined.includes("success") ||
      combined.includes("✅") ||
      combined.includes("generated") ||
      combined.includes("captured")
    ) {
      type = "success";
    } else if (
      combined.includes("error") ||
      combined.includes("❌") ||
      combined.includes("failed")
    ) {
      type = "error";
    } else if (combined.includes("warning") || combined.includes("⚠️")) {
      type = "warning";
    }

    // Show custom notification using notify() function
    return notify(body, { title, type });
  };

  // ========================================
  // 🎯 MAIN CAPTURE FUNCTION
  // ========================================

  // ⚡ OPTIMIZATION: Memoize URL list parsing to avoid re-computing on every render
  const urlList = useMemo(() => {
    return urls.split("\n").filter((url) => url.trim());
  }, [urls]);

  // ⚡ OPTIMIZATION: Memoize URL lines for line number rendering
  const urlLines = useMemo(() => {
    return urls.split("\n");
  }, [urls]);

  // ✅ NEW FEATURE: Handle multiple text boxes capture
  const handleMultipleTextBoxesCapture = async () => {
    // Validate that at least one text box has URLs
    const validTextBoxes = textBoxes.filter(
      (box) => box.urls.trim().length > 0
    );

    if (validTextBoxes.length === 0) {
      alert("Please enter URLs in at least one text box!");
      return;
    }

    // Validate all text boxes have session names
    const missingNames = validTextBoxes.filter(
      (box) => !box.sessionName.trim()
    );
    if (missingNames.length > 0) {
      alert(
        `Please provide session names for all text boxes with URLs!\n\n${missingNames.length} text box(es) missing session names.`
      );
      return;
    }

    setLoading(true);
    clearLogs();

    // ✅ NEW: Check if parallel processing is enabled
    if (enableParallelTextBoxes) {
      addLog(
        `🚀 Starting parallel capture for ${validTextBoxes.length} text box(es)`
      );
      addLog(`   ⚡ All text boxes will be processed simultaneously!`);
    } else {
      addLog(
        `🚀 Starting sequential capture for ${validTextBoxes.length} text box(es)`
      );
    }

    try {
      if (enableParallelTextBoxes) {
        // ✅ PARALLEL: Process all text boxes simultaneously
        await Promise.all(
          validTextBoxes.map(async (textBox, index) => {
            const boxNumber = index + 1;

            addLog(
              `\n📦 Processing Text Box ${boxNumber}/${validTextBoxes.length}`
            );
            addLog(`   📝 Session Name: ${textBox.sessionName}`);

            // Parse URLs from this text box
            const boxUrls = textBox.urls
              .split("\n")
              .map((url) => url.trim())
              .filter((url) => url.length > 0)
              .filter(
                (url) => url.startsWith("http://") || url.startsWith("https://")
              );

            if (boxUrls.length === 0) {
              addLog(`   ⚠️ No valid URLs found, skipping...`);
              return;
            }

            addLog(`   🔗 URLs: ${boxUrls.length}`);
            addLog(`   ⏱️ Batch Timeout: ${textBox.batchTimeout || 90}s`);

            // Capture screenshots for this text box
            await captureSingleTextBox(textBox, boxUrls);
          })
        );
      } else {
        // ✅ SEQUENTIAL: Process each text box one by one
        for (let i = 0; i < validTextBoxes.length; i++) {
          const textBox = validTextBoxes[i];
          const boxNumber = i + 1;

          addLog(
            `\n📦 Processing Text Box ${boxNumber}/${validTextBoxes.length}`
          );
          addLog(`   📝 Session Name: ${textBox.sessionName}`);

          // Parse URLs from this text box
          const boxUrls = textBox.urls
            .split("\n")
            .map((url) => url.trim())
            .filter((url) => url.length > 0)
            .filter(
              (url) => url.startsWith("http://") || url.startsWith("https://")
            );

          if (boxUrls.length === 0) {
            addLog(`   ⚠️ No valid URLs found, skipping...`);
            continue;
          }

          addLog(`   🔗 URLs: ${boxUrls.length}`);
          addLog(`   ⏱️ Batch Timeout: ${textBox.batchTimeout || 90}s`);

          // Capture screenshots for this text box
          await captureSingleTextBox(textBox, boxUrls);
        }
      }

      addLog(`\n✅ Batch capture complete!`);
      addLog(`   📊 Processed ${validTextBoxes.length} text box(es)`);
    } catch (error: any) {
      addLog(`❌ Batch capture failed: ${error.message}`);
      alert(`Batch capture failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ✅ NEW FEATURE: Capture screenshots for a single text box
  const captureSingleTextBox = async (textBox: TextBox, urls: string[]) => {
    const captureStartTime = Date.now();

    try {
      addLog(`   📸 Capturing ${urls.length} URL(s)...`);

      const controller = new AbortController();
      const timeoutId = setTimeout(
        () => controller.abort(),
        config.requestTimeout
      );

      const response = await fetch(
        `${config.apiBaseUrl}/api/screenshots/capture`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            urls: urls,
            viewport_width: 1366, // Standard laptop resolution (most common)
            viewport_height: 768,
            capture_mode: captureMode,
            use_stealth: useStealth,
            use_real_browser: useRealBrowser,
            browser_engine: browserEngine,
            base_url: baseUrl,
            words_to_remove: JSON.stringify(wordsToRemove),
            cookies: cookies,
            local_storage: localStorageData,
            track_network: trackNetwork,
            segment_overlap: segmentOverlap,
            segment_scroll_delay: segmentScrollDelay,
            segment_max_segments: segmentMaxSegments,
            segment_skip_duplicates: segmentSkipDuplicates,
            segment_smart_lazy_load: segmentSmartLazyLoad,
            batch_timeout: textBox.batchTimeout || 90, // ✅ NEW: Send per-text-box timeout to backend
          }),
          signal: controller.signal,
        }
      );

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const successCount = data.results.filter(
        (r: any) => r.status === "success"
      ).length;
      const failCount = data.results.filter(
        (r: any) => r.status === "error"
      ).length;

      addLog(`   ✅ Success: ${successCount}, ❌ Failed: ${failCount}`);

      // Create session with custom name
      if (successCount > 0) {
        const sessionScreenshots = data.results
          .filter((r: any) => r.status === "success")
          .flatMap((r: any) => {
            if (r.screenshot_paths && r.screenshot_paths.length > 0) {
              return r.screenshot_paths.map((path: string, idx: number) => ({
                filename: path.split("/").pop() || path,
                path: path,
                url: r.url,
                timestamp: new Date().toISOString(),
                quality_score: r.quality_score,
                segments: r.segment_count,
              }));
            } else if (r.screenshot_path) {
              return [
                {
                  filename:
                    r.screenshot_path.split("/").pop() || r.screenshot_path,
                  path: r.screenshot_path,
                  url: r.url,
                  timestamp: new Date().toISOString(),
                  quality_score: r.quality_score,
                },
              ];
            }
            return [];
          });

        const captureDuration = Date.now() - captureStartTime;
        const sessionNumber = sessions.length + 1;

        const newSession: Session = {
          id: `session-${Date.now()}`,
          name: textBox.sessionName, // ✅ Use custom session name from textBox
          defaultName: `Session ${sessionNumber}`,
          timestamp: new Date().toISOString(),
          screenshots: sessionScreenshots,
          urls: urls,
          duration: captureDuration,
          settings: {
            captureMode: captureMode,
            useStealth: useStealth,
            useRealBrowser: useRealBrowser,
          },
        };

        setSessions([newSession, ...sessions]);
        addLog(`   🗂️ Session created: ${textBox.sessionName}`);
        addLog(`   📅 Created: ${formatTimestamp(newSession.timestamp)}`);
        addLog(`   📊 Total segments: ${sessionScreenshots.length}`);

        // ✅ NEW: Auto-generate Word document with session name
        await generateWordDocumentForSession(
          textBox.sessionName,
          sessionScreenshots
        );
      }
    } catch (error: any) {
      addLog(`   ❌ Error: ${error.message}`);
      throw error;
    }
  };

  const handleCapture = async () => {
    // ✅ NEW FEATURE: Check if multiple text boxes mode is enabled
    if (enableMultipleTextBoxes) {
      // Process each text box separately
      await handleMultipleTextBoxesCapture();
      return;
    }

    // ✅ EXISTING: Single text box mode
    // Use memoized urlList instead of re-parsing

    if (urlList.length === 0) {
      alert("Please enter at least one URL");
      return;
    }

    // Validate URLs
    const invalidUrls = urlList.filter((url) => {
      try {
        const parsedUrl = new URL(url);
        // Only allow http and https protocols
        if (!["http:", "https:"].includes(parsedUrl.protocol)) {
          return true; // Invalid
        }
        return false; // Valid
      } catch {
        return true; // Invalid
      }
    });

    if (invalidUrls.length > 0) {
      const message = `Invalid URL(s) detected:\n\n${invalidUrls.join(
        "\n"
      )}\n\nPlease use full URLs with http:// or https://\n\nExamples:\n- https://example.com\n- https://google.com\n- http://localhost:3000`;
      alert(message);
      addLog(`❌ Invalid URLs: ${invalidUrls.join(", ")}`);
      return;
    }

    setLoading(true);
    setResults([]);
    setProgress({ current: 0, total: urlList.length });
    clearLogs();
    addLog(`Starting capture for ${urlList.length} URLs`);

    // Track start time for session duration
    const captureStartTime = Date.now();

    // Log capture mode
    const modeNames = {
      viewport: "Viewport only (single screenshot)",
      fullpage: "Full page (single tall screenshot)",
      segmented: "Segmented (multiple viewport screenshots)",
    };
    addLog(`Capture mode: ${modeNames[captureMode as keyof typeof modeNames]}`);

    if (captureMode === "segmented") {
      addLog(`  ├─ Overlap: ${segmentOverlap}%`);
      addLog(`  ├─ Scroll delay: ${segmentScrollDelay}ms`);
      addLog(`  ├─ Max segments: ${segmentMaxSegments}`);
      addLog(`  ├─ Skip duplicates: ${segmentSkipDuplicates ? "ON" : "OFF"}`);
      addLog(`  └─ Smart lazy-load: ${segmentSmartLazyLoad ? "ON" : "OFF"}`);
    }

    addLog(`Stealth mode: ${useStealth ? "ON (anti-bot detection)" : "OFF"}`);
    addLog(
      `Real browser: ${
        useRealBrowser ? "ON (visible window)" : "OFF (headless)"
      }`
    );
    addLog(
      `Network tracking: ${trackNetwork ? "ON (capturing HTTP events)" : "OFF"}`
    );

    try {
      addLog("Sending request to backend...");

      // ✅ FIXED: Use config for API URL and add timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(
        () => controller.abort(),
        config.requestTimeout
      );

      try {
        const response = await fetch(
          `${config.apiBaseUrl}/api/screenshots/capture`, // ✅ From config
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            signal: controller.signal, // ✅ Add timeout support
            body: JSON.stringify({
              urls: urlList,
              viewport_width: 1366, // Standard laptop resolution (most common)
              viewport_height: 768,
              capture_mode: captureMode,
              use_stealth: useStealth,
              use_real_browser: useRealBrowser,
              browser_engine: browserEngine, // "playwright" or "camoufox"
              base_url: baseUrl,
              words_to_remove: JSON.stringify(wordsToRemove), // ✅ Send as JSON array of WordTransformation objects
              cookies: cookies, // Add cookies for authentication
              local_storage: localStorageData, // Add localStorage for authentication
              segment_overlap: segmentOverlap,
              segment_scroll_delay: segmentScrollDelay,
              segment_max_segments: segmentMaxSegments,
              segment_skip_duplicates: segmentSkipDuplicates,
              segment_smart_lazy_load: segmentSmartLazyLoad,
              track_network: trackNetwork, // ✅ NEW: Network event tracking
            }),
          }
        );

        clearTimeout(timeoutId); // ✅ Clear timeout on success

        addLog("Received response from backend");

        // Log raw response for debugging
        const responseText = await response.text();
        addLog(`Raw response: ${responseText.substring(0, 200)}...`);
        console.log("Full backend response:", responseText);

        let data;
        try {
          data = JSON.parse(responseText);
        } catch (parseError: any) {
          throw new Error(`Failed to parse JSON: ${parseError.message}`);
        }

        // Safety check
        if (!data || !data.results || !Array.isArray(data.results)) {
          throw new Error(
            `Invalid response from backend: ${JSON.stringify(data)}`
          );
        }

        addLog(`Parsed ${data.results.length} results successfully`);
        console.log("Parsed results:", data.results);

        setResults(data.results);
        addLog(`Capture complete: ${data.results.length} results received`);

        if (data.cancelled) {
          addLog("⚠️ Operation was cancelled by user");
          alert("Screenshot capture was cancelled");
        } else {
          const successCount = data.results.filter(
            (r: ScreenshotResult) => r.status === "success"
          ).length;
          const failedCount = data.results.filter(
            (r: ScreenshotResult) => r.status === "failed"
          ).length;
          const cancelledCount = data.results.filter(
            (r: ScreenshotResult) => r.status === "cancelled"
          ).length;
          addLog(
            `✅ Success: ${successCount}, ❌ Failed: ${failedCount}, ⏹️ Cancelled: ${cancelledCount}`
          );

          // ✅ Show custom dialog based on URL count
          console.log(
            `🔍 Dialog check: urlList.length=${urlList.length}, successCount=${successCount}`
          );
          if (urlList.length === 1 && successCount === 1) {
            // Single URL - show custom dialog
            console.log("🔔 Showing single URL dialog");
            showNotification(
              "📸 Screenshot Captured",
              `Screenshot captured successfully for ${urlList[0]}`
            );
            // Show custom dialog after notification
            await showCustomAlert(
              "📸 Screenshot Captured",
              `Screenshot captured successfully!\n\nURL: ${urlList[0]}`
            );
          } else if (urlList.length > 1 && successCount > 0) {
            // Multiple URLs - show custom dialog with summary
            console.log("🔔 Showing multiple URLs dialog");
            showNotification(
              "📸 Screenshots Captured",
              `${successCount} of ${urlList.length} screenshots captured successfully`
            );
            // Show custom dialog after notification
            const summary = `✅ Success: ${successCount}\n❌ Failed: ${failedCount}${
              cancelledCount > 0 ? `\n⏹️ Cancelled: ${cancelledCount}` : ""
            }`;
            await showCustomAlert(
              "📸 Screenshots Captured",
              `Capture complete!\n\n${summary}\n\nTotal: ${urlList.length} URLs`
            );
          } else {
            console.log("⚠️ No dialog shown (conditions not met)");
          }

          // Create session if there are successful screenshots
          if (successCount > 0) {
            const captureDuration = Date.now() - captureStartTime;

            // Build screenshots array from successful results
            const sessionScreenshots: Screenshot[] = data.results
              .filter((r: ScreenshotResult) => r.status === "success")
              .flatMap((r: ScreenshotResult) => {
                if (r.screenshot_paths && r.screenshot_paths.length > 0) {
                  // Segmented capture - multiple screenshots
                  return r.screenshot_paths.map(
                    (path: string, index: number) => ({
                      filename: path.split("/").pop() || path,
                      path: path,
                      url: r.url,
                      timestamp: new Date().toISOString(),
                      quality_score: r.quality_score,
                      segments: r.screenshot_paths.length,
                    })
                  );
                } else if (r.screenshot_path) {
                  // Single screenshot
                  return [
                    {
                      filename:
                        r.screenshot_path.split("/").pop() || r.screenshot_path,
                      path: r.screenshot_path,
                      url: r.url,
                      timestamp: new Date().toISOString(),
                      quality_score: r.quality_score,
                    },
                  ];
                }
                return [];
              });

            // Create session
            const newSession = createSession(
              sessionScreenshots,
              urlList,
              captureDuration
            );
            addLog(`🗂️ Session created: ${newSession.name}`);
            addLog(`   📅 Created: ${formatTimestamp(newSession.timestamp)}`);
            addLog(`   📊 Total segments: ${sessionScreenshots.length}`);
          }
        }
      } catch (fetchError: any) {
        // ✅ FIXED: Handle timeout errors specifically
        if (fetchError.name === "AbortError") {
          throw new Error(
            `Request timed out after ${
              config.requestTimeout / 1000
            } seconds. The backend may be slow or unresponsive.`
          );
        }
        throw fetchError;
      }
    } catch (error: any) {
      console.error("Error:", error);
      const errorMessage = error?.message || String(error);
      addLog(`❌ Error: ${errorMessage}`);
      addLog(`❌ Stack: ${error?.stack || "No stack trace"}`);
      alert(
        `Error capturing screenshots: ${errorMessage}\n\nCheck logs for details.`
      );
    } finally {
      setLoading(false);
      addLog("Capture operation finished");
    }
  };

  // ⚡ OPTIMIZATION: Wrap with useCallback to prevent recreation
  const handleStop = useCallback(async () => {
    try {
      addLog("🛑 Stop button clicked - sending cancel request...");
      await fetch(`${config.apiBaseUrl}/api/screenshots/cancel`, {
        // ✅ Use config
        method: "POST",
      });
      addLog("Cancel request sent to backend");
    } catch (error) {
      console.error("Error stopping capture:", error);
      addLog(`❌ Error sending cancel request: ${error}`);
    }
  }, [addLog]); // ✅ Stable dependency

  const handleRetry = async (url: string) => {
    try {
      addLog(`🔄 Retrying screenshot for: ${url}`);
      const response = await fetch(
        `http://127.0.0.1:8000/api/screenshots/retry?url=${encodeURIComponent(
          url
        )}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();
      addLog(`✅ Retry completed for: ${url} - Status: ${result.status}`);

      // Update results
      setResults((prev) => prev.map((r) => (r.url === url ? result : r)));
    } catch (error) {
      console.error("Error:", error);
      addLog(`❌ Retry failed for: ${url} - ${error}`);
      alert("Error retrying screenshot");
    }
  };

  const handleOpenFile = async (filePath: string) => {
    try {
      addLog(`📂 Opening file: ${filePath}`);
      const response = await fetch(
        `http://127.0.0.1:8000/api/screenshots/open-file?path=${encodeURIComponent(
          filePath
        )}`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        addLog(`✅ File opened successfully`);
      } else {
        throw new Error("Failed to open file");
      }
    } catch (error) {
      console.error("Error:", error);
      addLog(`❌ Failed to open file: ${error}`);
      alert("Error opening file");
    }
  };

  const handleOpenFolder = async (filePath: string) => {
    try {
      addLog(`📁 Opening folder for: ${filePath}`);
      const response = await fetch(
        `http://127.0.0.1:8000/api/screenshots/open-folder?path=${encodeURIComponent(
          filePath
        )}`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        addLog(`✅ Folder opened successfully`);
      } else {
        throw new Error("Failed to open folder");
      }
    } catch (error) {
      console.error("Error:", error);
      addLog(`❌ Failed to open folder: ${error}`);
      alert("Error opening folder");
    }
  };

  // ✅ NEW: Generate Word document for a specific session with session name as filename
  const generateWordDocumentForSession = async (
    sessionName: string,
    sessionScreenshots: Screenshot[]
  ) => {
    try {
      // Collect all screenshot paths
      const screenshotPaths = sessionScreenshots.map((s) => s.path);

      if (screenshotPaths.length === 0) {
        addLog(`   ⚠️ No screenshots to include in document`);
        return;
      }

      addLog(
        `   📄 Generating Word document with ${screenshotPaths.length} screenshot(s)...`
      );

      // Use session name as document filename
      const documentName = `${sessionName}.docx`;

      // ✅ NEW: Build output path with optional folder
      let outputPath = "~/Desktop/ARC DEALERS SCREENSHOT WORD DOCS";
      if (wordDocFolderName.trim()) {
        outputPath += `/${wordDocFolderName.trim()}`;
        addLog(`   📁 Saving to folder: ${wordDocFolderName.trim()}`);
      }
      outputPath += `/${documentName}`;

      const response = await fetch(
        "http://127.0.0.1:8000/api/document/generate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            screenshot_paths: screenshotPaths,
            output_path: outputPath,
            title: sessionName,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        addLog(`   ❌ Document generation failed: ${response.status}`);
        return;
      }

      const data = await response.json();

      if (data.status === "success") {
        addLog(`   ✅ Document generated: ${documentName}`);

        // Show notification
        showNotification(
          "📄 Word Document Generated",
          `Document saved: ${documentName}`
        );
      } else {
        addLog(`   ❌ Document generation failed: ${data.error}`);
      }
    } catch (error: any) {
      addLog(`   ❌ Document generation error: ${error.message}`);
    }
  };

  const handleGenerateDocument = async () => {
    console.log("🔍 DEBUG: handleGenerateDocument called");

    // ✅ FIX: Close ALL modals before showing alert to prevent overlay interference
    setShowLoginModal(false);
    setShowCookieEditor(false);
    setShowExportModal(false);
    setShowSecurityAudit(false);
    setShowFormatExport(false);
    setShowFormatImport(false);

    // Wait for React to remove modal overlays from DOM
    await new Promise((resolve) => setTimeout(resolve, 50));
    console.log("🔍 DEBUG: All modals closed, DOM cleaned");

    // Collect all screenshots (including all segments from segmented captures)
    const successfulScreenshots: string[] = [];

    results
      .filter((r) => r.status === "success")
      .forEach((r) => {
        // If segmented capture, add all segments
        if (r.screenshot_paths && r.screenshot_paths.length > 0) {
          successfulScreenshots.push(...r.screenshot_paths);
        }
        // Otherwise, add single screenshot
        else if (r.screenshot_path) {
          successfulScreenshots.push(r.screenshot_path);
        }
      });

    console.log(`🔍 DEBUG: Found ${successfulScreenshots.length} screenshots`);

    if (successfulScreenshots.length === 0) {
      alert("No successful screenshots to include in document");
      return;
    }

    try {
      addLog(
        `📄 Generating Word document with ${successfulScreenshots.length} screenshots...`
      );

      // Generate document name from first screenshot filename
      // Remove segment numbers (_001, _002, etc.) and .png extension
      const firstScreenshot = successfulScreenshots[0];
      const firstFilename =
        firstScreenshot.split("/").pop() || "screenshots_report";
      const documentName =
        firstFilename
          .replace(/_\d{3}\.png$/, "") // Remove _001.png, _002.png, etc.
          .replace(/\.png$/, "") + // Remove .png
        ".docx";

      console.log(`🔍 DEBUG: Document name: ${documentName}`);
      console.log(`🔍 DEBUG: Sending request to backend...`);

      const response = await fetch(
        "http://127.0.0.1:8000/api/document/generate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            screenshot_paths: successfulScreenshots,
            output_path: `~/Desktop/ARC DEALERS SCREENSHOT WORD DOCS/${documentName}`,
            title: "Screenshot Report",
          }),
        }
      );

      console.log(`🔍 DEBUG: Response status: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ DEBUG: Response error: ${errorText}`);
        addLog(
          `❌ Document generation failed: ${response.status} ${errorText}`
        );

        // ✅ FIX: Use setTimeout to ensure alert stays visible
        setTimeout(() => {
          alert(`❌ Error: ${response.status} - ${errorText}`);
        }, 100);
        return;
      }

      const data = await response.json();
      console.log(`🔍 DEBUG: Response data:`, data);

      if (data.status === "success") {
        addLog(`✅ Document generated successfully: ${data.output_path}`);
        console.log(`✅ DEBUG: Document generated successfully!`);
        console.log(`📄 DEBUG: Output path: ${data.output_path}`);

        // Show notification
        showNotification(
          "📄 Word Document Generated",
          `Document saved: ${documentName}`
        );

        // ✅ FIX: Use custom dialog instead of browser alert
        console.log(`🔍 DEBUG: About to show success dialog...`);
        await showCustomAlert(
          "✅ Document Generated Successfully!",
          `Saved to:\n${data.output_path}`
        );
        console.log(`🔍 DEBUG: User acknowledged dialog`);
      } else {
        console.error(`❌ DEBUG: Generation failed: ${data.error}`);
        addLog(`❌ Document generation failed: ${data.error}`);

        // ✅ FIX: Use setTimeout to ensure alert stays visible
        setTimeout(() => {
          alert(`❌ Error: ${data.error}`);
        }, 100);
      }
    } catch (error) {
      console.error("❌ DEBUG: Exception caught:", error);
      console.error(
        "❌ DEBUG: Error stack:",
        error instanceof Error ? error.stack : "No stack"
      );
      addLog(`❌ Error generating document: ${error}`);

      // ✅ FIX: Use setTimeout to ensure alert stays visible
      setTimeout(() => {
        const errorMessage = `❌ Error generating document: ${error}\n\nCheck console for details.`;
        console.log(`🔍 DEBUG: About to show error alert: ${errorMessage}`);
        alert(errorMessage);
        console.log(`🔍 DEBUG: Error alert shown`);
      }, 100);
    }

    console.log(`🔍 DEBUG: handleGenerateDocument function completed`);
  };

  // ✅ REMOVED: Test notification function (no longer needed)

  // Catch any rendering errors
  try {
    return (
      <div className="container">
        <div className="header">
          <h1>📸 Screenshot Tool</h1>

          <div className="header-controls">
            {/* Settings Toggle Button */}
            <button
              className={`settings-toggle ${
                openTabs.includes("settings") ? "active" : ""
              }`}
              onClick={openSettingsTab}
              aria-label="Open settings"
              title="Open settings"
            >
              <span className="icon-settings">⚙️</span>
            </button>

            {/* Logs Toggle Button */}
            <button
              className={`logs-toggle ${hasErrors ? "error" : "success"} ${
                openTabs.includes("logs") ? "active" : ""
              }`}
              onClick={openLogsTab}
              aria-label="Open logs"
              title={
                hasErrors
                  ? `⚠️ ${getErrorCount()} error(s) detected - Click to view logs`
                  : "Show logs (all good!)"
              }
            >
              <div className="logs-icon">
                {hasErrors ? (
                  <span className="icon-error">⚠️</span>
                ) : (
                  <span className="icon-success">⏱️</span>
                )}
              </div>
              {hasErrors && getErrorCount() > 0 && (
                <span className="error-badge">{getErrorCount()}</span>
              )}
            </button>

            {/* Dark Mode Toggle Button */}
            <button
              className="dark-mode-toggle"
              onClick={toggleDarkMode}
              aria-label="Toggle dark mode"
              title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              <div
                className={`toggle-icon ${darkMode ? "dark" : "light"} ${
                  isToggling ? "celebrating" : ""
                }`}
              >
                {darkMode ? (
                  <span className="icon-moon">🌙</span>
                ) : (
                  <span className="icon-sun">☀️</span>
                )}
              </div>
            </button>
          </div>
        </div>

        {renderError && (
          <div
            style={{
              background: "#ffebee",
              border: "2px solid #f44336",
              padding: "15px",
              borderRadius: "8px",
              margin: "20px 0",
              color: "#c62828",
            }}
          >
            <h3>⚠️ Render Error</h3>
            <p>{renderError}</p>
            <button onClick={() => setRenderError(null)}>Dismiss</button>
          </div>
        )}

        {/* Tab Bar - Chrome Style */}
        <div className="tab-bar">
          {openTabs.map((tab) => (
            <div
              key={tab}
              className={`tab ${activeTab === tab ? "active" : ""} ${
                tab === "logs" && hasErrors ? "tab-error" : ""
              }`}
              onClick={() => switchTab(tab)}
            >
              <span className="tab-label">
                {tab === "main"
                  ? "📸 Main"
                  : tab === "sessions"
                  ? "🗂️ Sessions"
                  : tab === "urls"
                  ? "📁 URLs"
                  : tab === "cookies"
                  ? "🔐 Auth Data"
                  : tab === "settings"
                  ? "⚙️ Settings"
                  : tab === "logs"
                  ? "⏱️ Logs"
                  : "🔤 Keyword Config"}
                {tab === "logs" && hasErrors && getErrorCount() > 0 && (
                  <span className="tab-error-badge">{getErrorCount()}</span>
                )}
                {tab === "sessions" &&
                  sessions.length > 0 &&
                  activeTab !== "sessions" && (
                    <span className="tab-count-badge">{sessions.length}</span>
                  )}
              </span>
              {/* No close button for Main, Sessions, URLs, and Cookies tabs - they are permanent */}
              {tab === "settings" && (
                <button
                  className="tab-close"
                  onClick={(e) => {
                    e.stopPropagation();
                    closeSettingsTab();
                  }}
                  aria-label="Close settings tab"
                >
                  ✕
                </button>
              )}
              {tab === "logs" && (
                <button
                  className="tab-close"
                  onClick={(e) => {
                    e.stopPropagation();
                    closeLogsTab();
                  }}
                  aria-label="Close logs tab"
                >
                  ✕
                </button>
              )}
              {tab === "keyword-config" && (
                <button
                  className="tab-close"
                  onClick={(e) => {
                    e.stopPropagation();
                    closeKeywordConfigTab();
                  }}
                  aria-label="Close keyword config tab"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "logs" ? (
          <div className="tab-content">
            <div className="logs-section">
              <div className="logs-header">
                <h2>⏱️ Logs</h2>
                <div className="logs-buttons">
                  <button onClick={copyLogs} className="copy-logs-btn">
                    📋 Copy Logs
                  </button>
                  <button onClick={clearLogs} className="clear-logs-btn">
                    🗑️ Clear Logs
                  </button>
                </div>
              </div>
              <div className="logs-container">
                {logs.length > 0 ? (
                  logs.map((log, index) => (
                    <div key={index} className="log-entry">
                      {log}
                    </div>
                  ))
                ) : (
                  <div className="log-entry">
                    No logs yet. Start capturing to see logs.
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : activeTab === "keyword-config" ? (
          <div className="tab-content">
            <div className="settings-content">
              {/* Base URL for Screenshot Naming */}
              <div className="settings-section">
                <h3>📍 Base URL (Optional)</h3>
                <input
                  type="text"
                  className="base-url-input"
                  placeholder="https://example.com"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  disabled={loading}
                />
                <p className="option-hint">
                  💡 Used for screenshot naming. Path after base URL becomes
                  filename in PascalCase.
                  <br />
                  Example: Base URL <code>https://example.com/</code> + URL{" "}
                  <code>
                    https://example.com/accounting/autoPostingSettings
                  </code>{" "}
                  = <code>Accounting_AutoPostingSettings.png</code>
                </p>
              </div>

              {/* Words to Remove from Naming */}
              <div className="settings-section">
                <h3>🧹 Word Transformations</h3>
                <div className="tag-input-container">
                  {/* Display existing transformation tags */}
                  {wordsToRemove.map((transform, index) => (
                    <div
                      key={index}
                      className={`word-tag word-tag-${transform.type}`}
                      onClick={() => openWordEditor(index)}
                      style={{ cursor: "pointer" }}
                      title="Click to edit"
                    >
                      <span className="word-part">{transform.word}</span>
                      <span className="arrow">→</span>
                      <span className="replacement-part">
                        {transform.type === "remove"
                          ? "[remove]"
                          : transform.type === "space"
                          ? "[space]"
                          : transform.replacement}
                      </span>
                      <button
                        className="word-tag-remove"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeWordToRemove(index);
                        }}
                        disabled={loading}
                        title="Delete"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  {/* Input for adding new transformations */}
                  <input
                    type="text"
                    className="tag-input"
                    placeholder={
                      wordsToRemove.length === 0
                        ? 'word or word:"replacement"'
                        : "Add more..."
                    }
                    value={wordInput}
                    onChange={(e) => setWordInput(e.target.value)}
                    onKeyDown={handleWordInputKeyDown}
                    onBlur={() => {
                      if (wordInput.trim()) {
                        addWordToRemove(wordInput);
                      }
                    }}
                    disabled={loading}
                  />
                </div>
                <p className="option-hint">
                  💡 <strong>Syntax:</strong> <code>word</code> (space),{" "}
                  <code>word:""</code> (remove), <code>word:"text"</code>{" "}
                  (custom)
                  <br />
                  <strong>Examples:</strong> <code>dse-v2</code> •{" "}
                  <code>.png:""</code> • <code>Accounting:"Sales"</code>
                  <br />
                  Click tag to edit • Press <strong>Enter</strong> or{" "}
                  <strong>,</strong> to add
                </p>
              </div>
            </div>
          </div>
        ) : activeTab === "sessions" ? (
          <div className="tab-content">
            <div className="sessions-section">
              <div className="sessions-header">
                <h2>🗂️ Session History</h2>
                <div className="sessions-actions">
                  {sessions.length > 0 && (
                    <>
                      <button
                        onClick={selectAllSessions}
                        className="session-action-btn"
                      >
                        ☑ Select All
                      </button>
                      <button
                        onClick={deselectAllSessions}
                        className="session-action-btn"
                      >
                        ☐ Deselect All
                      </button>
                      {selectedSessions.size > 0 && (
                        <button
                          onClick={deleteSelectedSessions}
                          className="session-action-btn delete-btn"
                          disabled={isDeletingSession}
                          title={
                            isDeletingSession
                              ? "Deletion in progress..."
                              : "Delete selected sessions"
                          }
                        >
                          {isDeletingSession
                            ? "⏳ Deleting..."
                            : `🗑️ Delete Selected (${selectedSessions.size})`}
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>

              <div className="sessions-container">
                {sessions.length === 0 ? (
                  <div className="no-sessions">
                    <p>🗂️ No sessions yet.</p>
                    <p>Capture screenshots to create your first session!</p>
                  </div>
                ) : (
                  sessions.map((session) => (
                    <div key={session.id} className="session-card">
                      <div className="session-card-header">
                        <input
                          type="checkbox"
                          className="session-checkbox"
                          checked={selectedSessions.has(session.id)}
                          onChange={() => toggleSessionSelection(session.id)}
                        />

                        {editingSessionId === session.id ? (
                          <div className="session-name-edit">
                            <input
                              type="text"
                              className="session-name-input"
                              value={editingSessionName}
                              onChange={(e) =>
                                setEditingSessionName(e.target.value)
                              }
                              onKeyDown={(e) =>
                                handleSessionNameKeyDown(e, session.id)
                              }
                              onBlur={() => saveSessionName(session.id)}
                              autoFocus
                            />
                            <button
                              className="session-name-save"
                              onClick={() => saveSessionName(session.id)}
                              title="Save"
                            >
                              ✓
                            </button>
                            <button
                              className="session-name-cancel"
                              onClick={cancelEditingSession}
                              title="Cancel"
                            >
                              ✗
                            </button>
                            {sessionNameError && (
                              <span className="session-name-error">
                                {sessionNameError}
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="session-name-display">
                            <h3 className="session-name">{session.name}</h3>
                            <button
                              className="session-name-edit-btn"
                              onClick={() => startEditingSession(session.id)}
                              title="Rename session"
                            >
                              ✏️
                            </button>
                          </div>
                        )}
                      </div>

                      <div className="session-info">
                        <span className="session-stat">
                          📅 Created: {formatTimestamp(session.timestamp)}
                        </span>
                        <span className="session-stat">
                          📊 Total segments: {session.screenshots.length}
                        </span>
                        <span className="session-stat">
                          📸 Screenshots: {session.screenshots.length}
                        </span>
                        <span className="session-stat">
                          ⏱️ Duration: {Math.round(session.duration / 1000)}s
                        </span>
                      </div>

                      {/* ✅ NEW: Show screenshot storage location */}
                      {session.screenshots.length > 0 && (
                        <div className="session-location">
                          <span
                            className="session-stat"
                            style={{ fontSize: "13px", color: "#888" }}
                          >
                            📁 Location:{" "}
                            {session.screenshots[0].path
                              .split("/")
                              .slice(0, -1)
                              .join("/")}
                          </span>
                        </div>
                      )}

                      <div className="session-settings">
                        <span className="session-setting">
                          📸 {session.settings.captureMode}
                        </span>
                        {session.settings.useStealth && (
                          <span className="session-setting">🥷 Stealth</span>
                        )}
                        {session.settings.useRealBrowser && (
                          <span className="session-setting">
                            🌐 Real Browser
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>

              {selectedSessions.size > 0 && (
                <div className="sessions-footer">
                  <p>
                    📊 Selected: {selectedSessions.size} session(s) |{" "}
                    {sessions
                      .filter((s) => selectedSessions.has(s.id))
                      .reduce((sum, s) => sum + s.screenshots.length, 0)}{" "}
                    screenshot(s)
                  </p>
                  <button className="create-doc-btn" disabled>
                    📄 Create Word Doc from Selected (Coming Soon)
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : activeTab === "urls" ? (
          <div className="tab-content">
            <div className="urls-section">
              <div className="urls-header">
                <h2>📁 URL Library</h2>
                <div className="urls-header-actions">
                  <button
                    onClick={removeDuplicateUrls}
                    className="clean-duplicates-btn"
                    title="Remove duplicate URLs from all folders"
                  >
                    🧹 Clean Duplicates
                  </button>
                  <div className="new-folder-form">
                    <input
                      type="text"
                      className="new-folder-input"
                      placeholder="New folder name..."
                      value={newFolderName}
                      onChange={(e) => setNewFolderName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          createFolder();
                        }
                      }}
                    />
                    <button
                      onClick={createFolder}
                      className="create-folder-btn"
                    >
                      + New Folder
                    </button>
                  </div>
                </div>
              </div>

              <div className="folders-container">
                {urlFolders.length === 0 ? (
                  <div className="no-folders">
                    <p>📁 No folders yet.</p>
                    <p>Create your first folder to organize URLs!</p>
                  </div>
                ) : (
                  urlFolders.map((folder) => (
                    <div key={folder.id} className="folder-card">
                      <div className="folder-header">
                        <button
                          className="folder-expand-btn"
                          onClick={() => toggleFolderExpanded(folder.id)}
                        >
                          {expandedFolders.has(folder.id) ? "▼" : "▶"}
                        </button>

                        {editingFolderId === folder.id ? (
                          <div className="folder-name-edit">
                            <input
                              type="text"
                              className="folder-name-input"
                              value={editingFolderName}
                              onChange={(e) =>
                                setEditingFolderName(e.target.value)
                              }
                              onKeyDown={(e) => {
                                if (e.key === "Enter") {
                                  e.preventDefault();
                                  saveFolderName(folder.id);
                                } else if (e.key === "Escape") {
                                  e.preventDefault();
                                  cancelEditingFolder();
                                }
                              }}
                              onBlur={() => saveFolderName(folder.id)}
                              autoFocus
                            />
                            <button
                              className="folder-name-save"
                              onClick={() => saveFolderName(folder.id)}
                              title="Save"
                            >
                              ✓
                            </button>
                            <button
                              className="folder-name-cancel"
                              onClick={cancelEditingFolder}
                              title="Cancel"
                            >
                              ✗
                            </button>
                            {folderNameError && (
                              <span className="folder-name-error">
                                {folderNameError}
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="folder-name-display">
                            <h3 className="folder-name">
                              📂 {folder.name} ({folder.urls.length})
                            </h3>
                            <button
                              className="folder-edit-btn"
                              onClick={() => startEditingFolder(folder.id)}
                              title="Rename folder"
                            >
                              ✏️
                            </button>
                            <button
                              className="folder-delete-btn"
                              onClick={() => deleteFolder(folder.id)}
                              title="Delete folder"
                            >
                              🗑️
                            </button>
                          </div>
                        )}
                      </div>

                      {expandedFolders.has(folder.id) && (
                        <div className="folder-content">
                          {/* Toolbar: Select All, Search, Sort */}
                          {folder.urls.length > 0 && (
                            <div className="folder-toolbar">
                              <div className="toolbar-left">
                                <label className="select-all-checkbox">
                                  <input
                                    type="checkbox"
                                    checked={
                                      (selectedUrls[folder.id]?.size || 0) ===
                                      folder.urls.length
                                    }
                                    onChange={() => {
                                      if (
                                        (selectedUrls[folder.id]?.size || 0) ===
                                        folder.urls.length
                                      ) {
                                        deselectAllUrls(folder.id);
                                      } else {
                                        selectAllUrls(folder.id);
                                      }
                                    }}
                                  />
                                  <span>
                                    {(selectedUrls[folder.id]?.size || 0) ===
                                    folder.urls.length
                                      ? "Deselect All"
                                      : "Select All"}
                                  </span>
                                </label>

                                <input
                                  type="text"
                                  className="search-input"
                                  placeholder="Search URLs..."
                                  value={searchQuery[folder.id] || ""}
                                  onChange={(e) =>
                                    setSearchQuery({
                                      ...searchQuery,
                                      [folder.id]: e.target.value,
                                    })
                                  }
                                />
                              </div>

                              <div className="toolbar-right">
                                <select
                                  className="sort-select"
                                  value={sortOrder[folder.id] || "date-desc"}
                                  onChange={(e) =>
                                    setSortOrder({
                                      ...sortOrder,
                                      [folder.id]: e.target.value as any,
                                    })
                                  }
                                >
                                  <option value="date-desc">
                                    Newest First
                                  </option>
                                  <option value="date-asc">Oldest First</option>
                                  <option value="alpha-asc">A → Z</option>
                                  <option value="alpha-desc">Z → A</option>
                                </select>
                              </div>
                            </div>
                          )}

                          {/* Bulk Actions Bar (appears when URLs selected) */}
                          {(selectedUrls[folder.id]?.size || 0) > 0 && (
                            <div className="bulk-actions-bar">
                              <span className="selected-count">
                                {selectedUrls[folder.id]?.size || 0} selected
                              </span>
                              <div className="bulk-actions">
                                <button
                                  className="bulk-action-btn delete"
                                  onClick={() => deleteSelectedUrls(folder.id)}
                                >
                                  🗑️ Delete ({selectedUrls[folder.id]?.size})
                                </button>
                                <button
                                  className="bulk-action-btn copy"
                                  onClick={() => copySelectedUrls(folder.id)}
                                >
                                  📋 Copy ({selectedUrls[folder.id]?.size})
                                </button>
                              </div>
                            </div>
                          )}

                          {/* URL List */}
                          <div className="folder-urls">
                            {folder.urls.length === 0 ? (
                              <p className="no-urls">
                                No URLs in this folder yet.
                              </p>
                            ) : (
                              (() => {
                                const filteredUrls = getFilteredAndSortedUrls(
                                  folder.id
                                );
                                const query = searchQuery[folder.id];

                                if (filteredUrls.length === 0 && query) {
                                  return (
                                    <p className="no-results">
                                      No URLs match "{query}"
                                    </p>
                                  );
                                }

                                return (
                                  <>
                                    {query && (
                                      <p className="search-results-count">
                                        Showing {filteredUrls.length} of{" "}
                                        {folder.urls.length} URLs
                                      </p>
                                    )}
                                    {filteredUrls.map((url, displayIndex) => {
                                      const originalIndex =
                                        folder.urls.indexOf(url);
                                      return (
                                        <div
                                          key={originalIndex}
                                          className="url-item"
                                        >
                                          {editingUrlId ===
                                          `${folder.id}-${originalIndex}` ? (
                                            <div className="url-edit">
                                              <input
                                                type="text"
                                                className="url-input"
                                                value={editingUrlValue}
                                                onChange={(e) =>
                                                  setEditingUrlValue(
                                                    e.target.value
                                                  )
                                                }
                                                onKeyDown={(e) => {
                                                  if (e.key === "Enter") {
                                                    e.preventDefault();
                                                    saveUrl(
                                                      folder.id,
                                                      originalIndex
                                                    );
                                                  } else if (
                                                    e.key === "Escape"
                                                  ) {
                                                    e.preventDefault();
                                                    cancelEditingUrl();
                                                  }
                                                }}
                                                onBlur={() =>
                                                  saveUrl(
                                                    folder.id,
                                                    originalIndex
                                                  )
                                                }
                                                autoFocus
                                              />
                                              <button
                                                className="url-save-btn"
                                                onClick={() =>
                                                  saveUrl(
                                                    folder.id,
                                                    originalIndex
                                                  )
                                                }
                                                title="Save"
                                              >
                                                ✓
                                              </button>
                                              <button
                                                className="url-cancel-btn"
                                                onClick={cancelEditingUrl}
                                                title="Cancel"
                                              >
                                                ✗
                                              </button>
                                            </div>
                                          ) : (
                                            <div className="url-display">
                                              <input
                                                type="checkbox"
                                                className="url-checkbox"
                                                checked={
                                                  selectedUrls[folder.id]?.has(
                                                    originalIndex
                                                  ) || false
                                                }
                                                onChange={() =>
                                                  toggleUrlSelection(
                                                    folder.id,
                                                    originalIndex
                                                  )
                                                }
                                              />
                                              <span className="url-number">
                                                {originalIndex + 1}.
                                              </span>
                                              <span className="url-text">
                                                {url}
                                              </span>
                                              <button
                                                className="url-edit-btn"
                                                onClick={() =>
                                                  startEditingUrl(
                                                    folder.id,
                                                    originalIndex
                                                  )
                                                }
                                                title="Edit URL"
                                              >
                                                ✏️
                                              </button>
                                              <button
                                                className="url-delete-btn"
                                                onClick={() =>
                                                  deleteUrl(
                                                    folder.id,
                                                    originalIndex
                                                  )
                                                }
                                                title="Delete URL"
                                              >
                                                🗑️
                                              </button>
                                            </div>
                                          )}
                                        </div>
                                      );
                                    })}
                                  </>
                                );
                              })()
                            )}
                          </div>

                          {/* Bulk URL textarea - always visible */}
                          <div className="bulk-url-section">
                            <textarea
                              className="bulk-url-textarea"
                              placeholder="Paste URLs here (one per line or separated by spaces/commas)&#10;&#10;Example:&#10;https://example.com/page1&#10;https://example.com/page2&#10;https://example.com/page3"
                              value={bulkUrlInput[folder.id] || ""}
                              onChange={(e) =>
                                setBulkUrlInput({
                                  ...bulkUrlInput,
                                  [folder.id]: e.target.value,
                                })
                              }
                              rows={6}
                            />
                            <button
                              className="add-bulk-urls-btn"
                              onClick={() => addBulkUrlsToFolder(folder.id)}
                              disabled={!(bulkUrlInput[folder.id] || "").trim()}
                            >
                              ✨ Add URLs to Folder
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        ) : activeTab === "cookies" ? (
          <div className="tab-content">
            <div className="auth-methods-container">
              <h2 className="auth-methods-title">🔐 Authentication Methods</h2>
              <p className="auth-methods-subtitle">
                Choose your preferred method to handle authentication for
                screenshots
              </p>

              {/* Auth Method Buttons */}
              <div className="auth-method-buttons">
                {/* Button 1: Cookie Analysis */}
                <button
                  className={`auth-method-btn ${
                    expandedAuthMethod === "analysis" ? "active" : ""
                  }`}
                  onClick={() =>
                    setExpandedAuthMethod(
                      expandedAuthMethod === "analysis" ? null : "analysis"
                    )
                  }
                >
                  <div className="btn-icon">🔍</div>
                  <div className="btn-content">
                    <div className="btn-title">Cookie Analysis & Inspector</div>
                    <div className="btn-description">
                      Analyze and inspect extracted cookies
                    </div>
                  </div>
                  <div className="btn-arrow">
                    {expandedAuthMethod === "analysis" ? "▼" : "▶"}
                  </div>
                </button>

                {expandedAuthMethod === "analysis" &&
                  cookieImportStatus.playwright?.exists && (
                    <div className="auth-method-content">
                      <div className="analysis-filters">
                        <input
                          type="text"
                          placeholder="Filter by domain (e.g., zomato, google)"
                          value={analysisDomainFilter}
                          onChange={(e) =>
                            setAnalysisDomainFilter(e.target.value)
                          }
                          className="domain-filter-input"
                        />
                        <label className="auth-only-checkbox">
                          <input
                            type="checkbox"
                            checked={showAuthCookiesOnly}
                            onChange={(e) =>
                              setShowAuthCookiesOnly(e.target.checked)
                            }
                          />
                          Show only auth cookies
                        </label>
                        <button
                          className="analyze-btn-primary"
                          onClick={analyzeCookies}
                          disabled={isAnalyzingCookies}
                        >
                          {isAnalyzingCookies
                            ? "⏳ Analyzing..."
                            : "🔍 Analyze Cookies"}
                        </button>
                      </div>

                      {showCookieAnalysis && cookieAnalysis && (
                        <div className="analysis-results">
                          <div className="analysis-stats">
                            <div className="stat-card">
                              <div className="stat-value">
                                {cookieAnalysis.total}
                              </div>
                              <div className="stat-label">Total Cookies</div>
                            </div>
                            <div className="stat-card">
                              <div className="stat-value">
                                {cookieAnalysis.unique_domains}
                              </div>
                              <div className="stat-label">Unique Domains</div>
                            </div>
                            <div className="stat-card">
                              <div className="stat-value">
                                {cookieAnalysis.auth_count}
                              </div>
                              <div className="stat-label">Auth Cookies</div>
                            </div>
                            <div className="stat-card">
                              <div className="stat-value">
                                {Math.round(
                                  (cookieAnalysis.secure_count /
                                    cookieAnalysis.total) *
                                    100
                                )}
                                %
                              </div>
                              <div className="stat-label">Secure</div>
                            </div>
                          </div>

                          {cookieAnalysis.top_domains &&
                            cookieAnalysis.top_domains.length > 0 && (
                              <div className="top-domains">
                                <h3>🌐 Top Domains</h3>
                                <div className="domain-list">
                                  {cookieAnalysis.top_domains.map(
                                    (item: any, idx: number) => (
                                      <div key={idx} className="domain-item">
                                        <span className="domain-name">
                                          {item.domain}
                                        </span>
                                        <span className="domain-count">
                                          {item.count} cookies
                                        </span>
                                      </div>
                                    )
                                  )}
                                </div>
                              </div>
                            )}

                          {cookieAnalysis.auth_cookies &&
                            cookieAnalysis.auth_cookies.length > 0 && (
                              <div className="auth-cookies-list">
                                <h3>🔑 Authentication Cookies</h3>
                                <div className="cookie-table">
                                  <table>
                                    <thead>
                                      <tr>
                                        <th>Name</th>
                                        <th>Value</th>
                                        <th>Domain</th>
                                        <th>Expires</th>
                                        <th>SameSite</th>
                                        <th>Flags</th>
                                        <th>Actions</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {cookieAnalysis.auth_cookies.map(
                                        (cookie: any, idx: number) => (
                                          <tr
                                            key={idx}
                                            className="cookie-row-clickable"
                                            onClick={() => viewCookie(cookie)}
                                          >
                                            <td className="cookie-name">
                                              {cookie.name}
                                            </td>
                                            <td className="cookie-value">
                                              {cookie.value || "(empty)"}
                                            </td>
                                            <td className="cookie-domain">
                                              {cookie.domain}
                                            </td>
                                            <td className="cookie-expires">
                                              {cookie.expires === -1 ||
                                              cookie.expires === null
                                                ? "Session"
                                                : new Date(
                                                    cookie.expires * 1000
                                                  ).toLocaleDateString()}
                                            </td>
                                            <td className="cookie-samesite">
                                              <span
                                                className={`samesite-badge samesite-${(
                                                  cookie.sameSite || "Lax"
                                                ).toLowerCase()}`}
                                              >
                                                {cookie.sameSite || "Lax"}
                                              </span>
                                            </td>
                                            <td className="cookie-flags">
                                              {cookie.secure && (
                                                <span className="flag secure">
                                                  🔒
                                                </span>
                                              )}
                                              {cookie.httpOnly && (
                                                <span className="flag httponly">
                                                  🚫
                                                </span>
                                              )}
                                            </td>
                                            <td className="cookie-actions">
                                              <button
                                                className="btn-icon-small"
                                                onClick={(e) => {
                                                  e.stopPropagation();
                                                  viewCookie(cookie);
                                                }}
                                                title="View/Edit"
                                              >
                                                ✏️
                                              </button>
                                              <button
                                                className="btn-icon-small btn-danger-small"
                                                onClick={(e) => {
                                                  e.stopPropagation();
                                                  deleteCookie(cookie);
                                                }}
                                                title="Delete"
                                              >
                                                🗑️
                                              </button>
                                            </td>
                                          </tr>
                                        )
                                      )}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            )}
                        </div>
                      )}
                    </div>
                  )}

                {/* Cookie Editor Modal */}
                {showCookieEditor && editingCookie && (
                  <div
                    className="modal-overlay"
                    onClick={() => setShowCookieEditor(false)}
                  >
                    <div
                      className="modal-content cookie-editor-modal"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="modal-header">
                        <h2>🍪 Cookie Editor</h2>
                        <button
                          className="modal-close-btn"
                          onClick={() => setShowCookieEditor(false)}
                        >
                          ✕
                        </button>
                      </div>

                      <div className="modal-body">
                        {/* Security & Type Badges */}
                        <div className="cookie-badges">
                          <span
                            className={`badge ${
                              editingCookie.secure && editingCookie.httpOnly
                                ? "badge-success"
                                : editingCookie.secure || editingCookie.httpOnly
                                ? "badge-warning"
                                : "badge-danger"
                            }`}
                          >
                            {editingCookie.secure && editingCookie.httpOnly
                              ? "🛡️ Secure"
                              : editingCookie.secure
                              ? "🔒 HTTPS Only"
                              : editingCookie.httpOnly
                              ? "🚫 No JS Access"
                              : "⚠️ Insecure"}
                          </span>

                          {/* Cookie Prefix Badge */}
                          {editingCookie.name?.startsWith("__Secure-") && (
                            <span className="badge badge-prefix-secure">
                              🔐 __Secure- Prefix
                            </span>
                          )}
                          {editingCookie.name?.startsWith("__Host-") && (
                            <span className="badge badge-prefix-host">
                              🏠 __Host- Prefix
                            </span>
                          )}

                          <span className="badge badge-info">
                            {editingCookie.domain?.startsWith(".")
                              ? "🌐 Subdomain Cookie"
                              : "📍 Exact Domain"}
                          </span>
                          {editingCookie.expires === -1 ||
                          !editingCookie.expires ? (
                            <span className="badge badge-session">
                              ⏱️ Session Cookie
                            </span>
                          ) : (
                            <span className="badge badge-persistent">
                              💾 Expires:{" "}
                              {new Date(
                                editingCookie.expires * 1000
                              ).toLocaleDateString()}
                            </span>
                          )}

                          {/* Cookie Size Warning */}
                          {(() => {
                            const cookieSize =
                              (editingCookie.name?.length || 0) +
                              (editingCookie.value?.length || 0);
                            if (cookieSize > 4096) {
                              return (
                                <span className="badge badge-danger">
                                  ⚠️ Size: {cookieSize} bytes (exceeds 4096
                                  limit!)
                                </span>
                              );
                            } else if (cookieSize > 3000) {
                              return (
                                <span className="badge badge-warning">
                                  📏 Size: {cookieSize} bytes
                                </span>
                              );
                            }
                            return null;
                          })()}

                          {/* CHIPS Badge */}
                          {editingCookie.partitioned && (
                            <span className="badge badge-chips">
                              🔒 CHIPS (Partitioned)
                            </span>
                          )}
                        </div>

                        <div className="cookie-editor-form">
                          <div className="form-group">
                            <label>
                              Name
                              <span
                                className="tooltip-icon"
                                title="Cookie identifier (case-sensitive). Use __Secure- or __Host- prefixes for enhanced security (RFC 6265bis)"
                              >
                                ℹ️
                              </span>
                            </label>
                            <input
                              type="text"
                              value={editingCookie.name}
                              onChange={(e) =>
                                setEditingCookie({
                                  ...editingCookie,
                                  name: e.target.value,
                                })
                              }
                              className="form-input"
                              placeholder="session_id or __Secure-session_id"
                            />
                            {editingCookie.name?.startsWith("__Secure-") &&
                              !editingCookie.secure && (
                                <small className="warning-text">
                                  ⚠️ __Secure- prefix requires Secure flag!
                                </small>
                              )}
                            {editingCookie.name?.startsWith("__Host-") && (
                              <>
                                {!editingCookie.secure && (
                                  <small className="warning-text">
                                    ⚠️ __Host- prefix requires Secure flag!
                                  </small>
                                )}
                                {editingCookie.path !== "/" && (
                                  <small className="warning-text">
                                    ⚠️ __Host- prefix requires Path=/!
                                  </small>
                                )}
                                {editingCookie.domain && (
                                  <small className="warning-text">
                                    ⚠️ __Host- prefix must not have Domain
                                    attribute!
                                  </small>
                                )}
                              </>
                            )}
                          </div>

                          <div className="form-group">
                            <label>
                              Value
                              <span
                                className="tooltip-icon"
                                title="Cookie data (opaque token recommended for auth)"
                              >
                                ℹ️
                              </span>
                            </label>
                            <textarea
                              value={editingCookie.value || ""}
                              onChange={(e) =>
                                setEditingCookie({
                                  ...editingCookie,
                                  value: e.target.value,
                                })
                              }
                              className="form-textarea"
                              rows={3}
                              placeholder="abc123xyz..."
                            />
                          </div>

                          <div className="form-row">
                            <div className="form-group">
                              <label>
                                Domain
                                <span
                                  className="tooltip-icon"
                                  title="Use .example.com for subdomains, example.com for exact match"
                                >
                                  ℹ️
                                </span>
                              </label>
                              <input
                                type="text"
                                value={editingCookie.domain}
                                onChange={(e) =>
                                  setEditingCookie({
                                    ...editingCookie,
                                    domain: e.target.value,
                                  })
                                }
                                className="form-input"
                                placeholder=".example.com"
                              />
                            </div>

                            <div className="form-group">
                              <label>
                                Path
                                <span
                                  className="tooltip-icon"
                                  title="URL path scope (/ for entire domain)"
                                >
                                  ℹ️
                                </span>
                              </label>
                              <input
                                type="text"
                                value={editingCookie.path || "/"}
                                onChange={(e) =>
                                  setEditingCookie({
                                    ...editingCookie,
                                    path: e.target.value,
                                  })
                                }
                                className="form-input"
                                placeholder="/"
                              />
                            </div>
                          </div>

                          <div className="form-group">
                            <label>
                              SameSite
                              <span
                                className="tooltip-icon"
                                title="Controls cross-site request behavior (RFC 6265bis)"
                              >
                                ℹ️
                              </span>
                            </label>
                            <select
                              value={editingCookie.sameSite || "Lax"}
                              onChange={(e) =>
                                setEditingCookie({
                                  ...editingCookie,
                                  sameSite: e.target.value,
                                })
                              }
                              className="form-select"
                            >
                              <option value="Strict">
                                Strict - Same-site only (most secure)
                              </option>
                              <option value="Lax">
                                Lax - Top-level navigation (default)
                              </option>
                              <option value="None">
                                None - Allow third-party (requires Secure)
                              </option>
                            </select>
                            {editingCookie.sameSite === "None" &&
                              !editingCookie.secure && (
                                <small className="warning-text">
                                  ⚠️ SameSite=None requires Secure flag!
                                </small>
                              )}
                          </div>

                          <div className="form-row-checkboxes">
                            <div className="form-group-checkbox">
                              <label>
                                <input
                                  type="checkbox"
                                  checked={editingCookie.secure || false}
                                  onChange={(e) =>
                                    setEditingCookie({
                                      ...editingCookie,
                                      secure: e.target.checked,
                                    })
                                  }
                                />
                                <span className="checkbox-label">
                                  🔒 Secure
                                  <span
                                    className="tooltip-icon"
                                    title="Only sent over HTTPS connections"
                                  >
                                    ℹ️
                                  </span>
                                </span>
                              </label>
                            </div>

                            <div className="form-group-checkbox">
                              <label>
                                <input
                                  type="checkbox"
                                  checked={editingCookie.httpOnly || false}
                                  onChange={(e) =>
                                    setEditingCookie({
                                      ...editingCookie,
                                      httpOnly: e.target.checked,
                                    })
                                  }
                                />
                                <span className="checkbox-label">
                                  🚫 HttpOnly
                                  <span
                                    className="tooltip-icon"
                                    title="Prevents JavaScript access (XSS protection)"
                                  >
                                    ℹ️
                                  </span>
                                </span>
                              </label>
                            </div>

                            <div className="form-group-checkbox">
                              <label>
                                <input
                                  type="checkbox"
                                  checked={editingCookie.partitioned || false}
                                  onChange={(e) =>
                                    setEditingCookie({
                                      ...editingCookie,
                                      partitioned: e.target.checked,
                                    })
                                  }
                                />
                                <span className="checkbox-label">
                                  🔐 Partitioned (CHIPS)
                                  <span
                                    className="tooltip-icon"
                                    title="Cookies Having Independent Partitioned State - separate cookie jar per top-level site (Chrome 114+)"
                                  >
                                    ℹ️
                                  </span>
                                </span>
                              </label>
                            </div>
                          </div>
                          {editingCookie.partitioned &&
                            !editingCookie.secure && (
                              <small className="warning-text">
                                ⚠️ Partitioned cookies must have Secure flag!
                              </small>
                            )}
                          {editingCookie.partitioned &&
                            !editingCookie.name?.startsWith("__Host-") && (
                              <small className="info-text">
                                💡 Recommended: Use __Host- prefix with
                                Partitioned cookies for enhanced security
                              </small>
                            )}

                          <div className="form-group">
                            <label>
                              Expires
                              <span
                                className="tooltip-icon"
                                title="Persistent cookie expiration (leave empty for session cookie)"
                              >
                                ℹ️
                              </span>
                            </label>
                            <input
                              type="datetime-local"
                              value={
                                editingCookie.expires &&
                                editingCookie.expires !== -1
                                  ? new Date(editingCookie.expires * 1000)
                                      .toISOString()
                                      .slice(0, 16)
                                  : ""
                              }
                              onChange={(e) => {
                                const timestamp = e.target.value
                                  ? Math.floor(
                                      new Date(e.target.value).getTime() / 1000
                                    )
                                  : -1;
                                setEditingCookie({
                                  ...editingCookie,
                                  expires: timestamp,
                                });
                              }}
                              className="form-input"
                            />
                            <small>
                              Leave empty for session cookie (cleared when
                              browser closes)
                            </small>
                          </div>
                        </div>
                      </div>

                      <div className="modal-footer">
                        <div className="modal-footer-left">
                          <button
                            className="btn-danger"
                            onClick={() => {
                              deleteCookie(editingCookie);
                            }}
                          >
                            🗑️ Delete
                          </button>
                          <button
                            className="btn-secondary"
                            onClick={() => openExportModal("curl")}
                            title="Export as cURL command with options"
                          >
                            📋 cURL
                          </button>
                          <button
                            className="btn-secondary"
                            onClick={() => openExportModal("playwright")}
                            title="Export as Playwright code with options"
                          >
                            🎭 Playwright
                          </button>
                          <button
                            className="btn-security"
                            onClick={runSecurityAudit}
                            title="Run OWASP-compliant security audit"
                          >
                            🔒 Security Audit
                          </button>
                        </div>
                        <div className="modal-footer-right">
                          <button
                            className="btn-secondary"
                            onClick={() => setShowCookieEditor(false)}
                          >
                            Cancel
                          </button>
                          <button
                            className="btn-primary"
                            onClick={updateCookie}
                          >
                            💾 Save Changes
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 📤 Export Modal */}
                {showExportModal && (
                  <div
                    className="modal-overlay"
                    onClick={() => setShowExportModal(false)}
                  >
                    <div
                      className="modal-content export-modal"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="modal-header">
                        <h3>
                          {exportType === "curl"
                            ? "📋 Export as cURL"
                            : "🎭 Export as Playwright"}
                        </h3>
                        <button
                          className="modal-close"
                          onClick={() => setShowExportModal(false)}
                        >
                          ✕
                        </button>
                      </div>

                      <div className="modal-body">
                        {/* Export Options */}
                        <div className="export-options">
                          <h4>Export Options</h4>

                          {exportType === "curl" && (
                            <>
                              <label className="checkbox-label">
                                <input
                                  type="checkbox"
                                  checked={exportOptions.includeMethod}
                                  onChange={(e) =>
                                    setExportOptions({
                                      ...exportOptions,
                                      includeMethod: e.target.checked,
                                    })
                                  }
                                />
                                <span>Include HTTP Method</span>
                              </label>

                              {exportOptions.includeMethod && (
                                <div className="form-group">
                                  <label>HTTP Method</label>
                                  <select
                                    value={exportOptions.method}
                                    onChange={(e) =>
                                      setExportOptions({
                                        ...exportOptions,
                                        method: e.target.value,
                                      })
                                    }
                                    className="form-select"
                                  >
                                    <option value="GET">GET</option>
                                    <option value="POST">POST</option>
                                    <option value="PUT">PUT</option>
                                    <option value="DELETE">DELETE</option>
                                    <option value="PATCH">PATCH</option>
                                  </select>
                                </div>
                              )}

                              <label className="checkbox-label">
                                <input
                                  type="checkbox"
                                  checked={exportOptions.includeUrl}
                                  onChange={(e) =>
                                    setExportOptions({
                                      ...exportOptions,
                                      includeUrl: e.target.checked,
                                    })
                                  }
                                />
                                <span>Include URL</span>
                              </label>

                              {exportOptions.includeUrl && (
                                <div className="form-group">
                                  <label>Target URL</label>
                                  <input
                                    type="text"
                                    value={exportOptions.url}
                                    onChange={(e) =>
                                      setExportOptions({
                                        ...exportOptions,
                                        url: e.target.value,
                                      })
                                    }
                                    className="form-input"
                                    placeholder="https://example.com/api"
                                  />
                                </div>
                              )}
                            </>
                          )}

                          {exportType === "playwright" && (
                            <>
                              <label className="checkbox-label">
                                <input
                                  type="checkbox"
                                  checked={exportOptions.prettyPrint}
                                  onChange={(e) =>
                                    setExportOptions({
                                      ...exportOptions,
                                      prettyPrint: e.target.checked,
                                    })
                                  }
                                />
                                <span>Pretty Print (Multi-line)</span>
                              </label>
                            </>
                          )}

                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={exportOptions.includeComments}
                              onChange={(e) =>
                                setExportOptions({
                                  ...exportOptions,
                                  includeComments: e.target.checked,
                                })
                              }
                            />
                            <span>Include Comments</span>
                          </label>

                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={exportOptions.explainEverything}
                              onChange={(e) =>
                                setExportOptions({
                                  ...exportOptions,
                                  explainEverything: e.target.checked,
                                })
                              }
                            />
                            <span>
                              📚 Explain Everything (Educational Mode)
                            </span>
                          </label>
                        </div>

                        {/* Editable Code Preview */}
                        <div className="export-preview">
                          <h4>
                            Code Preview (Editable)
                            <span className="preview-hint">
                              ✏️ Edit before copying
                            </span>
                          </h4>
                          <textarea
                            className="code-editor"
                            value={exportCode}
                            onChange={(e) => setExportCode(e.target.value)}
                            spellCheck={false}
                            rows={20}
                          />
                        </div>
                      </div>

                      <div className="modal-footer">
                        <button
                          className="btn-secondary"
                          onClick={() => setShowExportModal(false)}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn-primary"
                          onClick={copyExportCode}
                        >
                          📋 Copy to Clipboard
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* 🔒 Security Audit Modal */}
                {showSecurityAudit && securityReport && (
                  <div
                    className="modal-overlay"
                    onClick={() => setShowSecurityAudit(false)}
                  >
                    <div
                      className="modal-content security-audit-modal"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="modal-header">
                        <h3>🔒 Cookie Security Audit</h3>
                        <button
                          className="modal-close"
                          onClick={() => setShowSecurityAudit(false)}
                        >
                          ✕
                        </button>
                      </div>

                      <div className="modal-body">
                        {/* Security Score */}
                        <div className="security-score-card">
                          <div
                            className="score-circle"
                            style={{ borderColor: securityReport.ratingColor }}
                          >
                            <div
                              className="score-value"
                              style={{ color: securityReport.ratingColor }}
                            >
                              {securityReport.score}
                            </div>
                            <div className="score-label">/ 100</div>
                          </div>
                          <div className="score-details">
                            <h2 style={{ color: securityReport.ratingColor }}>
                              {securityReport.rating}
                            </h2>
                            <p className="cookie-name">
                              Cookie: {securityReport.cookieName}
                            </p>
                            <p className="audit-timestamp">
                              Audited: {securityReport.timestamp}
                            </p>
                          </div>
                        </div>

                        {/* Critical Issues */}
                        {securityReport.issues.length > 0 && (
                          <div className="audit-section">
                            <h4 className="section-title critical">
                              🚨 Critical Issues ({securityReport.issues.length}
                              )
                            </h4>
                            {securityReport.issues.map(
                              (issue: any, idx: number) => (
                                <div
                                  key={idx}
                                  className={`audit-item severity-${issue.severity.toLowerCase()}`}
                                >
                                  <div className="audit-header">
                                    <span
                                      className={`severity-badge ${issue.severity.toLowerCase()}`}
                                    >
                                      {issue.severity}
                                    </span>
                                    <strong>{issue.title}</strong>
                                  </div>
                                  <p className="audit-description">
                                    {issue.description}
                                  </p>
                                  <p className="audit-impact">
                                    <strong>Impact:</strong> {issue.impact}
                                  </p>
                                  <p className="audit-fix">
                                    <strong>Fix:</strong> {issue.fix}
                                  </p>
                                  <p className="audit-owasp">
                                    <strong>Reference:</strong> {issue.owasp}
                                  </p>
                                </div>
                              )
                            )}
                          </div>
                        )}

                        {/* Warnings */}
                        {securityReport.warnings.length > 0 && (
                          <div className="audit-section">
                            <h4 className="section-title warning">
                              ⚠️ Warnings ({securityReport.warnings.length})
                            </h4>
                            {securityReport.warnings.map(
                              (warning: any, idx: number) => (
                                <div
                                  key={idx}
                                  className={`audit-item severity-${warning.severity.toLowerCase()}`}
                                >
                                  <div className="audit-header">
                                    <span
                                      className={`severity-badge ${warning.severity.toLowerCase()}`}
                                    >
                                      {warning.severity}
                                    </span>
                                    <strong>{warning.title}</strong>
                                  </div>
                                  <p className="audit-description">
                                    {warning.description}
                                  </p>
                                  <p className="audit-impact">
                                    <strong>Impact:</strong> {warning.impact}
                                  </p>
                                  <p className="audit-fix">
                                    <strong>Recommendation:</strong>{" "}
                                    {warning.fix}
                                  </p>
                                  <p className="audit-owasp">
                                    <strong>Reference:</strong> {warning.owasp}
                                  </p>
                                </div>
                              )
                            )}
                          </div>
                        )}

                        {/* Recommendations */}
                        {securityReport.recommendations.length > 0 && (
                          <div className="audit-section">
                            <h4 className="section-title info">
                              💡 Recommendations (
                              {securityReport.recommendations.length})
                            </h4>
                            {securityReport.recommendations.map(
                              (rec: any, idx: number) => (
                                <div
                                  key={idx}
                                  className={`audit-item severity-${rec.severity.toLowerCase()}`}
                                >
                                  <div className="audit-header">
                                    <span
                                      className={`severity-badge ${rec.severity.toLowerCase()}`}
                                    >
                                      {rec.severity}
                                    </span>
                                    <strong>{rec.title}</strong>
                                  </div>
                                  <p className="audit-description">
                                    {rec.description}
                                  </p>
                                  <p className="audit-impact">
                                    <strong>Benefit:</strong> {rec.impact}
                                  </p>
                                  <p className="audit-fix">
                                    <strong>Suggestion:</strong> {rec.fix}
                                  </p>
                                  <p className="audit-owasp">
                                    <strong>Reference:</strong> {rec.owasp}
                                  </p>
                                </div>
                              )
                            )}
                          </div>
                        )}

                        {/* All Clear */}
                        {securityReport.issues.length === 0 &&
                          securityReport.warnings.length === 0 &&
                          securityReport.recommendations.length === 0 && (
                            <div className="audit-all-clear">
                              <div className="all-clear-icon">✅</div>
                              <h3>Perfect Security Configuration!</h3>
                              <p>
                                This cookie follows all OWASP best practices and
                                RFC 6265bis standards.
                              </p>
                            </div>
                          )}
                      </div>

                      <div className="modal-footer">
                        <button
                          className="btn-secondary"
                          onClick={() => setShowSecurityAudit(false)}
                        >
                          Close
                        </button>
                        <button
                          className="btn-primary"
                          onClick={() => {
                            const report = JSON.stringify(
                              securityReport,
                              null,
                              2
                            );
                            navigator.clipboard.writeText(report);
                            alert("✅ Security report copied to clipboard!");
                          }}
                        >
                          📋 Copy Report
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* 📤 Multi-Format Export Modal */}
                {showFormatExport && (
                  <div
                    className="modal-overlay"
                    onClick={() => setShowFormatExport(false)}
                  >
                    <div
                      className="modal-content format-export-modal"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="modal-header">
                        <h3>📤 Export Cookies - Multiple Formats</h3>
                        <button
                          className="modal-close"
                          onClick={() => setShowFormatExport(false)}
                        >
                          ✕
                        </button>
                      </div>

                      <div className="modal-body">
                        <div className="format-selection">
                          <h4>Select Export Format</h4>

                          <div className="format-options">
                            <label
                              className={`format-option ${
                                exportFormat === "json" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="exportFormat"
                                value="json"
                                checked={exportFormat === "json"}
                                onChange={(e) =>
                                  setExportFormat(e.target.value)
                                }
                              />
                              <div className="format-details">
                                <div className="format-title">📄 JSON</div>
                                <div className="format-description">
                                  Standard JSON format (current format)
                                </div>
                                <div className="format-extension">.json</div>
                              </div>
                            </label>

                            <label
                              className={`format-option ${
                                exportFormat === "netscape" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="exportFormat"
                                value="netscape"
                                checked={exportFormat === "netscape"}
                                onChange={(e) =>
                                  setExportFormat(e.target.value)
                                }
                              />
                              <div className="format-details">
                                <div className="format-title">🍪 Netscape</div>
                                <div className="format-description">
                                  cookies.txt format (compatible with curl,
                                  wget)
                                </div>
                                <div className="format-extension">.txt</div>
                              </div>
                            </label>

                            <label
                              className={`format-option ${
                                exportFormat === "har" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="exportFormat"
                                value="har"
                                checked={exportFormat === "har"}
                                onChange={(e) =>
                                  setExportFormat(e.target.value)
                                }
                              />
                              <div className="format-details">
                                <div className="format-title">📦 HAR</div>
                                <div className="format-description">
                                  HTTP Archive format (browser DevTools
                                  compatible)
                                </div>
                                <div className="format-extension">.har</div>
                              </div>
                            </label>

                            <label
                              className={`format-option ${
                                exportFormat === "csv" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="exportFormat"
                                value="csv"
                                checked={exportFormat === "csv"}
                                onChange={(e) =>
                                  setExportFormat(e.target.value)
                                }
                              />
                              <div className="format-details">
                                <div className="format-title">📊 CSV</div>
                                <div className="format-description">
                                  Comma-separated values (Excel, Google Sheets)
                                </div>
                                <div className="format-extension">.csv</div>
                              </div>
                            </label>

                            <label
                              className={`format-option ${
                                exportFormat === "headers" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="exportFormat"
                                value="headers"
                                checked={exportFormat === "headers"}
                                onChange={(e) =>
                                  setExportFormat(e.target.value)
                                }
                              />
                              <div className="format-details">
                                <div className="format-title">
                                  📋 Set-Cookie Headers
                                </div>
                                <div className="format-description">
                                  HTTP Set-Cookie header format (server-side)
                                </div>
                                <div className="format-extension">.txt</div>
                              </div>
                            </label>

                            <label
                              className={`format-option ${
                                exportFormat === "curl-headers"
                                  ? "selected"
                                  : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="exportFormat"
                                value="curl-headers"
                                checked={exportFormat === "curl-headers"}
                                onChange={(e) =>
                                  setExportFormat(e.target.value)
                                }
                              />
                              <div className="format-details">
                                <div className="format-title">
                                  🔧 cURL Command
                                </div>
                                <div className="format-description">
                                  Ready-to-use cURL command with all cookies
                                </div>
                                <div className="format-extension">.sh</div>
                              </div>
                            </label>
                          </div>
                        </div>

                        <div className="format-preview">
                          <h4>Preview</h4>
                          <pre className="format-preview-code">
                            {exportAllCookiesInFormat(exportFormat)}
                          </pre>
                        </div>
                      </div>

                      <div className="modal-footer">
                        <button
                          className="btn-secondary"
                          onClick={() => setShowFormatExport(false)}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn-secondary"
                          onClick={copyFormattedCookies}
                        >
                          📋 Copy to Clipboard
                        </button>
                        <button
                          className="btn-primary"
                          onClick={downloadCookiesInFormat}
                        >
                          💾 Download File
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* 📥 Multi-Format Import Modal */}
                {showFormatImport && (
                  <div
                    className="modal-overlay"
                    onClick={() => setShowFormatImport(false)}
                  >
                    <div
                      className="modal-content format-import-modal"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="modal-header">
                        <h3>📥 Import Cookies - Multiple Formats</h3>
                        <button
                          className="modal-close"
                          onClick={() => setShowFormatImport(false)}
                        >
                          ✕
                        </button>
                      </div>

                      <div className="modal-body">
                        <div className="import-instructions">
                          <p>
                            <strong>📋 Supported Formats:</strong>
                          </p>
                          <ul>
                            <li>
                              <strong>JSON</strong> - Standard JSON array format
                            </li>
                            <li>
                              <strong>Netscape</strong> - cookies.txt format
                              (curl, wget compatible)
                            </li>
                            <li>
                              <strong>HAR</strong> - HTTP Archive format
                              (browser DevTools export)
                            </li>
                            <li>
                              <strong>CSV</strong> - Comma-separated values
                              (Excel, Google Sheets)
                            </li>
                          </ul>
                        </div>

                        <div className="format-selection">
                          <h4>Select Import Format</h4>

                          <div className="format-options-compact">
                            <label
                              className={`format-option-compact ${
                                importFormat === "json" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="importFormat"
                                value="json"
                                checked={importFormat === "json"}
                                onChange={(e) =>
                                  setImportFormat(e.target.value)
                                }
                              />
                              <span>📄 JSON</span>
                            </label>

                            <label
                              className={`format-option-compact ${
                                importFormat === "netscape" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="importFormat"
                                value="netscape"
                                checked={importFormat === "netscape"}
                                onChange={(e) =>
                                  setImportFormat(e.target.value)
                                }
                              />
                              <span>🍪 Netscape</span>
                            </label>

                            <label
                              className={`format-option-compact ${
                                importFormat === "har" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="importFormat"
                                value="har"
                                checked={importFormat === "har"}
                                onChange={(e) =>
                                  setImportFormat(e.target.value)
                                }
                              />
                              <span>📦 HAR</span>
                            </label>

                            <label
                              className={`format-option-compact ${
                                importFormat === "csv" ? "selected" : ""
                              }`}
                            >
                              <input
                                type="radio"
                                name="importFormat"
                                value="csv"
                                checked={importFormat === "csv"}
                                onChange={(e) =>
                                  setImportFormat(e.target.value)
                                }
                              />
                              <span>📊 CSV</span>
                            </label>
                          </div>
                        </div>

                        <div className="file-upload-section">
                          <label className="file-upload-label">
                            <input
                              type="file"
                              accept=".json,.txt,.har,.csv"
                              onChange={handleImportFile}
                              style={{ display: "none" }}
                            />
                            <div className="file-upload-button">
                              📁 Choose File to Import
                            </div>
                          </label>
                          <p className="file-upload-hint">
                            Select a file in {importFormat.toUpperCase()} format
                          </p>
                        </div>
                      </div>

                      <div className="modal-footer">
                        <button
                          className="btn-secondary"
                          onClick={() => setShowFormatImport(false)}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Button 2: Automated Auth State */}
                <button
                  className={`auth-method-btn ${
                    expandedAuthMethod === "automated" ? "active" : ""
                  }`}
                  onClick={() =>
                    setExpandedAuthMethod(
                      expandedAuthMethod === "automated" ? null : "automated"
                    )
                  }
                >
                  <div className="btn-icon">🔐</div>
                  <div className="btn-content">
                    <div className="btn-title">Automated Auth State</div>
                    <div className="btn-description">
                      One-click login with browser automation (Recommended)
                    </div>
                    {authStateStatus.exists && (
                      <div className="btn-badge">✅ Active</div>
                    )}
                  </div>
                  <div className="btn-arrow">
                    {expandedAuthMethod === "automated" ? "▼" : "▶"}
                  </div>
                </button>

                {expandedAuthMethod === "automated" && (
                  <div className="auth-method-content">
                    {authStateStatus.exists ? (
                      <div className="auth-state-saved">
                        <div className="auth-state-info">
                          <span className="status-indicator active">●</span>
                          <div className="auth-state-details">
                            <strong>✅ Auth State Saved!</strong>
                            <p>
                              Cookies: {authStateStatus.cookie_count || 0} |
                              localStorage:{" "}
                              {authStateStatus.localStorage_count || 0} items
                            </p>
                          </div>
                        </div>
                        <div className="auth-state-actions">
                          <button
                            className="btn-secondary"
                            onClick={openLoginBrowser}
                          >
                            🔄 Update Auth State
                          </button>
                          <button
                            className="btn-danger"
                            onClick={clearAuthState}
                          >
                            🗑️ Clear
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="auth-state-empty">
                        <p>No auth state saved yet.</p>
                        <button
                          className="btn-primary"
                          onClick={openLoginBrowser}
                          disabled={isLoginInProgress}
                        >
                          {isLoginInProgress
                            ? "⏳ Opening browser..."
                            : "🚀 Open Login Browser"}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Button 3: Browser Cookie Import */}
                <button
                  className={`auth-method-btn ${
                    expandedAuthMethod === "import" ? "active" : ""
                  }`}
                  onClick={() =>
                    setExpandedAuthMethod(
                      expandedAuthMethod === "import" ? null : "import"
                    )
                  }
                >
                  <div className="btn-icon">🍪</div>
                  <div className="btn-content">
                    <div className="btn-title">Import Browser Cookies</div>
                    <div className="btn-description">
                      Extract cookies from your installed browsers
                    </div>
                    {cookieImportStatus.playwright?.exists && (
                      <div className="btn-badge">
                        ✅ {cookieImportStatus.playwright.cookie_count} cookies
                      </div>
                    )}
                  </div>
                  <div className="btn-arrow">
                    {expandedAuthMethod === "import" ? "▼" : "▶"}
                  </div>
                </button>

                {expandedAuthMethod === "import" && (
                  <div className="auth-method-content">
                    <div className="cookie-import-controls">
                      <select
                        value={selectedBrowser}
                        onChange={(e) => setSelectedBrowser(e.target.value)}
                        className="browser-select"
                      >
                        <option value="auto">Auto-detect</option>
                        <option value="chrome">Chrome</option>
                        <option value="firefox">Firefox</option>
                        <option value="edge">Edge</option>
                        <option value="safari">Safari</option>
                        <option value="brave">Brave</option>
                        <option value="opera">Opera</option>
                      </select>

                      <input
                        type="text"
                        placeholder="Domains (optional, comma-separated)"
                        value={cookieDomains}
                        onChange={(e) => setCookieDomains(e.target.value)}
                        className="domain-input"
                      />

                      <button
                        className="btn-primary"
                        onClick={extractCookies}
                        disabled={isExtractingCookies}
                      >
                        {isExtractingCookies
                          ? "⏳ Extracting..."
                          : "🍪 Extract Cookies"}
                      </button>
                    </div>

                    {cookieImportStatus.playwright?.exists && (
                      <div className="cookie-status">
                        <p>
                          ✅ {cookieImportStatus.playwright.cookie_count}{" "}
                          cookies extracted
                          {cookieImportStatus.playwright.extracted_at && (
                            <span>
                              {" "}
                              •{" "}
                              {new Date(
                                cookieImportStatus.playwright.extracted_at
                              ).toLocaleString()}
                            </span>
                          )}
                        </p>
                        <button
                          className="btn-secondary"
                          onClick={clearCookies}
                        >
                          🗑️ Clear Cookies
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Button 4: Manual Cookie/LocalStorage */}
                <button
                  className={`auth-method-btn ${
                    expandedAuthMethod === "manual" ? "active" : ""
                  }`}
                  onClick={() =>
                    setExpandedAuthMethod(
                      expandedAuthMethod === "manual" ? null : "manual"
                    )
                  }
                >
                  <div className="btn-icon">✍️</div>
                  <div className="btn-content">
                    <div className="btn-title">
                      Manual Cookie & LocalStorage
                    </div>
                    <div className="btn-description">
                      Paste cookies and localStorage manually
                    </div>
                  </div>
                  <div className="btn-arrow">
                    {expandedAuthMethod === "manual" ? "▼" : "▶"}
                  </div>
                </button>

                {expandedAuthMethod === "manual" && (
                  <div className="auth-method-content">
                    <div className="manual-input-section">
                      <label>
                        <strong>🍪 Cookies (JSON format)</strong>
                        <textarea
                          value={cookies}
                          onChange={(e) => setCookies(e.target.value)}
                          placeholder='[{"name": "session", "value": "abc123", "domain": ".example.com"}]'
                          rows={6}
                          className="manual-textarea"
                        />
                      </label>

                      <label>
                        <strong>💾 LocalStorage (JSON format)</strong>
                        <textarea
                          value={localStorageData}
                          onChange={(e) => setLocalStorageData(e.target.value)}
                          placeholder='{"key": "value", "token": "xyz789"}'
                          rows={6}
                          className="manual-textarea"
                        />
                      </label>

                      <button
                        className="btn-secondary"
                        onClick={beautifyCookies}
                      >
                        ✨ Format JSON
                      </button>

                      <button
                        className="btn-primary"
                        onClick={() => setShowFormatImport(true)}
                      >
                        📥 Import Cookies
                      </button>

                      <button
                        className="btn-primary"
                        onClick={() => setShowFormatExport(true)}
                        disabled={!cookies.trim()}
                      >
                        📤 Export Cookies
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : activeTab === "settings" ? (
          <div className="tab-content">
            <div className="settings-content">
              {/* Keyword Config Button */}
              <div className="settings-section">
                <button
                  onClick={openKeywordConfigTab}
                  className="keyword-config-btn"
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#2196F3",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "14px",
                    fontWeight: "500",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    marginBottom: "0",
                  }}
                >
                  🔤 Keyword Config
                </button>
              </div>

              {/* Capture Mode Selection */}
              <div className="settings-section">
                <h3>📸 Capture Mode</h3>

                <label className="radio-label">
                  <input
                    type="radio"
                    name="captureMode"
                    value="viewport"
                    checked={captureMode === "viewport"}
                    onChange={(e) => setCaptureMode(e.target.value)}
                    disabled={loading}
                  />
                  <span className="radio-text">🖼️ Viewport only</span>
                </label>
                <p className="option-hint">
                  Single screenshot of visible area (1366x768)
                </p>

                <label className="radio-label">
                  <input
                    type="radio"
                    name="captureMode"
                    value="fullpage"
                    checked={captureMode === "fullpage"}
                    onChange={(e) => setCaptureMode(e.target.value)}
                    disabled={loading}
                  />
                  <span className="radio-text">📄 Full page</span>
                </label>
                <p className="option-hint">
                  Single tall screenshot of entire page (may be very long)
                </p>

                <label className="radio-label">
                  <input
                    type="radio"
                    name="captureMode"
                    value="segmented"
                    checked={captureMode === "segmented"}
                    onChange={(e) => setCaptureMode(e.target.value)}
                    disabled={loading}
                  />
                  <span className="radio-text">📚 Segmented</span>
                </label>
                <p className="option-hint">
                  Multiple viewport screenshots (scroll-by-scroll capture)
                </p>

                {/* Advanced Settings for Segmented Mode */}
                {captureMode === "segmented" && (
                  <div className="advanced-settings">
                    <button
                      type="button"
                      onClick={() => setShowAdvanced(!showAdvanced)}
                      className="advanced-toggle"
                      disabled={loading}
                    >
                      ⚙️ Advanced Settings {showAdvanced ? "▼" : "▶"}
                    </button>

                    {showAdvanced && (
                      <div className="advanced-panel">
                        <div className="advanced-row">
                          <label>Overlap: {segmentOverlap}%</label>
                          <input
                            type="range"
                            min="0"
                            max="50"
                            value={segmentOverlap}
                            onChange={(e) =>
                              setSegmentOverlap(parseInt(e.target.value))
                            }
                            disabled={loading}
                          />
                          <span className="hint-text">
                            Prevents gaps between segments
                          </span>
                        </div>

                        <div className="advanced-row">
                          <label>Scroll delay: {segmentScrollDelay}ms</label>
                          <input
                            type="number"
                            min="100"
                            max="5000"
                            step="100"
                            value={segmentScrollDelay}
                            onChange={(e) =>
                              setSegmentScrollDelay(parseInt(e.target.value))
                            }
                            disabled={loading}
                          />
                          <span className="hint-text">
                            Wait time for lazy-loaded content
                          </span>
                        </div>

                        <div className="advanced-row">
                          <label>Max segments: {segmentMaxSegments}</label>
                          <input
                            type="number"
                            min="1"
                            max="200"
                            value={segmentMaxSegments}
                            onChange={(e) =>
                              setSegmentMaxSegments(parseInt(e.target.value))
                            }
                            disabled={loading}
                          />
                          <span className="hint-text">
                            Prevents infinite scrolling sites
                          </span>
                        </div>

                        <div className="advanced-row">
                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={segmentSkipDuplicates}
                              onChange={(e) =>
                                setSegmentSkipDuplicates(e.target.checked)
                              }
                              disabled={loading}
                            />
                            <span>Skip duplicate segments</span>
                          </label>
                        </div>

                        <div className="advanced-row">
                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={segmentSmartLazyLoad}
                              onChange={(e) =>
                                setSegmentSmartLazyLoad(e.target.checked)
                              }
                              disabled={loading}
                            />
                            <span>Smart lazy-load detection</span>
                          </label>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Browser Engine Selection */}
              <div className="settings-section">
                <h3>🦊 Browser Engine</h3>

                <label className="radio-label">
                  <input
                    type="radio"
                    name="browserEngine"
                    value="playwright"
                    checked={browserEngine === "playwright"}
                    onChange={(e) => setBrowserEngine(e.target.value)}
                    disabled={loading}
                  />
                  <span className="radio-text">🎭 Playwright (Standard)</span>
                </label>
                <p className="option-hint">
                  Standard Chromium with Patchright patches (40-60% success on
                  protected sites)
                </p>

                <label className="radio-label">
                  <input
                    type="radio"
                    name="browserEngine"
                    value="camoufox"
                    checked={browserEngine === "camoufox"}
                    onChange={(e) => setBrowserEngine(e.target.value)}
                    disabled={loading}
                  />
                  <span className="radio-text">🦊 Camoufox (Advanced)</span>
                </label>
                <p className="option-hint">
                  Custom Firefox with TLS fingerprint patches (90-95% success on
                  protected sites like Zomato)
                </p>

                {browserEngine === "camoufox" && (
                  <div
                    style={{
                      background: "#e3f2fd",
                      border: "2px solid #2196f3",
                      padding: "12px",
                      borderRadius: "8px",
                      marginTop: "10px",
                    }}
                  >
                    <p
                      style={{ margin: 0, fontSize: "14px", color: "#1565c0" }}
                    >
                      ℹ️ <strong>Camoufox Info:</strong> Custom Firefox build
                      that bypasses TLS/HTTP2 fingerprinting. Requires:{" "}
                      <code>pip install camoufox</code>
                    </p>
                  </div>
                )}
              </div>

              {/* Stealth Mode */}
              <div className="settings-section">
                <h3>🥷 Stealth Mode</h3>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={useStealth}
                    onChange={(e) => setUseStealth(e.target.checked)}
                    disabled={loading}
                  />
                  <span className="checkbox-text">
                    Use stealth mode (bypass bot detection)
                  </span>
                </label>
                <p className="option-hint">
                  {useStealth
                    ? "✅ Enabled: Hides automation, adds realistic headers (JavaScript-level bypass)"
                    : "⚠️ Disabled: Some sites may block automated browsers"}
                </p>
              </div>

              {/* Real Browser Mode */}
              <div className="settings-section">
                <h3>🌐 Real Browser Mode</h3>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={useRealBrowser}
                    onChange={(e) => setUseRealBrowser(e.target.checked)}
                    disabled={loading}
                  />
                  <span className="checkbox-text">
                    Use real browser (slower, visible window)
                  </span>
                </label>
                <p className="option-hint">
                  {useRealBrowser
                    ? "✅ Enabled: Opens visible Chrome window (95-99% success, slower)"
                    : "⚠️ Disabled: Runs headless (invisible, faster)"}
                </p>
              </div>

              {/* Parallel Text Box Processing */}
              <div className="settings-section">
                <h3>⚡ Parallel Text Box Processing</h3>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={enableParallelTextBoxes}
                    onChange={(e) =>
                      setEnableParallelTextBoxes(e.target.checked)
                    }
                    disabled={loading}
                  />
                  <span className="checkbox-text">
                    Process all text boxes in parallel
                  </span>
                </label>
                <p className="option-hint">
                  {enableParallelTextBoxes
                    ? "✅ Enabled: All text boxes are processed simultaneously (maximum speed)"
                    : "⚠️ Disabled: Text boxes are processed one by one (sequential)"}
                </p>
              </div>

              {/* Network Event Tracking */}
              <div className="settings-section">
                <h3>📡 Network Event Tracking</h3>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={trackNetwork}
                    onChange={(e) => setTrackNetwork(e.target.checked)}
                    disabled={loading}
                  />
                  <span className="checkbox-text">
                    Track network events during capture
                  </span>
                </label>
                <p className="option-hint">
                  {trackNetwork
                    ? "✅ Enabled: Captures HTTP requests and responses (useful for debugging)"
                    : "⚠️ Disabled: Network events not tracked (faster capture)"}
                </p>
              </div>

              {/* Backend Management */}
              <div className="settings-section">
                <h3>🔧 Backend Management</h3>
                <p className="section-description">
                  Restart the backend server to apply code changes or fix
                  issues.
                </p>
                <button
                  onClick={restartBackend}
                  disabled={isRestartingBackend || loading}
                  className="restart-backend-btn"
                >
                  {isRestartingBackend
                    ? "🔄 Restarting..."
                    : "🔄 Restart Backend"}
                </button>
                {restartMessage && (
                  <p
                    className={`restart-message ${
                      restartMessage.includes("❌") ? "error" : "success"
                    }`}
                  >
                    {restartMessage}
                  </p>
                )}
                <p className="option-hint">
                  💡 Use this after updating code (e.g., applying Zomato fix).
                  The backend will restart automatically.
                </p>
              </div>
            </div>
          </div>
        ) : activeTab === "main" ? (
          /* Main View */
          <div className="tab-content">
            <div className="input-section">
              {/* ✅ NEW FEATURE: Multiple text boxes checkbox */}
              <div className="multiple-textboxes-section">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={enableMultipleTextBoxes}
                    onChange={(e) =>
                      setEnableMultipleTextBoxes(e.target.checked)
                    }
                    disabled={loading}
                  />
                  <span className="checkbox-text">
                    Open multiple text boxes (batch processing)
                  </span>
                </label>
                <p className="option-hint">
                  {enableMultipleTextBoxes
                    ? "Enabled✅: Create separate sessions and Word docs for each text box"
                    : "Disabled⚠️: Single text box mode (classic behavior)"}
                </p>
              </div>

              {enableMultipleTextBoxes ? (
                /* ✅ NEW: Multiple text boxes mode */
                <>
                  {/* ✅ NEW: Folder Name Input + Beautify Button (Horizontal Layout) */}
                  <div className="folder-and-beautify-row">
                    {/* Left: Folder Name Input */}
                    <div className="word-doc-folder-section">
                      <label>
                        <strong>📁 Folder Name (for Word docs):</strong>
                      </label>
                      <input
                        type="text"
                        className="word-doc-folder-input"
                        placeholder="e.g., November 2025, Q4 Reports (leave empty for no folder)"
                        value={wordDocFolderName}
                        onChange={(e) => setWordDocFolderName(e.target.value)}
                        disabled={loading}
                      />
                      <p className="option-hint">
                        {wordDocFolderName.trim()
                          ? `✅ Word docs will be saved to: ~/Desktop/ARC DEALERS SCREENSHOT WORD DOCS/${wordDocFolderName.trim()}/`
                          : "⚠️ Word docs will be saved directly to: ~/Desktop/ARC DEALERS SCREENSHOT WORD DOCS/"}
                      </p>
                    </div>

                    {/* Right: Beautify Button */}
                    <div className="beautify-all-section">
                      <button
                        onClick={beautifyAllTextBoxes}
                        disabled={
                          loading || textBoxes.every((box) => !box.urls.trim())
                        }
                        className="beautify-button"
                        title="Clean up and format URLs in all text boxes (one per line, only http:// or https://)"
                      >
                        ✨ Beautify All Text Boxes
                      </button>
                    </div>
                  </div>

                  <div className="multiple-textboxes-container">
                    {textBoxes.map((textBox, index) => (
                      <div key={textBox.id} className="textbox-group">
                        <div className="textbox-header-inline">
                          <div className="textbox-title-and-input">
                            <label className="textbox-inline-label">
                              <strong>
                                Text Box {index + 1} 📝 Session Name (for Word
                                doc):
                              </strong>
                            </label>
                            <input
                              type="text"
                              className="session-name-input-field-inline"
                              placeholder="e.g., Accounting, Parts, Service"
                              value={textBox.sessionName}
                              onChange={(e) =>
                                updateTextBox(
                                  textBox.id,
                                  "sessionName",
                                  e.target.value
                                )
                              }
                              disabled={loading}
                            />
                          </div>

                          {/* ✅ NEW: Batch Timeout Input (per text box) */}
                          <div
                            className="textbox-title-and-input"
                            style={{ marginLeft: "20px" }}
                          >
                            <label className="textbox-inline-label">
                              <strong>⏱️ Batch Timeout (secs):</strong>
                            </label>
                            <input
                              type="number"
                              className="session-name-input-field-inline"
                              placeholder="90"
                              min="10"
                              max="300"
                              value={textBox.batchTimeout || 90}
                              onChange={(e) => {
                                // ✅ FIXED: Only update local state, NO API calls
                                const newValue = parseInt(e.target.value);
                                if (
                                  !isNaN(newValue) &&
                                  newValue >= 10 &&
                                  newValue <= 300
                                ) {
                                  const updatedTextBoxes = textBoxes.map((tb) =>
                                    tb.id === textBox.id
                                      ? { ...tb, batchTimeout: newValue }
                                      : tb
                                  );
                                  setTextBoxes(updatedTextBoxes);
                                }
                              }}
                              onBlur={(e) => {
                                // ✅ FIXED: Only call API when user finishes typing (on blur)
                                const newValue = parseInt(e.target.value);
                                if (
                                  !isNaN(newValue) &&
                                  newValue >= 10 &&
                                  newValue <= 300
                                ) {
                                  updateBatchTimeout(textBox.id, newValue);
                                }
                              }}
                              disabled={loading}
                              style={{ width: "80px" }}
                            />
                          </div>

                          <button
                            className="remove-textbox-btn"
                            onClick={() => removeTextBox(textBox.id)}
                            disabled={loading || textBoxes.length <= 1}
                            title="Remove this text box"
                          >
                            ➖ Remove
                          </button>
                        </div>

                        <div className="textbox-urls">
                          <label>
                            <strong>🔗 URLs (one per line):</strong>
                          </label>
                          <div className="textarea-wrapper">
                            {/* Textarea */}
                            <textarea
                              className="textbox-urls-textarea"
                              placeholder="https://example.com&#10;https://google.com"
                              value={textBox.urls}
                              onChange={(e) => {
                                updateTextBox(
                                  textBox.id,
                                  "urls",
                                  e.target.value
                                );
                                // Auto-resize textarea
                                e.target.style.height = "auto";
                                e.target.style.height =
                                  e.target.scrollHeight + "px";
                              }}
                              onScroll={(e) => {
                                const lineNumbers = document.getElementById(
                                  `line-numbers-${textBox.id}`
                                );
                                if (lineNumbers) {
                                  lineNumbers.scrollTop =
                                    e.currentTarget.scrollTop;
                                }
                              }}
                              onFocus={(e) => {
                                // Expand on focus
                                e.target.style.height = "auto";
                                e.target.style.height =
                                  e.target.scrollHeight + "px";
                              }}
                              onBlur={(e) => {
                                // Shrink to minimum on blur if content is small
                                const lineCount =
                                  textBox.urls.split("\n").length;
                                const minRows = 6;
                                if (lineCount <= minRows) {
                                  e.target.style.height = "auto";
                                }
                              }}
                              rows={6}
                              disabled={loading}
                              style={{
                                backgroundImage: `linear-gradient(transparent 0px, transparent 7px, transparent 8px, transparent 19.5px),
                                  repeating-linear-gradient(
                                    transparent,
                                    transparent 19.5px,
                                    #e5e7eb 19.5px,
                                    #e5e7eb 20px
                                  )`,
                                backgroundAttachment: "local",
                                backgroundPosition: "60px 8px",
                                lineHeight: "19.5px",
                                minHeight: "135px",
                                overflow: "hidden",
                              }}
                            />
                            {/* Line numbers - sequential S.No for URLs only */}
                            <div
                              className="line-numbers-hardcoded"
                              id={`line-numbers-${textBox.id}`}
                              style={{
                                position: "absolute",
                                left: "1px",
                                top: "1px",
                                bottom: "1px",
                                width: "50px",
                                padding: "8px 0",
                                paddingLeft: "8px",
                                fontFamily: '"Courier New", monospace',
                                fontSize: "13px",
                                lineHeight: "19.5px",
                                color: "rgba(0, 0, 0, 0.5)",
                                userSelect: "none",
                                pointerEvents: "none",
                                zIndex: 10,
                                textAlign: "right",
                                borderRight: "1px solid rgba(0, 0, 0, 0.1)",
                                background: "rgba(249, 250, 251, 0.9)",
                                overflow: "hidden",
                                borderTopLeftRadius: "3px",
                                borderBottomLeftRadius: "3px",
                                boxSizing: "border-box",
                              }}
                            >
                              {(() => {
                                const lines = textBox.urls.split("\n");
                                let sno = 0;
                                return lines.map((line, lineIndex) => {
                                  const hasUrl = line.trim() !== "";
                                  if (hasUrl) sno++;
                                  return (
                                    <div
                                      key={lineIndex}
                                      style={{
                                        height: "19.5px",
                                        lineHeight: "19.5px",
                                        paddingRight: "8px",
                                        fontWeight: 600,
                                        fontSize: "13px",
                                        textAlign: "right",
                                      }}
                                    >
                                      {hasUrl ? sno : ""}
                                    </div>
                                  );
                                });
                              })()}
                            </div>
                          </div>

                          {/* ✅ NEW: @mention folder detection for each text box */}
                          {(() => {
                            const mentionedFolder = detectFolderMention(
                              textBox.urls
                            );
                            if (mentionedFolder && urlFolders.length > 0) {
                              const folder = urlFolders.find(
                                (f) =>
                                  f.name.toLowerCase() ===
                                  mentionedFolder.toLowerCase()
                              );
                              if (folder) {
                                return (
                                  <div className="folder-mention-hint">
                                    <p>
                                      💡 Detected folder mention:{" "}
                                      <strong>@{mentionedFolder}</strong>
                                    </p>
                                    <button
                                      className="load-folder-btn"
                                      onClick={() => {
                                        // Load URLs into this specific text box
                                        updateTextBox(
                                          textBox.id,
                                          "urls",
                                          folder.urls.join("\n")
                                        );
                                        addLog(
                                          `✅ Loaded ${folder.urls.length} URL(s) from folder "${folder.name}" into Text Box`
                                        );
                                      }}
                                      disabled={loading}
                                    >
                                      📁 Load {folder.urls.length} URL(s) from "
                                      {folder.name}"
                                    </button>
                                  </div>
                                );
                              } else {
                                return (
                                  <div className="folder-mention-hint error">
                                    <p>
                                      ⚠️ Folder{" "}
                                      <strong>@{mentionedFolder}</strong> not
                                      found
                                    </p>
                                  </div>
                                );
                              }
                            }

                            // Show available folders hint if there are folders
                            if (urlFolders.length > 0 && !textBox.urls.trim()) {
                              return (
                                <div className="folder-hint">
                                  <p>
                                    💡 Tip: Type <strong>@foldername</strong> to
                                    load saved URLs
                                  </p>
                                  <p className="available-folders">
                                    Available folders:{" "}
                                    {urlFolders
                                      .map((f) => `@${f.name}`)
                                      .join(", ")}
                                  </p>
                                </div>
                              );
                            }
                            return null;
                          })()}
                        </div>
                      </div>
                    ))}

                    <button
                      className="add-textbox-btn"
                      onClick={addTextBox}
                      disabled={loading}
                    >
                      ➕ Add Another Text Box
                    </button>
                  </div>
                </>
              ) : (
                /* ✅ EXISTING: Single text box mode */
                <>
                  <div className="input-header">
                    <h2>Enter URLs (one per line)</h2>
                    {/* Beautify Button */}
                    <button
                      onClick={beautifyUrls}
                      disabled={loading || !urls.trim()}
                      className="beautify-button"
                      title="Clean up and format URLs (one per line, only http:// or https://)"
                    >
                      ✨ Beautify
                    </button>
                  </div>

                  <div className="textarea-wrapper">
                    {/* Line numbers overlay */}
                    <div className="line-numbers" ref={lineNumbersRef}>
                      {/* ⚡ OPTIMIZATION: Use memoized urlLines instead of re-splitting */}
                      {urlLines.map((line, index) => (
                        <div key={index} className="line-number">
                          {line.trim() !== "" ? index + 1 : ""}
                        </div>
                      ))}
                    </div>
                    {/* Textarea */}
                    <textarea
                      ref={textareaRef}
                      value={urls}
                      onChange={(e) => setUrls(e.target.value)}
                      onScroll={handleTextareaScroll}
                      placeholder="https://example.com&#10;https://google.com&#10;https://github.com"
                      rows={10}
                      disabled={loading}
                      className="numbered-textarea"
                    />
                  </div>

                  {/* @mention folder detection */}
                  {(() => {
                    const mentionedFolder = detectFolderMention(urls);
                    if (mentionedFolder && urlFolders.length > 0) {
                      const folder = urlFolders.find(
                        (f) =>
                          f.name.toLowerCase() === mentionedFolder.toLowerCase()
                      );
                      if (folder) {
                        return (
                          <div className="folder-mention-hint">
                            <p>
                              💡 Detected folder mention:{" "}
                              <strong>@{mentionedFolder}</strong>
                            </p>
                            <button
                              className="load-folder-btn"
                              onClick={() => loadFolderUrls(mentionedFolder)}
                              disabled={loading}
                            >
                              📁 Load {folder.urls.length} URL(s) from "
                              {folder.name}"
                            </button>
                          </div>
                        );
                      } else {
                        return (
                          <div className="folder-mention-hint error">
                            <p>
                              ❌ Folder <strong>@{mentionedFolder}</strong> not
                              found!
                            </p>
                          </div>
                        );
                      }
                    }
                    // Show available folders hint if there are folders
                    if (urlFolders.length > 0 && !urls.trim()) {
                      return (
                        <div className="folder-hint">
                          <p>
                            💡 Tip: Type <strong>@foldername</strong> to load
                            saved URLs
                          </p>
                          <p className="available-folders">
                            Available folders:{" "}
                            {urlFolders.map((f) => `@${f.name}`).join(", ")}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  })()}
                </>
              )}

              <div className="button-group">
                <button onClick={handleCapture} disabled={loading}>
                  {loading ? "Capturing..." : "Capture Screenshots"}
                </button>

                {loading && (
                  <button onClick={handleStop} className="stop-btn">
                    ⏹️ Stop Capture
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : null}

        {loading && (
          <div className="progress">
            <p>
              Progress: {progress.current} / {progress.total}
            </p>
          </div>
        )}

        {results.length > 0 && (
          <div className="results-section">
            <h2>Results ({results.length})</h2>

            <button onClick={handleGenerateDocument} className="generate-btn">
              Generate Word Document
            </button>

            <div className="results-grid">
              {results.map((result, index) => (
                <div key={index} className={`result-card ${result.status}`}>
                  <h3>Screenshot {index + 1}</h3>

                  {/* Truncated URL with hover/click tooltip */}
                  <div className="url-container">
                    <p
                      className="url truncated"
                      onMouseEnter={() => handleUrlMouseEnter(index)}
                      onMouseLeave={handleUrlMouseLeave}
                      onClick={() => handleUrlClick(index)}
                      title="Hover 3s or click to see full URL"
                    >
                      {result.url}
                    </p>
                    {(hoveredUrl === index || clickedUrl === index) && (
                      <div className="url-tooltip">{result.url}</div>
                    )}
                  </div>

                  {/* Status badge with inline quality score */}
                  <div className="status-quality-row">
                    <div className="status-badge">
                      {result.status === "success"
                        ? "✅"
                        : result.status === "cancelled"
                        ? "⏹️"
                        : "❌"}{" "}
                      {result.status}
                    </div>

                    {result.quality_score !== undefined &&
                      result.quality_score !== null && (
                        <span className="quality-score inline">
                          Quality: {result.quality_score.toFixed(1)}%
                        </span>
                      )}
                  </div>

                  {result.quality_issues &&
                    result.quality_issues.length > 0 && (
                      <div className="quality-issues">
                        <strong>Issues:</strong>
                        <ul>
                          {result.quality_issues.map((issue, i) => (
                            <li key={i}>{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {result.error && (
                    <p className="error">Error: {result.error}</p>
                  )}

                  {/* Show segment count for segmented captures */}
                  {result.segment_count !== undefined &&
                    result.segment_count !== null &&
                    result.segment_count > 1 && (
                      <p className="segment-count">
                        📚 {result.segment_count} segments captured
                      </p>
                    )}

                  {result.screenshot_path && (
                    <p className="path">Saved: {result.screenshot_path}</p>
                  )}

                  {result.status === "success" &&
                    (result.screenshot_paths || result.screenshot_path) && (
                      <>
                        {/* Show all segments for segmented captures */}
                        {result.screenshot_paths &&
                        result.screenshot_paths.length > 0 ? (
                          <>
                            <div className="segments-container">
                              <div
                                className="segments-header"
                                onClick={() => toggleSegmentExpansion(index)}
                                role="button"
                                tabIndex={0}
                                onKeyPress={(e) => {
                                  if (e.key === "Enter" || e.key === " ") {
                                    toggleSegmentExpansion(index);
                                  }
                                }}
                              >
                                <p className="segments-label">
                                  <span className="expand-icon">
                                    {expandedSegments.has(index) ? "▼" : "▶"}
                                  </span>
                                  📸 {result.screenshot_paths.length} segments
                                  captured -{" "}
                                  {expandedSegments.has(index)
                                    ? "Click to collapse"
                                    : "Click to view all"}
                                </p>
                              </div>

                              {expandedSegments.has(index) && (
                                <div className="segments-list">
                                  {result.screenshot_paths.map(
                                    (segmentPath, segIdx) => (
                                      <div
                                        key={segIdx}
                                        className="screenshot-preview segment-preview"
                                      >
                                        <p className="segment-number">
                                          Segment {segIdx + 1}
                                        </p>
                                        <img
                                          src={`http://127.0.0.1:8000/api/screenshots/file/${encodeURIComponent(
                                            segmentPath
                                          )}`}
                                          alt={`Segment ${segIdx + 1} preview`}
                                          className="preview-image"
                                        />
                                      </div>
                                    )
                                  )}
                                </div>
                              )}
                            </div>
                            <div className="action-buttons">
                              <button
                                onClick={() =>
                                  handleOpenFile(result.screenshot_paths![0])
                                }
                                className="open-file-btn"
                              >
                                📄 Open First Segment
                              </button>
                              <button
                                onClick={() =>
                                  handleOpenFolder(result.screenshot_paths![0])
                                }
                                className="open-folder-btn"
                              >
                                📁 Open Folder
                              </button>
                            </div>
                          </>
                        ) : (
                          /* Show single screenshot for non-segmented captures */
                          <>
                            <div className="screenshot-preview">
                              <img
                                src={`http://127.0.0.1:8000/api/screenshots/file/${encodeURIComponent(
                                  result.screenshot_path!
                                )}`}
                                alt="Screenshot preview"
                                className="preview-image"
                              />
                            </div>
                            <div className="action-buttons">
                              <button
                                onClick={() =>
                                  handleOpenFile(result.screenshot_path!)
                                }
                                className="open-file-btn"
                              >
                                📄 Open File
                              </button>
                              <button
                                onClick={() =>
                                  handleOpenFolder(result.screenshot_path!)
                                }
                                className="open-folder-btn"
                              >
                                📁 Open Folder
                              </button>
                            </div>
                          </>
                        )}
                      </>
                    )}

                  {result.status === "failed" && (
                    <button
                      onClick={() => handleRetry(result.url)}
                      className="retry-btn"
                    >
                      🔄 Retry
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Login URL Modal */}
        {showLoginModal && (
          <div
            className="modal-overlay"
            onClick={() => setShowLoginModal(false)}
          >
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>🔓 Login & Save Auth State</h2>
              <p className="modal-description">
                Enter the URL where you want to log in. A browser window will
                open where you can complete your login (Okta/MFA/etc.).
              </p>
              <label htmlFor="login-url-input">Login URL:</label>
              <input
                id="login-url-input"
                type="text"
                className="login-url-input"
                value={loginUrl}
                onChange={(e) => setLoginUrl(e.target.value)}
                placeholder="https://preprodapp.tekioncloud.com/home"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") startLogin();
                  if (e.key === "Escape") setShowLoginModal(false);
                }}
              />
              <div className="modal-actions">
                <button
                  className="modal-btn modal-btn-primary"
                  onClick={startLogin}
                  disabled={!loginUrl.trim()}
                >
                  🔓 Start Login
                </button>
                <button
                  className="modal-btn modal-btn-secondary"
                  onClick={() => setShowLoginModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ✅ Word Transformation Editor Modal */}
        {showWordEditor && (
          <div
            className="modal-overlay"
            style={{ zIndex: 99998 }}
            onClick={closeWordEditor}
          >
            <div
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
              style={{ maxWidth: "500px" }}
            >
              <h2>
                ✏️ {editingWordIndex !== null ? "Edit" : "Add"} Word
                Transformation
              </h2>

              <div style={{ marginTop: "20px" }}>
                <label
                  style={{
                    display: "block",
                    marginBottom: "8px",
                    fontWeight: "500",
                  }}
                >
                  Word to Find:
                </label>
                <input
                  type="text"
                  className="base-url-input"
                  placeholder="e.g., Accounting, dse-v2, .png"
                  value={editorWord}
                  onChange={(e) => setEditorWord(e.target.value)}
                  autoFocus
                  style={{ marginBottom: "20px" }}
                />

                <label
                  style={{
                    display: "block",
                    marginBottom: "8px",
                    fontWeight: "500",
                  }}
                >
                  Replacement Type:
                </label>
                <div style={{ marginBottom: "20px" }}>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="editorType"
                      value="remove"
                      checked={editorType === "remove"}
                      onChange={(e) => setEditorType("remove")}
                    />
                    <span className="radio-text">
                      🗑️ Remove (delete completely)
                    </span>
                  </label>

                  <label className="radio-label">
                    <input
                      type="radio"
                      name="editorType"
                      value="space"
                      checked={editorType === "space"}
                      onChange={(e) => setEditorType("space")}
                    />
                    <span className="radio-text">␣ Replace with Space</span>
                  </label>

                  <label className="radio-label">
                    <input
                      type="radio"
                      name="editorType"
                      value="custom"
                      checked={editorType === "custom"}
                      onChange={(e) => setEditorType("custom")}
                    />
                    <span className="radio-text">
                      ✏️ Replace with Custom Text
                    </span>
                  </label>
                </div>

                {editorType === "custom" && (
                  <>
                    <label
                      style={{
                        display: "block",
                        marginBottom: "8px",
                        fontWeight: "500",
                      }}
                    >
                      Custom Replacement Text:
                    </label>
                    <input
                      type="text"
                      className="base-url-input"
                      placeholder="e.g., Sales Chains"
                      value={editorReplacement}
                      onChange={(e) => setEditorReplacement(e.target.value)}
                      style={{ marginBottom: "20px" }}
                    />
                  </>
                )}

                <div
                  style={{
                    background: "#f0f0f0",
                    padding: "12px",
                    borderRadius: "6px",
                    marginBottom: "20px",
                    fontSize: "13px",
                  }}
                >
                  <strong>Preview:</strong> {editorWord || "[word]"} →{" "}
                  {editorType === "remove"
                    ? "[removed]"
                    : editorType === "space"
                    ? "[space]"
                    : editorReplacement || "[custom text]"}
                </div>
              </div>

              <div className="modal-actions">
                <button
                  className="modal-btn modal-btn-primary"
                  onClick={saveWordTransformation}
                  disabled={
                    !editorWord.trim() ||
                    (editorType === "custom" && !editorReplacement.trim())
                  }
                >
                  💾 Save
                </button>
                <button
                  className="modal-btn modal-btn-secondary"
                  onClick={closeWordEditor}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ✅ Custom Dialog (replaces browser alert/confirm) */}
        {customDialog.show && (
          <div
            className="modal-overlay"
            style={{ zIndex: 99999 }}
            onClick={(e) => {
              e.stopPropagation();
              // Prevent closing by clicking overlay for dialogs
            }}
          >
            <div
              className="modal-content custom-dialog-modal"
              onClick={(e) => e.stopPropagation()}
              style={{
                maxWidth: "500px",
                padding: "30px",
                textAlign: "center",
              }}
            >
              <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
                {customDialog.title}
              </h2>
              <p
                style={{
                  marginBottom: "30px",
                  fontSize: "16px",
                  lineHeight: "1.6",
                  whiteSpace: "pre-wrap",
                }}
              >
                {customDialog.message}
              </p>
              <div
                className="modal-actions"
                style={{ gap: "15px", justifyContent: "center" }}
              >
                {customDialog.type === "confirm" && (
                  <button
                    className="modal-btn modal-btn-secondary"
                    onClick={() => customDialog.onCancel?.()}
                    style={{
                      minWidth: "100px",
                      padding: "12px 24px",
                      fontSize: "16px",
                    }}
                  >
                    Cancel
                  </button>
                )}
                <button
                  className="modal-btn modal-btn-primary"
                  onClick={() => customDialog.onConfirm?.()}
                  autoFocus
                  style={{
                    minWidth: "100px",
                    padding: "12px 24px",
                    fontSize: "16px",
                  }}
                >
                  OK
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  } catch (error: any) {
    console.error("Render error:", error);
    return (
      <div className="container">
        <h1>📸 Screenshot Tool - ERROR</h1>
        <div
          style={{
            background: "#ffebee",
            border: "2px solid #f44336",
            padding: "20px",
            borderRadius: "8px",
            margin: "20px",
            color: "#c62828",
          }}
        >
          <h2>⚠️ Application Error</h2>
          <p>
            <strong>Error:</strong> {error.message}
          </p>
          <p>
            <strong>Stack:</strong>
          </p>
          <pre
            style={{ background: "#fff", padding: "10px", overflow: "auto" }}
          >
            {error.stack}
          </pre>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      </div>
    );
  }
}

export default App;
