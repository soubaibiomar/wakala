import puppeteer from 'puppeteer-core';
import path from 'path';

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || path.resolve(process.cwd(), '../output');
const EDGE_PATH = process.env.EDGE_PATH || 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function run() {
  const browser = await puppeteer.launch({
    executablePath: EDGE_PATH,
    headless: true,
    defaultViewport: { width: 1440, height: 900 },
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
  });

  try {
    const page = await browser.newPage();
    await page.goto('http://localhost:3000/catalogue', { waitUntil: 'networkidle2', timeout: 30000 });
    await sleep(2000);

    // Open Chatbot
    const trigger = await page.$('button[aria-label*="chat" i], .chatbot-trigger, [class*="trigger" i]');
    if (trigger) {
      await trigger.click();
      await sleep(1500);
    }

    // Send query
    const chatInput = await page.$('textarea, input[placeholder*="message" i], input[placeholder*="Posez" i]');
    if (chatInput) {
      await chatInput.type('Bonjour, quel SUV me conseillez-vous pour la ville ?', { delay: 20 });
      await sleep(500);
      await page.keyboard.press('Enter');
      console.log('Waiting 15s for full streaming response...');
      await sleep(15000);
    }

    const finalChatShot = path.join(ARTIFACT_DIR, '06_chatbot_completed_stream.png');
    await page.screenshot({ path: finalChatShot, fullPage: false });
    console.log('Saved:', finalChatShot);
  } catch (err) {
    console.error('Error:', err);
  } finally {
    await browser.close();
  }
}

run();
