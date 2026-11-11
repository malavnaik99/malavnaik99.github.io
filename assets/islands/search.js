// Site search island: loaded on first use, by the Ctrl+K dialog or the home page "Ask about my work" box.
// Searches /search.json, built by Jekyll from every post, project and page.
(function () {
  var items = null, loading = null, dlg, input, list, active = 0, shown = [];
  // Words in almost every question ("how do you…") that would match everything; ignored unless they are all there is.
  var STOP = " a an and are about can could did do does for from has have how i in is it me my of on or so tell the this to was what when where which who why with would you your ";

  function load() {
    return loading || (loading = fetch("/search.json").then(function (r) { return r.json(); }).then(function (d) { items = d; return d; }, function (e) { loading = null; throw e; }));
  }

  // Rank by how many query words each item contains; a word in the title counts double. Empty query: everything, in index order.
  function find(q, max) {
    if (!items) return [];
    var words = q.toLowerCase().replace(/[^\w\s&+#.-]/g, " ").split(/\s+/).filter(Boolean);
    var useful = words.filter(function (w) { return STOP.indexOf(" " + w + " ") < 0; });
    if (useful.length) words = useful;
    if (!words.length) return items.slice(0, max);
    return items.map(function (it) {
      var t = it.t.toLowerCase(), hay = (t + " " + (it.d || "") + " " + it.k + " " + (it.x || "")).toLowerCase(), s = 0;
      words.forEach(function (w) { if (hay.indexOf(w) > -1) s += t.indexOf(w) > -1 ? 2 : 1; });
      return { it: it, s: s };
    }).filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s; }) // stable sort: ties keep index order (newest posts first)
      .slice(0, max).map(function (r) { return r.it; });
  }

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
      // A search field's own Esc only clears the text; close the dialog in one press instead.
      if (e.key === "Escape") { e.preventDefault(); dlg.close(); }
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }
  function render() {
    shown = find(input.value, 12);
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
  function open() {
    if (!dlg) build();
    dlg.showModal(); input.value = ""; render(); input.focus();
    load().then(render, function () { list.innerHTML = '<li class="search-empty">Search is unavailable right now.</li>'; });
  }

  window.siteSearch = { open: open, load: load, find: find };
})();
