// Ctrl+K search island: loaded only when a visitor opens search. Searches /search.json, built by Jekyll.
(function () {
  var items = null, dlg, input, list, active = 0, shown = [];
  function build() {
    dlg = document.createElement("dialog");
    dlg.className = "search-dialog";
    dlg.setAttribute("aria-label", "Search the site");
    dlg.innerHTML = '<form method="dialog"><label class="sr-only" for="search-q">Search posts, projects and pages</label>' +
      '<input id="search-q" type="search" placeholder="Search posts, projects and pages" autocomplete="off" role="combobox" aria-expanded="true" aria-controls="search-results">' +
      '<ul id="search-results" role="listbox"></ul><p class="search-hint">Enter to open · Esc to close</p></form>';
    document.body.appendChild(dlg);
    input = dlg.querySelector("input"); list = dlg.querySelector("ul");
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); active = (active + (e.key === "ArrowDown" ? 1 : -1) + shown.length) % (shown.length || 1); mark(); }
      if (e.key === "Enter" && shown[active]) { e.preventDefault(); location.href = shown[active].u; }
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }
  function render() {
    var words = input.value.toLowerCase().split(/\s+/).filter(Boolean);
    shown = !items ? [] : items.filter(function (it) {
      var hay = (it.t + " " + (it.d || "") + " " + it.k).toLowerCase();
      return words.every(function (w) { return hay.indexOf(w) > -1; });
    }).slice(0, 12);
    active = 0;
    list.innerHTML = "";
    shown.forEach(function (it, i) {
      var li = document.createElement("li"), a = document.createElement("a");
      li.setAttribute("role", "option"); li.id = "sr-" + i;
      a.href = it.u;
      a.innerHTML = '<span class="sk"></span><span class="st"></span>';
      a.firstChild.textContent = it.k; a.lastChild.textContent = it.t;
      li.appendChild(a); list.appendChild(li);
    });
    if (!shown.length) list.innerHTML = '<li class="search-empty">' + (items ? "No matches." : "Loading…") + "</li>";
    mark();
  }
  function mark() {
    Array.prototype.forEach.call(list.children, function (li, i) { li.setAttribute("aria-selected", i === active); });
    input.setAttribute("aria-activedescendant", shown.length ? "sr-" + active : "");
  }
  window.openSearch = function () {
    if (!dlg) build();
    dlg.showModal(); input.value = ""; render(); input.focus();
    if (!items) fetch("/search.json").then(function (r) { return r.json(); }).then(function (d) { items = d; render(); })
      .catch(function () { list.innerHTML = '<li class="search-empty">Search is unavailable right now.</li>'; });
  };
})();
