/**
 * Browser automation and screenshot capture using Puppeteer
 */

import puppeteer from 'puppeteer-core';
import { config, findChrome } from './config.js';
import { logger } from './logger.js';
import fs from 'fs';
import path from 'path';

/**
 * Capture screenshot of a URL
 * @param {string} url - The URL to capture
 * @param {string} outputPath - Path to save the screenshot
 * @param {object} options - Additional options
 * @returns {Promise<object>} Screenshot metadata
 */
export async function captureScreenshot(url, outputPath, options = {}) {
  const executablePath = findChrome();
  
  if (!executablePath) {
    throw new Error(
      'No Chrome/Chromium browser found. Please install Google Chrome or Chromium.\n' +
      'Download from: https://www.google.com/chrome/'
    );
  }

  logger.debug(`Using browser: ${executablePath}`);
  logger.info(`Capturing: ${url}`);

  const browser = await puppeteer.launch({
    executablePath,
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--hide-scrollbars',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process'
    ]
  });

  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport(config.screenshot.viewport);

    // Set user agent to avoid bot detection
    await page.setUserAgent(
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );

    // Navigate to URL with timeout
    const startTime = Date.now();
    await page.goto(url, {
      waitUntil: config.screenshot.waitUntil,
      timeout: config.screenshot.timeout
    });

    // Wait a bit for any lazy-loaded content
    await page.waitForTimeout(1000);

    // Scroll to bottom to trigger lazy loading
    await autoScroll(page);

    // Take screenshot
    await page.screenshot({
      path: outputPath,
      fullPage: config.screenshot.fullPage,
      type: config.screenshot.type
    });

    const duration = Date.now() - startTime;
    const stats = fs.statSync(outputPath);

    logger.success(`Screenshot saved: ${path.basename(outputPath)} (${(stats.size / 1024).toFixed(2)} KB, ${duration}ms)`);

    return {
      url,
      path: outputPath,
      size: stats.size,
      duration,
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    logger.error(`Failed to capture ${url}: ${error.message}`);
    throw error;
  } finally {
    await browser.close();
  }
}

/**
 * Auto-scroll page to trigger lazy loading
 */
async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 100;
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;

        if (totalHeight >= scrollHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 100);
    });
  });
}

/**
 * Capture multiple URLs with retry logic
 * @param {string[]} urls - Array of URLs to capture
 * @param {function} progressCallback - Progress callback function
 * @returns {Promise<object[]>} Array of screenshot metadata
 */
export async function captureMultiple(urls, progressCallback = null) {
  const results = [];
  
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    const filename = `screenshot_${i + 1}_${Date.now()}.png`;
    const outputPath = path.join(config.dirs.screenshots, filename);

    let attempt = 0;
    let success = false;
    let result = null;

    while (attempt < config.retry.maxAttempts && !success) {
      attempt++;
      try {
        if (attempt > 1) {
          logger.warn(`Retry attempt ${attempt}/${config.retry.maxAttempts} for ${url}`);
          await sleep(config.retry.delayMs);
        }

        result = await captureScreenshot(url, outputPath);
        success = true;
        results.push(result);

      } catch (error) {
        if (attempt === config.retry.maxAttempts) {
          logger.error(`Failed after ${attempt} attempts: ${url}`);
          results.push({
            url,
            error: error.message,
            failed: true
          });
        }
      }
    }

    if (progressCallback) {
      progressCallback(i + 1, urls.length, url, success);
    }
  }

  return results;
}

/**
 * Sleep utility
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

