// Moderation threshold sandbox: loaded only when a visitor opens it. Reads the precomputed sweep (real test-set results).
(function () {
  var pct = function (x) { return (x * 100).toFixed(1) + "%"; };
  var nice = function (g) { return g.replace(/_/g, " ").replace("homosexual gay or lesbian", "gay or lesbian").replace("psychiatric or mental illness", "psychiatric or mental illness"); };
  window.islands = window.islands || {};
  window.islands.moderation = function (box) {
    box.innerHTML = '<p class="small muted">Loading saved results…</p>';
    fetch(box.dataset.src).then(function (r) { return r.json(); }).then(function (d) {
      var s = d.sweep;
      box.innerHTML =
        '<label class="slider"><span>Flag a comment when its toxicity score is at least <b class="mono" data-t></b></span>' +
        '<input type="range" min="0" max="' + (s.length - 1) + '" step="1"></label>' +
        '<p class="small muted presets">Jump to the two saved policies: <button type="button" class="btn small" data-go="0.22">send to review (0.22)</button> <button type="button" class="btn small" data-go="0.82">auto-action (0.82)</button></p>' +
        '<div class="meters">' +
        '<div class="meter"><span class="k">Precision</span><span class="v mono" data-v="precision"></span><span class="bar"><i data-b="precision"></i></span><span class="small muted">of flagged comments that really are toxic</span></div>' +
        '<div class="meter"><span class="k">Recall</span><span class="v mono" data-v="recall"></span><span class="bar"><i data-b="recall"></i></span><span class="small muted">of all toxic comments that get flagged</span></div>' +
        '<div class="meter"><span class="k">Flagged</span><span class="v mono" data-v="flagged"></span><span class="bar"><i data-b="flagged"></i></span><span class="small muted">of all comments: <b data-per1000></b> per 1,000 go to human review or automatic action</span></div>' +
        '</div>' +
        '<h4 class="groups-title">Harmless comments wrongly flagged, by group mentioned</h4>' +
        '<p class="small muted">Across all identity-labelled harmless comments: <b class="mono" data-all></b> (the thin line on each bar). Groups with at least 200 harmless test comments.</p>' +
        '<ul class="groups"></ul>';
      var input = box.querySelector("input"), ul = box.querySelector(".groups");
      d.groups.forEach(function (g) {
        var li = document.createElement("li");
        li.innerHTML = '<span class="g"></span><span class="bar"><i></i><em class="avg"></em></span><span class="v mono"></span>';
        li.firstChild.textContent = nice(g); li.dataset.g = g; ul.appendChild(li);
      });
      function show(i) {
        var r = s[i], max = 0;
        box.querySelector("[data-t]").textContent = r.t.toFixed(2);
        input.setAttribute("aria-valuetext", "threshold " + r.t.toFixed(2));
        ["precision", "recall", "flagged"].forEach(function (k) {
          box.querySelector('[data-v="' + k + '"]').textContent = pct(r[k]);
          box.querySelector('[data-b="' + k + '"]').style.width = (r[k] * 100) + "%";
        });
        box.querySelector("[data-per1000]").textContent = Math.round(r.flagged * 1000);
        box.querySelector("[data-all]").textContent = pct(r.fpr_all);
        d.groups.forEach(function (g) { max = Math.max(max, r.fpr[g]); });
        max = Math.max(max, r.fpr_all, 0.01);
        Array.prototype.forEach.call(ul.children, function (li) {
          var v = r.fpr[li.dataset.g];
          li.querySelector("i").style.width = (v / max * 100) + "%";
          li.querySelector(".avg").style.left = (r.fpr_all / max * 100) + "%";
          li.querySelector(".v").textContent = pct(v);
        });
      }
      function goTo(t) { var i = s.findIndex(function (r) { return Math.abs(r.t - t) < 0.001; }); input.value = i; show(i); }
      input.addEventListener("input", function () { show(+input.value); });
      Array.prototype.forEach.call(box.querySelectorAll("[data-go]"), function (b) { b.addEventListener("click", function () { goTo(+b.dataset.go); }); });
      goTo(0.22);
    }).catch(function () { box.innerHTML = '<p class="small muted">The saved results could not be loaded. Please try again later.</p>'; });
  };
})();
