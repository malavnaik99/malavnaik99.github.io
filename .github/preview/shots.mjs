// Temporary (redesign preview): screenshots of 4 pages, light/dark, mobile/desktop.
import { chromium } from "playwright";
const out = process.argv[2], base = "http://localhost:8080";
const pages = [["home", "/"], ["blog", "/blog/"], ["post", "/blog/precision-recall-content-moderation/"], ["about", "/about/"]];
const browser = await chromium.launch();
for (const [name, path] of pages)
  for (const [vp, width, height] of [["mobile", 390, 844], ["desktop", 1280, 800]])
    for (const scheme of ["light", "dark"]) {
      const page = await browser.newPage({ viewport: { width, height }, colorScheme: scheme });
      page.on("pageerror", e => console.log(`JS error on ${name}: ${e.message}`));
      await page.goto(base + path, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: `${out}/${name}-${vp}-${scheme}.png`, fullPage: true });
      await page.close();
    }
await browser.close();
