// Temporary (Signal preview): full pages, mobile/desktop, dark/light, plus an opened project card and the toolkit graph.
import { chromium } from "playwright";
const out = process.argv[2], base = "http://localhost:8080";
const pages = [["home", "/"], ["post", "/blog/precision-recall-content-moderation/"], ["work", "/work/"], ["writing", "/writing/"], ["about", "/about/"]];
const browser = await chromium.launch();
async function open(path, width, height, scheme, label) {
  const page = await browser.newPage({ viewport: { width, height }, colorScheme: scheme });
  page.on("pageerror", e => console.log(`JS error (${label}): ${e.message}`));
  page.on("console", m => { if (m.type() === "error") console.log(`console error (${label}): ${m.text()}`); });
  await page.goto(base + path, { waitUntil: "networkidle" });
  await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(2500); // lazy images, and the h1 decode
  return page;
}
for (const [name, path] of pages)
  for (const [vp, width, height] of [["mobile", 390, 844], ["desktop", 1440, 900]])
    for (const scheme of ["dark", "light"]) {
      const page = await open(path, width, height, scheme, `${name} ${vp} ${scheme}`);
      await page.screenshot({ path: `${out}/${name}-${vp}-${scheme}.png`, fullPage: true });
      await page.close();
    }
for (const scheme of ["dark", "light"]) { // a project card opened (moderation sandbox) and the GenAI toolkit tab
  const page = await open("/", 1440, 900, scheme, `home details ${scheme}`);
  await page.click("#tab-genai");
  await (await page.$("#toolkit")).screenshot({ path: `${out}/toolkit-genai-desktop-${scheme}.png` });
  await page.click(".row:nth-child(1) summary");
  await page.waitForTimeout(600);
  await (await page.$(".rows")).screenshot({ path: `${out}/projects-open-desktop-${scheme}.png` });
  await page.close();
}
await browser.close();
