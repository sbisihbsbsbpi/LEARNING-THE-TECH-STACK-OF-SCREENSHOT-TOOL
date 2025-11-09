/**
 * Configuration for the headless screenshot tool
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const config = {
  // Chrome/Chromium paths to try (macOS)
  chromePaths: [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
  ],

  // Screenshot settings
  screenshot: {
    fullPage: true,
    type: 'png',
    quality: 90,
    waitUntil: 'networkidle2',
    timeout: 60000,
    viewport: {
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1
    }
  },

  // Document settings
  document: {
    pageSize: {
      width: 8.5 * 914.4, // inches to twips (1 inch = 914.4 twips)
      height: 11 * 914.4
    },
    margins: {
      top: 720,    // 0.5 inch
      right: 720,
      bottom: 720,
      left: 720
    },
    imageWidth: 6.5 * 914.4 // 6.5 inches in twips
  },

  // Directories
  dirs: {
    screenshots: path.join(process.cwd(), 'screenshots'),
    output: path.join(process.cwd(), 'output'),
    temp: path.join(process.cwd(), 'temp'),
    assets: path.join(__dirname, '..', 'assets')
  },

  // Retry settings
  retry: {
    maxAttempts: 3,
    delayMs: 2000
  }
};

/**
 * Find the first available Chrome/Chromium executable
 */
export function findChrome() {
  for (const chromePath of config.chromePaths) {
    if (fs.existsSync(chromePath)) {
      return chromePath;
    }
  }
  return null;
}

/**
 * Ensure required directories exist
 */
export function ensureDirectories() {
  Object.values(config.dirs).forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

