// DSA search sandbox: loaded only when a visitor opens it. Shows precomputed keyword vs vector results for the 25 test questions.
(function () {
  window.islands = window.islands || {};
  window.islands.dsa = function (box) {
    box.innerHTML = '<p class="small muted">Loading saved results…</p>';
    fetch(box.dataset.src).then(function (r) { return r.json(); }).then(function (d) {
      box.innerHTML = '<label class="pick"><span class="small muted">Pick a test question</span><select></select></label>' +
        '<p class="small expected"></p><div class="compare"><section><h4>Keyword (BM25)</h4><ol data-m="keyword"></ol></section>' +
        '<section><h4>Vector (all-MiniLM-L6-v2)</h4><ol data-m="vector"></ol></section></div>';
      var sel = box.querySelector("select");
      d.examples.forEach(function (ex, i) {
        var o = document.createElement("option"); o.value = i; o.textContent = ex.q; sel.appendChild(o);
      });
      function show(i) {
        var ex = d.examples[i];
        box.querySelector(".expected").textContent = "Answered by Article " + ex.expected.join(" or ") + ".";
        ["keyword", "vector"].forEach(function (m) {
          var ol = box.querySelector('[data-m="' + m + '"]'); ol.innerHTML = "";
          var hit = ex[m].some(function (a) { return ex.expected.indexOf(a.article) > -1; });
          ex[m].forEach(function (a) {
            var li = document.createElement("li"), ok = ex.expected.indexOf(a.article) > -1;
            if (ok) li.className = "hit";
            li.innerHTML = '<a class="art"></a><span class="ok mono"></span><p class="small muted"></p>';
            li.querySelector(".art").textContent = "Article " + a.article + ": " + a.title;
            li.querySelector(".art").href = a.url;
            li.querySelector(".ok").textContent = ok ? "right article" : "";
            li.querySelector("p").textContent = a.paragraph;
            ol.appendChild(li);
          });
          ol.parentNode.querySelector("h4").setAttribute("data-verdict", hit ? "found it in the top 3" : "missed it");
        });
      }
      sel.addEventListener("change", function () { show(+sel.value); });
      show(0);
    }).catch(function () { box.innerHTML = '<p class="small muted">The saved results could not be loaded. Please try again later.</p>'; });
  };
})();
