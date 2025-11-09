/**
 * Simple logging utility with colors
 */

import chalk from 'chalk';

export const logger = {
  info: (message) => {
    console.log(chalk.blue('ℹ'), message);
  },

  success: (message) => {
    console.log(chalk.green('✓'), message);
  },

  warn: (message) => {
    console.log(chalk.yellow('⚠'), message);
  },

  error: (message) => {
    console.log(chalk.red('✗'), message);
  },

  debug: (message) => {
    if (process.env.DEBUG) {
      console.log(chalk.gray('→'), message);
    }
  },

  title: (message) => {
    console.log('\n' + chalk.bold.cyan(message) + '\n');
  },

  divider: () => {
    console.log(chalk.gray('─'.repeat(60)));
  }
};

