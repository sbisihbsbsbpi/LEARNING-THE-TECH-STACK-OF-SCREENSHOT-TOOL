#!/usr/bin/env node

/**
 * Setup script to verify environment and dependencies
 */

import { findChrome, ensureDirectories } from './config.js';
import { logger } from './logger.js';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function checkNode() {
  const version = process.version;
  const major = parseInt(version.slice(1).split('.')[0]);
  
  if (major >= 18) {
    logger.success(`Node.js ${version} ✓`);
    return true;
  } else {
    logger.error(`Node.js ${version} - Please upgrade to v18 or higher`);
    return false;
  }
}

async function checkChrome() {
  const chromePath = findChrome();
  if (chromePath) {
    logger.success(`Chrome/Chromium found: ${chromePath} ✓`);
    return true;
  } else {
    logger.error('Chrome/Chromium not found');
    logger.info('Please install Google Chrome from: https://www.google.com/chrome/');
    return false;
  }
}

async function checkAppleScript() {
  try {
    await execAsync('osascript -e "return 1"');
    logger.success('AppleScript available ✓');
    return true;
  } catch (error) {
    logger.error('AppleScript not available');
    return false;
  }
}

async function testBrowserAccess() {
  logger.info('Testing browser access (this may prompt for permissions)...');
  
  const script = `
    tell application "System Events"
      set frontApp to name of first application process whose frontmost is true
      return frontApp
    end tell
  `;

  try {
    const { stdout } = await execAsync(`osascript -e '${script}'`);
    logger.success(`System Events access: ${stdout.trim()} ✓`);
    return true;
  } catch (error) {
    logger.warn('System Events access may require permission');
    logger.info('Go to: System Preferences > Privacy & Security > Automation');
    return false;
  }
}

async function setup() {
  logger.title('🔧 Setup & Environment Check');
  logger.divider();

  const checks = [
    await checkNode(),
    await checkChrome(),
    await checkAppleScript(),
    await testBrowserAccess()
  ];

  logger.divider();

  // Create directories
  logger.info('Creating required directories...');
  ensureDirectories();
  logger.success('Directories created ✓');

  logger.divider();

  const allPassed = checks.every(c => c);
  
  if (allPassed) {
    logger.title('✅ Setup Complete!');
    logger.success('All checks passed. You can now run: npm start');
  } else {
    logger.title('⚠️  Setup Incomplete');
    logger.warn('Some checks failed. Please resolve the issues above.');
  }
}

setup().catch(error => {
  logger.error('Setup failed:');
  console.error(error);
  process.exit(1);
});

