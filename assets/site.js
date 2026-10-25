// Theme toggle, mobile menu, copy buttons, blog filter. Vanilla JS; the site works without it.
(function () {
  var root = document.documentElement;

  var themeBtn = document.querySelector(".theme-btn");
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("theme", root.dataset.theme); } catch (e) {}
  });

  var menuBtn = document.querySelector(".menu-btn"), nav = document.getElementById("site-nav");
  if (menuBtn && nav) menuBtn.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", open);
  });

  function copyButton(label, getText) {
    var b = document.createElement("button");
    b.type = "button"; b.className = "copy-btn"; b.textContent = label;
    b.addEventListener("click", function () {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(getText()).then(function () {
        b.textContent = "Copied"; setTimeout(function () { b.textContent = label; }, 1500);
      });
    });
    return b;
  }
  document.querySelectorAll(".prose pre").forEach(function (pre) {
    pre.appendChild(copyButton("Copy", function () { return pre.querySelector("code") ? pre.querySelector("code").innerText : pre.innerText; }));
  });

  var shareCopy = document.querySelector("[data-copy-link]");
  if (shareCopy) shareCopy.replaceWith(Object.assign(copyButton("Copy link", function () { return location.href.split("#")[0]; }), { className: "btn small" }));

  // Blog index: filter by series.
  var filters = document.querySelectorAll("[data-filter]");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var s = btn.dataset.filter;
      filters.forEach(function (b) { b.setAttribute("aria-pressed", b === btn); });
      document.querySelectorAll("[data-series]").forEach(function (card) {
        card.hidden = s !== "all" && card.dataset.series !== s;
      });
    });
  });
})();
