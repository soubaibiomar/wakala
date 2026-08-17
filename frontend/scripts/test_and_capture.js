import puppeteer from 'puppeteer-core';
import path from 'path';

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || path.resolve(process.cwd(), '../output');
const EDGE_PATH = process.env.EDGE_PATH || 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function run() {
  console.log('Launching browser with Edge...');
  const browser = await puppeteer.launch({
    executablePath: EDGE_PATH,
    headless: true,
    defaultViewport: { width: 1440, height: 900 },
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
  });

  try {
    const page = await browser.newPage();

    // ─── 1. Home Page ───────────────────────────────────────────
    console.log('Navigating to http://localhost:3000...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle2', timeout: 30000 });
    
    console.log('Waiting 4.5s for HeroIntro animation to complete...');
    await sleep(4500);

    const homeShot = path.join(ARTIFACT_DIR, '01_home_hero_search.png');
    await page.screenshot({ path: homeShot, fullPage: false });
    console.log('Saved:', homeShot);

    // ─── 2. Search Bar Interaction ──────────────────────────────
    console.log('Testing NLP Search input on Hero...');
    const searchInput = await page.$('#nlp-search-input, input.search-input');
    if (searchInput) {
      console.log('Typing query into NLP Search Bar...');
      await searchInput.type('SUV familial diesel budget 250000 DH', { delay: 35 });
      await sleep(1000);

      const submitBtn = await page.$('#nlp-search-submit, button.search-btn, button[type="submit"]');
      if (submitBtn) {
        console.log('Clicking search submit...');
        await submitBtn.click();
        console.log('Waiting for Priority Modal to open...');
        await sleep(3500);
      }
    }

    const modalShot = path.join(ARTIFACT_DIR, '02_priority_modal.png');
    await page.screenshot({ path: modalShot, fullPage: false });
    console.log('Saved:', modalShot);

    // Submit Priority Modal
    const modalBtn = await page.$('button.priority-modal__submit, button[type="submit"].priority-modal-btn, .priority-modal button');
    if (modalBtn) {
      console.log('Submitting Priority Modal...');
      await modalBtn.click();
      await sleep(3500);
    }

    // ─── 3. Catalogue Recommendations Results ───────────────────
    console.log('Checking Catalogue page...');
    const currentUrl = page.url();
    if (!currentUrl.includes('/catalogue')) {
      await page.goto('http://localhost:3000/catalogue', { waitUntil: 'networkidle2', timeout: 30000 });
      await sleep(2500);
    }

    const catShot = path.join(ARTIFACT_DIR, '03_recommendation_catalogue.png');
    await page.screenshot({ path: catShot, fullPage: false });
    console.log('Saved:', catShot);

    // ─── 4. Test Chatbot Widget ─────────────────────────────────
    console.log('Opening AI Chatbot widget...');
    const trigger = await page.$('button[aria-label*="chat" i], .chatbot-trigger, [class*="trigger" i]');
    if (trigger) {
      await trigger.click();
      await sleep(1500);
    }

    const chatOpenedShot = path.join(ARTIFACT_DIR, '04_chatbot_opened.png');
    await page.screenshot({ path: chatOpenedShot, fullPage: false });
    console.log('Saved:', chatOpenedShot);

    // ─── 5. Test Chatbot Message & Streaming Response ───────────
    console.log('Sending message to AI Chatbot...');
    const chatInput = await page.$('textarea, input[placeholder*="message" i], input[placeholder*="Posez" i]');
    if (chatInput) {
      await chatInput.type('Bonjour, propose-moi un SUV familial fiable a moins de 220 000 MAD', { delay: 20 });
      await sleep(500);
      await page.keyboard.press('Enter');
      console.log('Message sent, waiting 10s for streaming response and car cards...');
      await sleep(10000);
    }

    const chatResponseShot = path.join(ARTIFACT_DIR, '05_chatbot_response.png');
    await page.screenshot({ path: chatResponseShot, fullPage: false });
    console.log('Saved:', chatResponseShot);

    console.log('All 5 screenshots captured successfully!');
  } catch (err) {
    console.error('Error during testing & capturing:', err);
  } finally {
    await browser.close();
  }
}

run();
