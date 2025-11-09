/**
 * macOS active browser tab detection using AppleScript
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { logger } from './logger.js';

const execAsync = promisify(exec);

/**
 * Get the URL of the active tab from Safari
 */
async function getSafariActiveTab() {
  const script = `
    tell application "Safari"
      if (count of windows) > 0 then
        return URL of current tab of front window
      end if
    end tell
  `;

  try {
    const { stdout } = await execAsync(`osascript -e '${script}'`);
    return stdout.trim();
  } catch (error) {
    throw new Error('Failed to get Safari active tab. Make sure Safari is running and has an open tab.');
  }
}

/**
 * Get the URL of the active tab from Chrome
 */
async function getChromeActiveTab() {
  const script = `
    tell application "Google Chrome"
      if (count of windows) > 0 then
        return URL of active tab of front window
      end if
    end tell
  `;

  try {
    const { stdout } = await execAsync(`osascript -e '${script}'`);
    return stdout.trim();
  } catch (error) {
    throw new Error('Failed to get Chrome active tab. Make sure Chrome is running and has an open tab.');
  }
}

/**
 * Get the URL of the active tab from Brave
 */
async function getBraveActiveTab() {
  const script = `
    tell application "Brave Browser"
      if (count of windows) > 0 then
        return URL of active tab of front window
      end if
    end tell
  `;

  try {
    const { stdout } = await execAsync(`osascript -e '${script}'`);
    return stdout.trim();
  } catch (error) {
    throw new Error('Failed to get Brave active tab. Make sure Brave is running and has an open tab.');
  }
}

/**
 * Get the URL of the active tab from Edge
 */
async function getEdgeActiveTab() {
  const script = `
    tell application "Microsoft Edge"
      if (count of windows) > 0 then
        return URL of active tab of front window
      end if
    end tell
  `;

  try {
    const { stdout } = await execAsync(`osascript -e '${script}'`);
    return stdout.trim();
  } catch (error) {
    throw new Error('Failed to get Edge active tab. Make sure Edge is running and has an open tab.');
  }
}

/**
 * Detect which browser is frontmost and get its active tab
 */
async function detectActiveBrowser() {
  const script = `
    tell application "System Events"
      set frontApp to name of first application process whose frontmost is true
      return frontApp
    end tell
  `;

  try {
    const { stdout } = await execAsync(`osascript -e '${script}'`);
    return stdout.trim();
  } catch (error) {
    return null;
  }
}

/**
 * Get the active tab URL from any supported browser
 * @returns {Promise<{url: string, browser: string}>}
 */
export async function getActiveTabURL() {
  logger.info('Detecting active browser tab...');

  const frontApp = await detectActiveBrowser();
  logger.debug(`Front application: ${frontApp}`);

  const browsers = [
    { name: 'Safari', fn: getSafariActiveTab },
    { name: 'Google Chrome', fn: getChromeActiveTab },
    { name: 'Brave Browser', fn: getBraveActiveTab },
    { name: 'Microsoft Edge', fn: getEdgeActiveTab }
  ];

  // Try the frontmost app first if it's a browser
  const frontBrowser = browsers.find(b => frontApp && frontApp.includes(b.name.split(' ')[0]));
  if (frontBrowser) {
    try {
      const url = await frontBrowser.fn();
      if (url) {
        logger.success(`Got active tab from ${frontBrowser.name}: ${url}`);
        return { url, browser: frontBrowser.name };
      }
    } catch (error) {
      logger.debug(`Failed to get tab from ${frontBrowser.name}: ${error.message}`);
    }
  }

  // Try all browsers
  for (const browser of browsers) {
    try {
      const url = await browser.fn();
      if (url) {
        logger.success(`Got active tab from ${browser.name}: ${url}`);
        return { url, browser: browser.name };
      }
    } catch (error) {
      logger.debug(`${browser.name}: ${error.message}`);
    }
  }

  throw new Error(
    'Could not get active tab URL from any browser.\n' +
    'Make sure one of these browsers is running with an open tab:\n' +
    '  - Safari\n' +
    '  - Google Chrome\n' +
    '  - Brave Browser\n' +
    '  - Microsoft Edge\n\n' +
    'Note: You may need to grant Terminal/VS Code permission to control these apps in System Preferences > Privacy & Security > Automation.'
  );
}

