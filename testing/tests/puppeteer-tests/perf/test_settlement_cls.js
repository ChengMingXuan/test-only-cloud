const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  await browser.close();
})();
