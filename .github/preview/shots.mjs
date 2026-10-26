// Temporary (redesign preview): screenshots light/dark, mobile/desktop.
import { chromium } from "playwright";
const out = process.argv[2], base = "http://localhost:8080";
const pages = [["home", "/"], ["post", "/blog/precision-recall-content-moderation/"], ["work", "/work/"], ["writing", "/writing/"], ["about", "/about/"]];
const browser = await chromium.launch();
for (const [name, path] of pages)
  for (const [vp, width, height] of [["mobile", 390, 844], ["desktop", 1280, 800]])
    for (const scheme of ["dark", "light"]) {
      const page = await browser.newPage({ viewport: { width, height }, colorScheme: scheme });
      page.on("pageerror", e => console.log(`JS error on ${name}: ${e.message}`));
      page.on("console", m => { if (m.type() === "error") console.log(`console error on ${name}: ${m.text()}`); });
      await page.goto(base + path, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(500);
      await page.screenshot({ path: `${out}/${name}-${vp}-${scheme}.png`, fullPage: true });
      await page.close();
    }
{ // the Ctrl+K search box, open with a query
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, colorScheme: "dark" });
  await page.goto(base + "/writing/", { waitUntil: "networkidle" });
  await page.keyboard.press("Control+k");
  await page.waitForSelector("dialog[open] input");
  await page.keyboard.type("dublin");
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${out}/search-desktop-dark.png` });
  await page.close();
}
for (const [name, path, sel] of [["sandbox-moderation", "/projects/moderation-classifier/", "#sandbox-moderation"], ["sandbox-dsa", "/projects/ask-the-dsa/", "#sandbox-dsa"], ["sandbox-automation", "/projects/blog-automation-bot/", "#sandbox-automation"]]) // sandboxes, opened
  for (const [vp, width, height] of [["mobile", 390, 844], ["desktop", 1280, 900]])
    for (const scheme of ["dark", "light"]) {
      const page = await browser.newPage({ viewport: { width, height }, colorScheme: scheme });
      page.on("pageerror", e => console.log(`JS error on ${name}: ${e.message}`));
      await page.goto(base + path, { waitUntil: "networkidle" });
      await page.click(`${sel} [data-island-load], ${sel} [data-play-flow]`);
      await page.waitForTimeout(1500);
      await (await page.$(sel)).screenshot({ path: `${out}/${name}-${vp}-${scheme}.png` });
      await page.close();
    }
for (const [vp, width, height] of [["mobile", 390, 844], ["desktop", 1280, 900]]) { // SQL console: open, run each example
  const page = await browser.newPage({ viewport: { width, height }, colorScheme: vp === "desktop" ? "dark" : "light" });
  page.on("pageerror", e => console.log(`JS error on sql: ${e.message}`));
  await page.goto(base + "/projects/dublin-bikes-pipeline/", { waitUntil: "networkidle" });
  await page.click("#sql [data-island-load]");
  await page.waitForFunction(() => /Ready|rows?\b/.test(document.querySelector("#sql [data-status]")?.textContent || ""), null, { timeout: 60000 }).catch(() => {});
  for (const q of ["empty", "hours", "rain"]) {
    await page.click(`#sql [data-sql="${q}"]`);
    await page.waitForTimeout(1500);
    console.log(`sql ${vp} ${q}: ${await page.textContent("#sql [data-status]")}`);
  }
  await (await page.$("#sql")).screenshot({ path: `${out}/sandbox-sql-${vp}.png` });
  await page.close();
}
await browser.close();
