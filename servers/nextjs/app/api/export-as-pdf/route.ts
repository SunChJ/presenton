import path from 'path';
import fs from 'fs';
import puppeteer from 'puppeteer';

import { sanitizeFilename } from '@/app/(presentation-generator)/utils/others';
import { NextResponse, NextRequest } from 'next/server';


export async function POST(req: NextRequest) {
  const { id, title } = await req.json();
  console.log(`[PDF Export] Starting export for presentation: ${id}`);
  
  if (!id) {
    return NextResponse.json({ error: "Missing Presentation ID" }, { status: 400 });
  }
  
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-web-security',
    ]
  });
  const page = await browser.newPage();
  
  // Enable console logging from the page
  page.on('console', (msg) => console.log(`[Page Console] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', (error) => console.error(`[Page Error] ${error.message}`));
  
  await page.setViewport({ width: 1280, height: 720 });
  page.setDefaultNavigationTimeout(300000);
  page.setDefaultTimeout(300000);

  const targetUrl = `http://localhost:5001/pdf-maker?id=${id}`;
  console.log(`[PDF Export] Navigating to: ${targetUrl}`);
  
  await page.goto(targetUrl, { waitUntil: 'networkidle0', timeout: 300000 });

  console.log(`[PDF Export] Page loaded, waiting for document ready...`);
  await page.waitForFunction('() => document.readyState === "complete"')

  // Check if we're on an error page
  const isErrorPage = await page.evaluate(() => {
    const errorText = document.body.textContent || '';
    return errorText.includes('We encountered an issue loading your presentation') ||
           errorText.includes('Failed to load presentation');
  });

  if (isErrorPage) {
    console.error(`[PDF Export] Error page detected - presentation failed to load`);
    const pageContent = await page.content();
    console.log(`[PDF Export] Page HTML: ${pageContent.substring(0, 500)}...`);
  } else {
    console.log(`[PDF Export] Presentation page loaded successfully`);
  }

  // Debug: Log what puppeteer can see
  console.log(`[PDF Export] Analyzing page structure...`);
  const pageDebugInfo = await page.evaluate(() => {
    const wrapper = document.getElementById('presentation-slides-wrapper');
    const body = document.body;
    
    return {
      hasWrapper: !!wrapper,
      wrapperHTML: wrapper ? wrapper.outerHTML.substring(0, 500) : 'No wrapper found',
      wrapperChildren: wrapper ? wrapper.children.length : 0,
      wrapperInnerHTML: wrapper ? wrapper.innerHTML.substring(0, 800) : 'No wrapper',
      allDataSpeakerNotes: document.querySelectorAll('[data-speaker-note]').length,
      bodyClasses: body.className,
      bodyDataAttributes: Object.keys(body.dataset),
      divCount: document.querySelectorAll('div').length,
      totalElements: document.querySelectorAll('*').length
    };
  });
  
  console.log(`[PDF Export] Page structure:`, JSON.stringify(pageDebugInfo, null, 2));

  // Wait specifically for presentation slides to load
  try {
    console.log(`[PDF Export] Waiting for presentation slides...`);
    await page.waitForFunction(
      () => {
        const wrapper = document.getElementById('presentation-slides-wrapper');
        if (!wrapper) {
          console.log('No presentation-slides-wrapper found');
          return false;
        }
        
        // Try different selectors to find slides
        const allDivs = wrapper.querySelectorAll('div');
        const speakerNotes = wrapper.querySelectorAll('[data-speaker-note]');
        const slideElements1 = wrapper.querySelectorAll(':scope > div > div[data-speaker-note]');
        const slideElements2 = wrapper.querySelectorAll(':scope > div > div');
        const slideElements3 = document.querySelectorAll('[data-speaker-note]');
        
        console.log(`Wrapper found. Children: ${wrapper.children.length}`);
        console.log(`All divs in wrapper: ${allDivs.length}`);
        console.log(`Speaker notes in wrapper: ${speakerNotes.length}`);
        console.log(`Selector1 (:scope > div > div[data-speaker-note]): ${slideElements1.length}`);
        console.log(`Selector2 (:scope > div > div): ${slideElements2.length}`);
        console.log(`Selector3 (all data-speaker-note): ${slideElements3.length}`);
        
        // Return true if we find any slides using any method
        return slideElements3.length > 0 || slideElements2.length > 0;
      },
      { timeout: 30000 }
    );
    console.log(`[PDF Export] Slides loaded successfully`);

    await new Promise(resolve => setTimeout(resolve, 2000)); // Extra wait

  } catch (error) {
    console.error(`[PDF Export] Failed to load slides:`, error);
    
    // Get final page state for debugging
    const finalPageInfo = await page.evaluate(() => {
      const wrapper = document.getElementById('presentation-slides-wrapper');
      return {
        wrapperExists: !!wrapper,
        wrapperContent: wrapper ? wrapper.outerHTML.substring(0, 1000) : 'No wrapper',
        pageTitle: document.title,
        bodyText: document.body.innerText.substring(0, 500)
      };
    });
    
    console.log(`[PDF Export] Final page state:`, JSON.stringify(finalPageInfo, null, 2));
  }


  // Extract the first slide title from the page
  const firstSlideTitle = await page.evaluate(() => {
    const wrapper = document.getElementById('presentation-slides-wrapper');
    if (!wrapper) return null;
    
    const firstSlide = wrapper.querySelector('[data-speaker-note]');
    if (!firstSlide) return null;
    
    // Look for the main title in the first slide (common patterns)
    const titleSelectors = [
      'h1', 'h2', 'h3', 
      '[style*="font-size: 48px"]', '[style*="font-size: 36px"]', '[style*="font-size: 32px"]',
      '.text-4xl', '.text-3xl', '.text-2xl',
      '.font-bold'
    ];
    
    for (const selector of titleSelectors) {
      const titleElement = firstSlide.querySelector(selector);
      if (titleElement && titleElement.textContent && titleElement.textContent.trim().length > 0) {
        return titleElement.textContent.trim();
      }
    }
    
    // Fallback: get any text from first slide
    const allText = firstSlide.textContent || '';
    const lines = allText.split('\n').filter(line => line.trim().length > 0);
    return lines[0] || null;
  });

  console.log(`[PDF Export] Extracted first slide title: "${firstSlideTitle}"`);
  
  console.log(`[PDF Export] Generating PDF...`);
  const pdfBuffer = await page.pdf({
    width: "1280px",
    height: "720px",
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  console.log(`[PDF Export] PDF generated, size: ${pdfBuffer.length} bytes`);
  browser.close();

  // Use first slide title or fallback to provided title
  const finalTitle = firstSlideTitle || title || 'presentation';
  const sanitizedTitle = sanitizeFilename(finalTitle);
  const destinationPath = path.join(process.env.APP_DATA_DIRECTORY!, 'exports', `${sanitizedTitle}.pdf`);
  await fs.promises.mkdir(path.dirname(destinationPath), { recursive: true });
  await fs.promises.writeFile(destinationPath, pdfBuffer);

  console.log(`[PDF Export] PDF saved to: ${destinationPath}`);

  // Convert absolute path to relative URL path for frontend access
  const relativePath = path.relative(process.env.APP_DATA_DIRECTORY!, destinationPath);
  const downloadUrl = `/app_data/exports/${path.basename(destinationPath)}`;
  
  console.log(`[PDF Export] Download URL: ${downloadUrl}`);

  return NextResponse.json({
    success: true,
    path: downloadUrl
  });
}
