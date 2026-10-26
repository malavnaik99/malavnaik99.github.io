// Temporary (Signal preview): home page, mobile/desktop, dark/light, full page and first screen.
import { chromium } from "playwright";
const out = process.argv[2], base = "http://localhost:8080";
const browser = await chromium.launch();
for (const [vp, width, height] of [["mobile", 390, 844], ["desktop", 1440, 900]])
  for (const scheme of ["dark", "light"]) {
    const page = await browser.newPage({ viewport: { width, height }, colorScheme: scheme });
    page.on("pageerror", e => console.log(`JS error (${vp} ${scheme}): ${e.message}`));
    page.on("console", m => { if (m.type() === "error") console.log(`console error (${vp} ${scheme}): ${m.text()}`); });
    await page.goto(base + "/", { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(2500); // let the h1 decode finish
    await page.screenshot({ path: `${out}/home-${vp}-${scheme}-first-screen.png` });
    const bottom = await page.$eval(".metrics", el => el.getBoundingClientRect().bottom + scrollY + 48);
    await page.screenshot({ path: `${out}/home-${vp}-${scheme}-to-metrics.png`, fullPage: true, clip: { x: 0, y: 0, width, height: bottom } });
    if (vp === "mobile") { // the Menu, opened
      await page.click(".menu-btn");
      await page.screenshot({ path: `${out}/home-mobile-${scheme}-menu.png` });
    }
    await page.close();
  }
await browser.close();
