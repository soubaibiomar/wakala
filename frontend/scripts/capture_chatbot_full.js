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
    const chatInput = await page.$('textarea, input[placeholder*="message" i], input[placeholder*="Posez" i], input[placeholder*="Rechercher" i]');
    if (chatInput) {
      console.log('Sending message to chatbot...');
      await chatInput.type('Bonjour, quel est le meilleur SUV diesel pour une famille ?', { delay: 25 });
      await sleep(500);
      
      const sendBtn = await page.$('button[type="submit"], [class*="send" i], [class*="submit" i]');
      if (sendBtn) {
        await sendBtn.click();
      } else {
        await page.keyboard.press('Enter');
      }

      console.log('Waiting for response...');
      // Wait until typing indicator disappears or text messages are rendered
      await sleep(12000);
    }

    const finalShot = path.join(ARTIFACT_DIR, '05_chatbot_full_conversation.png');
    await page.screenshot({ path: finalShot, fullPage: false });
    console.log('Saved:', finalShot);
  } catch (err) {
    console.error('Error:', err);
  } finally {
    await browser.close();
  }
}

run();
