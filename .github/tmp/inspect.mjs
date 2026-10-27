// Temporary: list what Google Translate's proxy adds around the page, so its top bar can be hidden.
import { chromium } from "playwright";
const b = await chromium.launch({ channel: "chrome" });
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.goto("https://malavnaik-com.translate.goog/?_x_tr_sl=en&_x_tr_tl=gu&_x_tr_hl=gu", { waitUntil: "networkidle" });
await p.waitForTimeout(4000);
console.log(JSON.stringify(await p.evaluate(() => {
  const d = el => ({ tag: el.tagName, id: el.id, cls: String(el.className).slice(0, 80), pos: getComputedStyle(el).position, h: Math.round(el.getBoundingClientRect().height), top: Math.round(el.getBoundingClientRect().top) });
  return {
    htmlStyle: document.documentElement.getAttribute("style"), bodyStyle: document.body.getAttribute("style"),
    bodyCS: { marginTop: getComputedStyle(document.body).marginTop, top: getComputedStyle(document.body).top, position: getComputedStyle(document.body).position },
    htmlKids: [...document.documentElement.children].map(d), bodyKids: [...document.body.children].map(d),
    fixedOrTop: [...document.querySelectorAll("body *")].filter(el => { const r = el.getBoundingClientRect(); return r.top < 80 && r.height > 30 && r.width > 1000; }).slice(0, 12).map(d),
    iframes: [...document.querySelectorAll("iframe")].map(f => ({ id: f.id, cls: f.className, src: (f.src || "").slice(0, 100), parent: f.parentElement.tagName + "#" + f.parentElement.id + "." + f.parentElement.className })),
    header: document.querySelector(".site-header") && Math.round(document.querySelector(".site-header").getBoundingClientRect().top),
  };
}), null, 1));
await b.close();
