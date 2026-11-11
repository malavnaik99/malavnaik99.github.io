// Theme, menu, tabs, the Ask box, copy buttons, blog filter, sandbox islands and the live pipeline readout.
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
    // Malav's own spelling of his name is માલવ નાયક: set it on the wordmarks, and correct Google's "નાઈક" wherever it translates the name.
    $$(".wordmark, .footer-wordmark").forEach(function (w) { w.textContent = "માલવ નાયક"; w.lang = "gu"; });
    var fixName = function () {
      var walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), n;
      while ((n = walk.nextNode())) if (/નાઈક/.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(/નાઈક/g, "નાયક");
    };
    fixName();
    new MutationObserver(fixName).observe(document.body, { childList: true, subtree: true, characterData: true });
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

  // Search island (search.js): loaded once, on first use by the Ctrl+K dialog or the "Ask" box.
  var searchScript;
  function withSearch(cb) {
    if (window.siteSearch) return cb();
    if (!searchScript) { searchScript = document.createElement("script"); searchScript.src = "/assets/islands/search.js"; document.head.appendChild(searchScript); }
    searchScript.addEventListener("load", cb);
  }

  // "Ask about my work": example chips reveal their pre-written answer; typed questions search the site, results right under the box.
  var chips = $$("[data-answer]"), askInput = $("#ask-input"), askList = $("#ask-results"), askStatus = $("#ask-status");
  function clearAsk() { if (askList) { askList.innerHTML = ""; askStatus.textContent = ""; } }
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (c) {
        var on = c === chip && c.getAttribute("aria-expanded") !== "true";
        c.setAttribute("aria-expanded", on);
        document.getElementById(c.dataset.answer).hidden = !on;
      });
      clearAsk();
    });
  });
  function ask() {
    chips.forEach(function (c) { c.setAttribute("aria-expanded", false); document.getElementById(c.dataset.answer).hidden = true; });
    if (!askInput.value.trim()) return clearAsk();
    withSearch(function () {
      window.siteSearch.load().then(function () {
        var q = askInput.value.trim(), hits = q ? window.siteSearch.find(q, 5) : [];
        askList.innerHTML = "";
        hits.forEach(function (it) {
          var li = document.createElement("li"), a = document.createElement("a");
          a.href = it.u;
          a.innerHTML = '<span class="sk"></span><span class="st"></span><span class="sd"></span>';
          a.children[0].textContent = it.k; a.children[1].textContent = it.t; a.children[2].textContent = it.d || "";
          li.appendChild(a); askList.appendChild(li);
        });
        askStatus.textContent = !q ? "" : hits.length ? hits.length + (hits.length === 1 ? " page matches" : " pages match") + " your question:" : "Nothing matches those words yet. Try other words, or one of the example questions.";
      }, function () { askStatus.textContent = "Search is unavailable right now. Try one of the example questions."; });
    });
  }
  var askForm = $("#ask-form");
  if (askForm && askList) {
    askForm.addEventListener("submit", function (e) { e.preventDefault(); ask(); });
    askInput.addEventListener("input", ask);
  }

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

  // Sandboxes are islands: each one's code loads when it comes into view (or its button is pressed), never before.
  // On the home page they sit in closed rows, so they open when the visitor expands the row.
  function openIsland(box) {
    if (box.dataset.opened) return;
    box.dataset.opened = "1";
    var name = box.dataset.island, btn = $("[data-island-load]", box);
    if (btn) btn.disabled = true;
    var run = function () { window.islands[name](box); };
    if (window.islands && window.islands[name]) return run();
    var sc = document.createElement("script");
    sc.src = "/assets/islands/" + name + ".js";
    sc.onload = run;
    document.head.appendChild(sc);
  }
  var islandBoxes = $$("[data-island]");
  islandBoxes.forEach(function (box) {
    var btn = $("[data-island-load]", box);
    if (btn) btn.addEventListener("click", function () { openIsland(box); });
  });
  if (window.IntersectionObserver) {
    var islandWatch = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { islandWatch.unobserve(e.target); openIsland(e.target); } });
    }, { rootMargin: "200px 0px" });
    islandBoxes.forEach(function (box) { islandWatch.observe(box); });
  }

  // Scrollable tables in posts: make them reachable with the Tab key so keyboard users can scroll them.
  // shortcut: checked once at load, not on resize; fine because tables only overflow on narrow screens, which rarely change width.
  $$(".prose table").forEach(function (t) { if (t.scrollWidth > t.clientWidth) t.tabIndex = 0; });

  // Ctrl+K (or the search button) opens the search dialog.
  function openSearch() { withSearch(function () { window.siteSearch.open(); }); }
  var searchBtn = $(".search-btn");
  if (searchBtn) searchBtn.addEventListener("click", openSearch);
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
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
