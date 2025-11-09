#!/usr/bin/env node

/**
 * Simple test script to verify the tool works
 */

import { captureMultiple } from './browser.js';
import { generateDocument } from './document.js';
import { logger } from './logger.js';
import { ensureDirectories } from './config.js';
import path from 'path';

async function runTest() {
  logger.title('🧪 Running Test');
  logger.info('This will capture a screenshot of example.com and generate a test document');
  logger.divider();

  // Ensure directories exist
  ensureDirectories();

  // Test URLs
  const testUrls = ['https://example.com'];

  logger.info('Test URL: https://example.com');
  logger.divider();

  try {
    // Capture screenshots
    logger.info('Capturing screenshot...');
    const results = await captureMultiple(testUrls, (current, total, url, success) => {
      if (success) {
        logger.success(`Captured ${current}/${total}: ${url}`);
      } else {
        logger.error(`Failed ${current}/${total}: ${url}`);
      }
    });

    logger.divider();

    // Generate document
    logger.info('Generating test document...');
    const outputPath = path.join(process.cwd(), 'output', 'test-output.docx');
    await generateDocument(results, outputPath);

    logger.divider();
    logger.title('✅ Test Passed!');
    logger.success(`Test document created: ${outputPath}`);
    logger.info('You can now run: npm start');

  } catch (error) {
    logger.divider();
    logger.title('❌ Test Failed');
    logger.error(error.message);
    console.error(error);
    process.exit(1);
  }
}

runTest();

