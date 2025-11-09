/**
 * Word document generation with embedded screenshots
 */

import { Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType } from 'docx';
import fs from 'fs';
import path from 'path';
import sharp from 'sharp';
import { config } from './config.js';
import { logger } from './logger.js';

/**
 * Generate a Word document from screenshot results
 * @param {object[]} results - Array of screenshot results
 * @param {string} outputPath - Path to save the document
 * @returns {Promise<string>} Path to the generated document
 */
export async function generateDocument(results, outputPath) {
  logger.info('Generating Word document...');

  const sections = [];

  // Title page
  sections.push(
    new Paragraph({
      text: 'Website Screenshots Report',
      heading: HeadingLevel.TITLE,
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 }
    }),
    new Paragraph({
      text: `Generated: ${new Date().toLocaleString()}`,
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 }
    }),
    new Paragraph({
      text: `Total URLs: ${results.length}`,
      alignment: AlignmentType.CENTER,
      spacing: { after: 800 }
    })
  );

  // Add each screenshot
  for (let i = 0; i < results.length; i++) {
    const result = results[i];
    
    // Page break before each new screenshot (except first)
    if (i > 0) {
      sections.push(
        new Paragraph({
          text: '',
          pageBreakBefore: true
        })
      );
    }

    // URL heading
    sections.push(
      new Paragraph({
        text: `${i + 1}. ${result.url}`,
        heading: HeadingLevel.HEADING_1,
        spacing: { after: 200 }
      })
    );

    if (result.failed) {
      // Error message
      sections.push(
        new Paragraph({
          children: [
            new TextRun({
              text: `❌ Failed to capture: ${result.error}`,
              color: 'FF0000',
              bold: true
            })
          ],
          spacing: { after: 400 }
        })
      );
    } else {
      // Metadata
      sections.push(
        new Paragraph({
          children: [
            new TextRun({
              text: `Captured: ${new Date(result.timestamp).toLocaleString()}`,
              size: 20,
              color: '666666'
            })
          ],
          spacing: { after: 200 }
        }),
        new Paragraph({
          children: [
            new TextRun({
              text: `Size: ${(result.size / 1024).toFixed(2)} KB | Duration: ${result.duration}ms`,
              size: 20,
              color: '666666'
            })
          ],
          spacing: { after: 400 }
        })
      );

      // Embed screenshot
      try {
        const imageBuffer = await processImage(result.path);
        const dimensions = await getImageDimensions(result.path);

        sections.push(
          new Paragraph({
            children: [
              new ImageRun({
                data: imageBuffer,
                transformation: {
                  width: config.document.imageWidth,
                  height: (config.document.imageWidth / dimensions.width) * dimensions.height
                }
              })
            ],
            spacing: { after: 400 }
          })
        );
      } catch (error) {
        logger.error(`Failed to embed image for ${result.url}: ${error.message}`);
        sections.push(
          new Paragraph({
            children: [
              new TextRun({
                text: `⚠️ Failed to embed screenshot: ${error.message}`,
                color: 'FFA500'
              })
            ],
            spacing: { after: 400 }
          })
        );
      }
    }
  }

  // Create document
  const doc = new Document({
    sections: [{
      properties: {
        page: {
          size: {
            width: config.document.pageSize.width,
            height: config.document.pageSize.height
          },
          margin: config.document.margins
        }
      },
      children: sections
    }]
  });

  // Write to file
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);

  const stats = fs.statSync(outputPath);
  logger.success(`Document generated: ${path.basename(outputPath)} (${(stats.size / 1024).toFixed(2)} KB)`);

  return outputPath;
}

/**
 * Process image for embedding (optimize if needed)
 */
async function processImage(imagePath) {
  const image = sharp(imagePath);
  const metadata = await image.metadata();

  // If image is very large, resize it
  if (metadata.width > 2000) {
    return await image
      .resize(2000, null, { withoutEnlargement: true })
      .png({ quality: 90 })
      .toBuffer();
  }

  return fs.readFileSync(imagePath);
}

/**
 * Get image dimensions
 */
async function getImageDimensions(imagePath) {
  const metadata = await sharp(imagePath).metadata();
  return {
    width: metadata.width,
    height: metadata.height
  };
}

