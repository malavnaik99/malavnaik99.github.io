// Hero sky: every Dublinbikes station as a light at its real position (brighter = more bikes free, amber ring = empty),
// with the River Liffey as the only landmark. Loaded by site.js only after the page has painted.
// Data: /assets/data/sky.json (saved snapshot + river) or, when switched on in _data/sky_live.json, the pipeline's
// "latest" file if it is under two hours old. The text summary under the map is the same information in words.
// The same file holds the street map on the Dublin bikes project page (islands.stationmap), which shares the data loader.
(function () {
  var MAX_AGE = 2 * 3600 * 1000, STEP_MS = 220;
  var MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], DAY = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  function valid(d) {
    return d && d.hours && d.stations && d.bikes && d.hours.length && d.bikes.length === d.stations.length;
  }
  // The pipeline's file should already leave these out; the page makes sure.
  function clean(d) {
    var keep = d.stations.map(function (s, i) { return s[3] > 0 && String(s[0]).toLowerCase() !== "station118" ? i : -1; }).filter(function (i) { return i >= 0; });
    return { hours: d.hours, generated_utc: d.generated_utc, stations: keep.map(function (i) { return d.stations[i]; }), bikes: keep.map(function (i) { return d.bikes[i]; }) };
  }
  function when(hours, i) { // "2026-10-25T01:00" -> "Sun 25 Oct, 01:00"; the repeated hour when clocks go back is marked
    var m = /^(\d{4})-(\d\d)-(\d\d)T(\d\d:\d\d)/.exec(hours[i]) || [];
    var day = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3])).getUTCDay();
    return DAY[day] + " " + (+m[3]) + " " + MON[+m[2] - 1] + ", " + m[4] + (i > 0 && hours[i] === hours[i - 1] ? " (again: clocks went back)" : "");
  }
  var num = function (n) { return n.toLocaleString("en-IE"); };
  // The saved snapshot (+ river), or the pipeline's live file when it is under two hours old.
  function load(src, live) {
    var river = [];
    return fetch(src).then(function (r) { return r.json(); }).then(function (j) {
      river = j.river || [];
      if (!live) return { data: j.snapshot, label: "saved snapshot" };
      var ctl = new AbortController();
      setTimeout(function () { ctl.abort(); }, 4000);
      return fetch(live, { signal: ctl.signal }).then(function (r) { return r.ok ? r.json() : null; }).then(function (l) {
        return valid(l) && Date.now() - Date.parse(l.generated_utc) < MAX_AGE ? { data: l, label: "live" } : { data: j.snapshot, label: "saved snapshot" };
      }).catch(function () { return { data: j.snapshot, label: "saved snapshot" }; });
    }).then(function (r) { return { d: clean(r.data), label: r.label, river: river }; });
  }

  window.islands = window.islands || {};
  window.islands.sky = function (bar) {
    var hero = bar.closest(".hero"), canvas = hero.querySelector("[data-sky-map]"), tip = hero.querySelector(".sky-tip");
    var text = bar.querySelector("[data-sky-text]"), range = bar.querySelector("[data-sky-hour]"), play = bar.querySelector("[data-sky-play]"), time = bar.querySelector("[data-sky-time]");
    var still = matchMedia("(prefers-reduced-motion: reduce)").matches;
    var ctx = canvas.getContext("2d"), d, river = [], label = "saved snapshot", hour = 0, timer = null, pts = [], dpr = 1;
    var playLabel = play.textContent;

    load(bar.dataset.src, bar.dataset.live).then(function (res) {
      d = res.d; river = res.river; label = res.label;
      hero.classList.add("has-sky");
      if (label === "live") bar.classList.add("is-live");
      range.max = d.hours.length - 1; range.disabled = false;
      fit(); show(still ? d.hours.length - 1 : 0);
      if (!still) toggle(); // plays the last hours once, then stops on the newest; never starts by itself under reduced motion
    }).catch(function () {}); // the sky stays dark and the summary text stays as it was built

    function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }
    function fit() {
      var r = hero.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(r.width * dpr); canvas.height = Math.round(r.height * dpr);
      var la = d.stations.map(function (s) { return s[1]; }), lo = d.stations.map(function (s) { return s[2]; });
      var minLa = Math.min.apply(0, la), maxLa = Math.max.apply(0, la), minLo = Math.min.apply(0, lo), maxLo = Math.max.apply(0, lo);
      var k = Math.cos((minLa + maxLa) / 2 * Math.PI / 180), pad = 0.08;
      var W = canvas.width, H = canvas.height, dx = (maxLo - minLo) * k, dy = maxLa - minLa;
      var s = Math.min(W * (1 - 2 * pad) / dx, H * (1 - 2 * pad) / dy);
      var ox = (W - dx * s) / 2, oy = (H - dy * s) / 2;
      fit.xy = function (lat, lon) { return [ox + (lon - minLo) * k * s, oy + (maxLa - lat) * s]; };
    }
    function draw() {
      var W = canvas.width, H = canvas.height, ink = css("--text"), empty = css("--dg-warn");
      ctx.clearRect(0, 0, W, H);
      ctx.globalAlpha = 1; ctx.lineWidth = 2 * dpr; ctx.strokeStyle = css("--line"); ctx.lineJoin = "round";
      river.forEach(function (line) {
        ctx.beginPath();
        line.forEach(function (p, i) { var q = fit.xy(p[0], p[1]); if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); });
        ctx.stroke();
      });
      pts = [];
      d.stations.forEach(function (st, i) {
        var b = d.bikes[i][hour], q = fit.xy(st[1], st[2]);
        pts.push({ x: q[0], y: q[1], st: st, b: b });
        if (b === null || b === undefined) return;
        var f = Math.min(1, b / st[3]);
        ctx.globalAlpha = 0.1 + 0.6 * f; ctx.fillStyle = ink; // capped so text drawn over the map stays crisp
        ctx.beginPath(); ctx.arc(q[0], q[1], (1.4 + 1.8 * f) * dpr, 0, 7); ctx.fill();
        if (b === 0) { ctx.globalAlpha = 0.9; ctx.strokeStyle = empty; ctx.lineWidth = 1.5 * dpr; ctx.beginPath(); ctx.arc(q[0], q[1], 4.5 * dpr, 0, 7); ctx.stroke(); }
      });
      ctx.globalAlpha = 1;
    }
    function summary(h) {
      var total = 0, n = 0, empty = 0;
      d.bikes.forEach(function (row) { var b = row[h]; if (b === null || b === undefined) return; total += b; n++; if (b === 0) empty++; });
      return "Dublinbikes, " + when(d.hours, h) + " (" + label + "): " + num(total) + " bikes at " + n + " stations, " + empty + " empty.";
    }
    function show(h) {
      hour = h; range.value = h; draw();
      var s = summary(h);
      text.textContent = s; range.setAttribute("aria-valuetext", s); time.textContent = when(d.hours, h);
    }
    function stop() { clearInterval(timer); timer = null; play.textContent = playLabel; }
    function toggle() {
      if (timer) return stop();
      if (hour >= d.hours.length - 1) show(0);
      play.textContent = "Pause";
      timer = setInterval(function () { if (hour >= d.hours.length - 1) return stop(); show(hour + 1); }, STEP_MS);
    }
    play.addEventListener("click", toggle);
    range.addEventListener("input", function () { stop(); show(+range.value); });

    // Pointing at a station (or tapping it) shows its name and "X of Y bikes".
    function point(e) {
      if (!d) return;
      var r = canvas.getBoundingClientRect(), x = (e.clientX - r.left) * dpr, y = (e.clientY - r.top) * dpr, best = null, bd = 14 * dpr;
      pts.forEach(function (p) { var dd = Math.hypot(p.x - x, p.y - y); if (dd < bd) { bd = dd; best = p; } });
      if (!best || best.b === null || best.b === undefined) { tip.hidden = true; return; }
      tip.textContent = best.st[0] + ": " + best.b + " of " + best.st[3] + " bikes";
      tip.style.left = best.x / dpr + "px"; tip.style.top = best.y / dpr + "px"; tip.hidden = false;
    }
    canvas.addEventListener("pointermove", point);
    canvas.addEventListener("pointerdown", point);
    canvas.addEventListener("pointerleave", function () { tip.hidden = true; });
    if (window.ResizeObserver) new ResizeObserver(function () { if (d) { fit(); draw(); } }).observe(hero);
    new MutationObserver(function () { if (d) draw(); }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  };

  // Street map (Dublin bikes project page): every station on OpenStreetMap, at the newest hour of data.
  // Leaflet (pinned copy in assets/vendor) and the map pictures load only when the visitor reaches the map.
  var VENDOR = "/assets/vendor/leaflet-1.9.4/";
  function script(src) {
    return new Promise(function (ok, fail) { var s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = fail; document.head.appendChild(s); });
  }
  window.islands.stationmap = function (box) {
    var link = document.createElement("link"); link.rel = "stylesheet"; link.href = VENDOR + "leaflet.css"; document.head.appendChild(link);
    box.innerHTML = '<p class="small muted">Loading the map…</p>';
    Promise.all([load(box.dataset.src, box.dataset.live), window.L ? null : script(VENDOR + "leaflet.js")]).then(function (r) {
      var d = r[0].d, h = d.hours.length - 1, ink = getComputedStyle(document.documentElement);
      var accent = ink.getPropertyValue("--accent").trim(), warn = ink.getPropertyValue("--dg-warn").trim();
      box.innerHTML = '<div class="station-map-view" role="region" aria-label="Street map of Dublinbikes stations"></div><p class="small station-map-sum"></p>' +
        '<details class="station-list"><summary>All stations as a list</summary><table><thead><tr><th scope="col">Station</th><th scope="col">Bikes</th><th scope="col">Docks</th></tr></thead><tbody></tbody></table></details>';
      var map = L.map(box.firstChild, { scrollWheelZoom: false }), pts = [], total = 0, empty = 0, rows = [];
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
      d.stations.forEach(function (s, i) {
        var b = d.bikes[i][h];
        if (b === null || b === undefined) return;
        var f = Math.min(1, b / s[3]), tip = document.createElement("span"); // built with textContent: names come from the data, never read as HTML
        tip.textContent = s[0] + ": " + b + " of " + s[3] + " bikes";
        L.circleMarker([s[1], s[2]], b === 0 ? { radius: 7, color: warn, weight: 2.5, fillOpacity: 0 } : { radius: 4 + 5 * f, color: accent, weight: 1, fillColor: accent, fillOpacity: 0.25 + 0.6 * f })
          .bindTooltip(tip).bindPopup(tip.cloneNode(true)).addTo(map);
        pts.push([s[1], s[2]]); total += b; if (b === 0) empty++; rows.push([s[0], b, s[3]]);
      });
      map.fitBounds(pts, { padding: [16, 16] });
      box.querySelector(".station-map-sum").textContent = "Dublinbikes, " + when(d.hours, h) + " (" + r[0].label + "): " + num(total) + " bikes at " + pts.length +
        " stations, " + empty + " empty. Bigger, more solid circles have more bikes free; an amber ring means empty. Tap or point at a station for its numbers.";
      var tb = box.querySelector("tbody");
      rows.sort(function (a, b) { return a[0].localeCompare(b[0]); }).forEach(function (row) {
        var tr = document.createElement("tr");
        row.forEach(function (v) { var td = document.createElement("td"); td.textContent = v; tr.appendChild(td); });
        tb.appendChild(tr);
      });
    }).catch(function () { box.innerHTML = '<p class="small muted">The map could not be loaded. Please try again later.</p>'; });
  };
})();
