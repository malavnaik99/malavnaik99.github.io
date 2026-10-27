// Theme, menu, tabs, ask-chips, copy buttons, blog filter and the live pipeline readout.
// Vanilla JS; every word of content is already in the HTML, so the site works without it.
(function () {
  var root = document.documentElement;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };

  var themeBtn = $(".theme-btn");
  if (themeBtn) themeBtn.addEventListener("click", function () {
    root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light";
    try { localStorage.setItem("theme", root.dataset.theme); } catch (e) {}
  });

  // Gujarati button: on Google Translate's copy of the site it becomes "English" and goes back to the same page on malavnaik.com.
  var langBtn = $(".lang-btn");
  if (langBtn && /\.translate\.goog$/.test(location.hostname)) {
    var original = "https://malavnaik.com" + location.pathname + location.hash;
    langBtn.textContent = "English"; langBtn.lang = "en"; langBtn.hreflang = "en"; langBtn.title = "Back to the English page";
    langBtn.href = original;
    langBtn.addEventListener("click", function (e) { e.preventDefault(); location.href = original; });
  }

  var menuBtn = $(".menu-btn"), nav = $("#site-nav");
  if (menuBtn && nav) menuBtn.addEventListener("click", function () {
    menuBtn.setAttribute("aria-expanded", nav.classList.toggle("open"));
  });

  // Toolkit constellation: label each node with the matching tool from its tab panel.
  $$(".constellation .area").forEach(function (g) {
    var tools = $$("#" + g.dataset.panel + " li");
    $$("text", g).forEach(function (t, i) { if (tools[i]) t.textContent = tools[i].textContent; });
  });

  // Toolkit tabs (WAI-ARIA tabs pattern: arrows, Home and End move between tabs).
  $$("[role=tablist]").forEach(function (list) {
    var tabs = $$("[role=tab]", list);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on);
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      $$(".constellation .area").forEach(function (g) { g.classList.toggle("on", g.dataset.panel === tab.getAttribute("aria-controls")); });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var n = { ArrowDown: i + 1, ArrowRight: i + 1, ArrowUp: i - 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
        if (n === undefined) return;
        e.preventDefault();
        select(tabs[(n + tabs.length) % tabs.length], true);
      });
    });
  });

  // "Ask about my work": example chips reveal their pre-written answer; free text isn't live yet.
  var chips = $$("[data-answer]");
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (c) {
        var on = c === chip && c.getAttribute("aria-expanded") !== "true";
        c.setAttribute("aria-expanded", on);
        document.getElementById(c.dataset.answer).hidden = !on;
      });
      var soon = $("#ask-soon"); if (soon) soon.hidden = true;
    });
  });
  var askForm = $("#ask-form");
  if (askForm) askForm.addEventListener("submit", function (e) {
    e.preventDefault();
    chips.forEach(function (c) { c.setAttribute("aria-expanded", false); document.getElementById(c.dataset.answer).hidden = true; });
    $("#ask-soon").hidden = false;
  });

  // Copy buttons on code blocks, and "Copy link" on posts.
  function copyButton(label, getText, cls) {
    var b = document.createElement("button");
    b.type = "button"; b.className = cls; b.textContent = label;
    b.addEventListener("click", function () {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(getText()).then(function () {
        b.textContent = "Copied"; setTimeout(function () { b.textContent = label; }, 1500);
      });
    });
    return b;
  }
  $$(".prose pre").forEach(function (pre) {
    pre.appendChild(copyButton("Copy", function () { var c = $("code", pre); return (c || pre).innerText; }, "copy-btn"));
  });
  var shareCopy = $("[data-copy-link]");
  if (shareCopy) shareCopy.replaceWith(copyButton("Copy link", function () { return location.href.split("#")[0]; }, "btn small"));

  // Blog index: filter by series.
  var filters = $$("[data-filter]");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filters.forEach(function (b) { b.setAttribute("aria-pressed", b === btn); });
      $$("[data-series]").forEach(function (card) {
        card.hidden = btn.dataset.filter !== "all" && card.dataset.series !== btn.dataset.filter;
      });
    });
  });

  // Automation Lab sandbox: replay the CSS animation of the approval flow.
  $$("[data-play-flow]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var flow = btn.closest(".sandbox-card").querySelector(".flow-anim");
      flow.classList.remove("playing"); void flow.offsetWidth; flow.classList.add("playing");
    });
  });

  // Sandboxes are islands: their code loads only when a visitor opens one.
  $$("[data-island-load]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var box = btn.closest("[data-island]"), name = box.dataset.island;
      btn.disabled = true;
      var run = function () { window.islands[name](box); };
      if (window.islands && window.islands[name]) return run();
      var sc = document.createElement("script");
      sc.src = "/assets/islands/" + name + ".js";
      sc.onload = run;
      document.head.appendChild(sc);
    });
  });

  if (location.hash === "#sql") { var sqlBtn = $("#sql [data-island-load]"); if (sqlBtn) sqlBtn.click(); }

  // Ctrl+K (or the search button) loads the search island on first use.
  function openSearch() {
    if (window.openSearch) return window.openSearch();
    var sc = document.createElement("script");
    sc.src = "/assets/islands/search.js";
    sc.onload = function () { window.openSearch(); };
    document.head.appendChild(sc);
  }
  var searchBtn = $(".search-btn");
  if (searchBtn) searchBtn.addEventListener("click", openSearch);
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
  });

  // Hero: the h1 "decodes" under an aria-hidden copy (the real text stays in the page), and a spotlight follows the mouse on desktop.
  var hero = $(".hero"), h1 = hero && $("h1", hero);
  var still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (h1 && !still) {
    var line = h1.textContent, pool = "01#$%&ABCDEF<>/{}", tick = 0;
    var over = document.createElement("span");
    over.className = "decode"; over.setAttribute("aria-hidden", "true");
    h1.appendChild(over); h1.classList.add("decoding");
    var timer = setInterval(function () {
      var upto = Math.floor(Math.min(1, ++tick / 36) * line.length), out = "";
      for (var i = 0; i < line.length; i++) out += i < upto || line[i] === " " ? line[i] : pool[(i * 7 + tick * 3) % pool.length];
      over.textContent = out;
      if (upto >= line.length) { clearInterval(timer); h1.classList.remove("decoding"); over.remove(); }
    }, 45);
  }
  if (hero && !still && matchMedia("(pointer: fine) and (min-width: 761px)").matches) hero.addEventListener("pointermove", function (e) {
    var r = hero.getBoundingClientRect();
    hero.style.setProperty("--mx", (e.clientX - r.left) / r.width * 100 + "%");
    hero.style.setProperty("--my", (e.clientY - r.top) / r.height * 100 + "%");
  });

  // Live signals ticker: a tap or click pauses and resumes it (hover pauses it too, in CSS).
  var ticker = $(".ticker");
  if (ticker) ticker.addEventListener("click", function () { ticker.classList.toggle("paused"); });

  // Live pipeline readout: the latest successful run of the public Dublin bikes collector on GitHub Actions.
  // Without an answer within 4 seconds, the page keeps saying "runs every 15 min" and claims nothing live.
  var live = $$("[data-pipeline]");
  if (live.length && window.fetch && window.AbortController) {
    var ctl = new AbortController();
    setTimeout(function () { ctl.abort(); }, 4000);
    fetch("https://api.github.com/repos/malavnaik99/dublin-data-pipeline/actions/workflows/ingest.yml/runs?per_page=1&status=success", { signal: ctl.signal })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        var run = d && d.workflow_runs && d.workflow_runs[0];
        if (!run) return;
        var mins = Math.max(0, Math.round((Date.now() - Date.parse(run.updated_at)) / 60000));
        if (mins > 60) return; // more than a few missed runs: don't call it live
        live.forEach(function (el) {
          el.classList.add("is-live");
          $(".status", el).textContent = "live · last run " + (mins < 1 ? "just now" : mins + " min ago");
        });
      })
      .catch(function () {});
  }
})();
