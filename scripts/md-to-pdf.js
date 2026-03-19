const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function markdownToPDF(inputFile, outputFile) {
  const markdown = fs.readFileSync(inputFile, 'utf8');
  
  // Convert markdown to HTML (simple conversion)
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 800px;
      margin: 40px auto;
      padding: 20px;
      line-height: 1.6;
      color: #333;
    }
    h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
    h2 { color: #1e40af; margin-top: 30px; }
    h3 { color: #3b82f6; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background: #f8fafc; font-weight: 600; }
    code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
    blockquote { border-left: 4px solid #2563eb; margin: 0; padding-left: 20px; color: #64748b; }
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }
  </style>
</head>
<body>
  ${markdown
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
    .replace(/^\|(.+)\|$/gim, (match, p1) => `<tr>${p1.split('|').map(c => `<td>${c.trim()}</td>`).join('')}</tr>`)
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[h|t|r|p|a|b|u])(.+)$/gim, '<p>$1</p>')
  }
</body>
</html>`;

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'networkidle0' });
  
  await page.pdf({
    path: outputFile,
    format: 'A4',
    margin: { top: '40px', right: '40px', bottom: '40px', left: '40px' },
    printBackground: true
  });
  
  await browser.close();
  console.log(`PDF created: ${outputFile}`);
}

const inputFile = process.argv[2] || 'content/content-ideas-2025.md';
const outputFile = process.argv[3] || 'content/content-ideas-2025.pdf';

markdownToPDF(inputFile, outputFile).catch(console.error);
