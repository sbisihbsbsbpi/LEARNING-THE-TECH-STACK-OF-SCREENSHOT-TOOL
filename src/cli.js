#!/usr/bin/env node

/**
 * CLI interface for the headless screenshot tool
 */

import inquirer from 'inquirer';
import ora from 'ora';
import chalk from 'chalk';
import path from 'path';
import { config, ensureDirectories, findChrome } from './config.js';
import { captureMultiple } from './browser.js';
import { generateDocument } from './document.js';
import { getActiveTabURL } from './activeTab.js';
import { logger } from './logger.js';

// Ensure directories exist
ensureDirectories();

/**
 * Main CLI function
 */
async function main() {
  console.clear();
  
  logger.title('📸 Headless Screenshot Tool');
  logger.info('Capture website screenshots and generate Word documents');
  logger.divider();

  // Check for Chrome
  const chromePath = findChrome();
  if (!chromePath) {
    logger.error('No Chrome/Chromium browser found!');
    logger.info('Please install Google Chrome from: https://www.google.com/chrome/');
    process.exit(1);
  }
  logger.success(`Found browser: ${path.basename(path.dirname(chromePath))}`);
  logger.divider();

  // Get input method
  const { inputMethod } = await inquirer.prompt([
    {
      type: 'list',
      name: 'inputMethod',
      message: 'How would you like to provide URLs?',
      choices: [
        { name: '📝 Enter URLs manually', value: 'manual' },
        { name: '🌐 Capture active browser tab', value: 'active' },
        { name: '📋 Paste multiple URLs (one per line)', value: 'paste' }
      ]
    }
  ]);

  let urls = [];

  if (inputMethod === 'active') {
    // Get active tab
    const spinner = ora('Detecting active browser tab...').start();
    try {
      const { url, browser } = await getActiveTabURL();
      spinner.succeed(`Got URL from ${browser}`);
      urls = [url];
      logger.info(`URL: ${chalk.cyan(url)}`);
    } catch (error) {
      spinner.fail('Failed to get active tab');
      logger.error(error.message);
      process.exit(1);
    }
  } else if (inputMethod === 'manual') {
    // Manual entry
    let addMore = true;
    while (addMore) {
      const { url } = await inquirer.prompt([
        {
          type: 'input',
          name: 'url',
          message: `Enter URL ${urls.length + 1}:`,
          validate: (input) => {
            if (!input.trim()) return 'URL cannot be empty';
            if (!input.startsWith('http://') && !input.startsWith('https://')) {
              return 'URL must start with http:// or https://';
            }
            return true;
          }
        }
      ]);
      urls.push(url.trim());

      const { more } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'more',
          message: 'Add another URL?',
          default: false
        }
      ]);
      addMore = more;
    }
  } else if (inputMethod === 'paste') {
    // Paste multiple
    const { urlText } = await inquirer.prompt([
      {
        type: 'editor',
        name: 'urlText',
        message: 'Paste URLs (one per line):',
        default: 'https://example.com\nhttps://github.com'
      }
    ]);

    urls = urlText
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && (line.startsWith('http://') || line.startsWith('https://')));

    if (urls.length === 0) {
      logger.error('No valid URLs found');
      process.exit(1);
    }
  }

  logger.divider();
  logger.info(`Total URLs to capture: ${chalk.bold(urls.length)}`);
  logger.divider();

  // Confirm
  const { proceed } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'proceed',
      message: 'Proceed with screenshot capture?',
      default: true
    }
  ]);

  if (!proceed) {
    logger.warn('Cancelled by user');
    process.exit(0);
  }

  // Capture screenshots
  logger.title('📸 Capturing Screenshots');
  
  const spinner = ora('Initializing...').start();
  let completed = 0;
  let failed = 0;

  const results = await captureMultiple(urls, (current, total, url, success) => {
    completed = current;
    if (!success) failed++;
    spinner.text = `Progress: ${current}/${total} (${failed} failed)`;
  });

  spinner.succeed(`Captured ${completed} screenshots (${failed} failed)`);

  // Generate document
  logger.divider();
  logger.title('📄 Generating Word Document');

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
  const outputFilename = `screenshots_${timestamp}_${Date.now()}.docx`;
  const outputPath = path.join(config.dirs.output, outputFilename);

  const docSpinner = ora('Creating document...').start();
  try {
    await generateDocument(results, outputPath);
    docSpinner.succeed('Document created successfully');
  } catch (error) {
    docSpinner.fail('Failed to create document');
    logger.error(error.message);
    process.exit(1);
  }

  // Summary
  logger.divider();
  logger.title('✅ Complete!');
  logger.success(`Document saved to: ${chalk.cyan(outputPath)}`);
  logger.info(`Total screenshots: ${results.filter(r => !r.failed).length}/${urls.length}`);
  
  if (failed > 0) {
    logger.warn(`Failed captures: ${failed}`);
  }

  logger.divider();

  // Open document
  const { openDoc } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'openDoc',
      message: 'Open the document now?',
      default: true
    }
  ]);

  if (openDoc) {
    const { exec } = await import('child_process');
    exec(`open "${outputPath}"`);
    logger.success('Opening document...');
  }
}

// Run CLI
main().catch(error => {
  logger.error('Fatal error:');
  console.error(error);
  process.exit(1);
});

