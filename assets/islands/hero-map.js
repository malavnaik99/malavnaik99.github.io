// Hero map: the background map behind the home page hero, and "Explore the live map" (a full-screen street map).
//
// What it does
//   - Projects latitude/longitude onto the hero canvas. assets/islands/sky.js draws the Dublinbikes stations through the
//     same projection (map.xy), so stations, river and outlines always line up.
//   - Draws the landmarks as thin, faint lines: Dublin Bay coastline, River Liffey, Grand Canal, Royal Canal and the
//     Phoenix Park boundary, and places the five place-name labels (their words are in index.md / _includes/sky-bar.html,
//     so the Gujarati button's Google Translate copy translates them).
//   - Resting hero: fades the map out under the headline column, the moderation card and the text strips, so no station
//     sits behind text.
//   - Explore mode ("Explore the live map", or the "Live map" link, address malavnaik.com/#live-map): a full-screen <dialog>
//     with the same OpenStreetMap street map as the Dublin bikes project page (islands.stationmap in sky.js, Leaflet,
//     built on first open). Esc or "Close map" closes it and puts focus back where it was; the rest of the page is
//     unreachable while it is open. Its map images come from OpenStreetMap's servers, only once a visitor opens it.
//   - Works without station data: the outlines and labels still draw and "Live data unavailable" shows in explore mode.
//
// Where the outline data came from
//   assets/data/dublin-outlines.json, made once by `python3 scripts/make_sky.py --outlines` from OpenStreetMap
//   (© OpenStreetMap contributors, ODbL) via the Overpass API, simplified to 20 m and checked against the station
//   positions. It is a static file in this repo: no map library and no map requests while the page runs.
//   Label positions are in the same file (LABELS in make_sky.py).
//
// Loaded by assets/site.js after the page has painted; sky.js then adds the stations through map.layer().
(function () {
  // The area to fit on screen: wide screens also show Dublin Bay and the edge of Phoenix Park; tall screens fit the stations.
  var WIDE = [53.322, -6.330, 53.360, -6.180], TALL = [53.330, -6.311, 53.360, -6.230]; // south, west, north, east
  var PAD = 0.05, CLEAR = 14, FEATHER = 44; // fully clear this many px around text, then fade the map back over FEATHER px
  var STYLE = { coast: [1, 1], liffey: [2, 1.4], grand_canal: [1.4, 1], royal_canal: [1.4, 1], phoenix_park: [1, 1] }; // [line width, strength]

  window.islands = window.islands || {};
  window.islands.heroMap = function (bar) {
    var hero = bar.closest(".hero"), sky = hero.querySelector(".sky"), canvas = sky.querySelector("[data-sky-map]");
    var ctx = canvas.getContext("2d"), places = [].slice.call(sky.querySelectorAll("[data-place]"));
    var dialog = hero.querySelector(".sky-explore"), openers = [].slice.call(hero.querySelectorAll("[data-explore-open]"));
    var covers = [].slice.call(hero.querySelectorAll(".sky-head, .hero-copy, .hero-demo, .sky-bar"));
    var data = { lines: {}, labels: {} }, layer = null, dpr = 1, xy = null, holes = [], ink = "";
    var map = {
      xy: function (lat, lon) { return xy(lat, lon); },
      dpr: function () { return dpr; },
      layer: function (fn) { layer = fn; render(); },
      render: render,
      // "live", "saved snapshot" or null (no station data): anything but live shows the note in explore mode.
      status: function (label) { dialog.querySelector("[data-sky-nolive]").hidden = label === "live"; }
    };

    function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }
    function fit() {
      var r = canvas.getBoundingClientRect();
      dpr = 1; // a faint background: 1x is enough, and a third of the pixel work of a sharp phone screen
      var w = Math.round(r.width * dpr), h = Math.round(r.height * dpr);
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; } // resizing a canvas is costly: only when needed
      var W = canvas.width, H = canvas.height, b = W >= H ? WIDE : TALL;
      var k = Math.cos((b[0] + b[2]) / 2 * Math.PI / 180), dx = (b[3] - b[1]) * k, dy = b[2] - b[0];
      var s = Math.min(W * (1 - 2 * PAD) / dx, H * (1 - 2 * PAD) / dy), ox = (W - dx * s) / 2, oy = (H - dy * s) / 2;
      xy = function (lat, lon) { return [ox + (lon - b[1]) * k * s, oy + (b[2] - lat) * s]; };
    }
    function render() {
      if (!canvas.width || !xy) return;
      var W = canvas.width, H = canvas.height;
      ctx.clearRect(0, 0, W, H);
      ctx.globalCompositeOperation = "source-over"; ctx.lineJoin = ctx.lineCap = "round"; ctx.strokeStyle = ink;
      Object.keys(STYLE).forEach(function (name) {
        ctx.lineWidth = STYLE[name][0] * dpr; ctx.globalAlpha = STYLE[name][1] * 0.28;
        (data.lines[name] || []).forEach(function (line) {
          ctx.beginPath();
          line.forEach(function (p, i) { var q = xy(p[0], p[1]); if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); });
          ctx.stroke();
        });
      });
      ctx.globalAlpha = 1;
      if (layer) layer(ctx);
    }
    // The fade under the text is a CSS mask: a small stencil made once per resize (not on every replay frame). White = map
    // shows, transparent = map hidden; each text box is cut out with a soft edge (rings of rising strength).
    function maskUnderText() {
      var S = 8, W = Math.ceil(canvas.width / dpr / S), H = Math.ceil(canvas.height / dpr / S); // 1 stencil pixel = 8 CSS px
      if (!holes.length || !W || !H) { canvas.style.webkitMaskImage = canvas.style.maskImage = ""; return; }
      var m = document.createElement("canvas"), g = m.getContext("2d");
      m.width = W; m.height = H; g.fillStyle = "#fff"; g.fillRect(0, 0, W, H);
      g.globalCompositeOperation = "destination-out";
      holes.forEach(function (r) {
        for (var i = 0, n = 6; i <= n; i++) {
          var e = (CLEAR + FEATHER * (1 - i / n)) / S, x = r.x / dpr / S - e, y = r.y / dpr / S - e, w = r.w / dpr / S + 2 * e, h = r.h / dpr / S + 2 * e;
          g.globalAlpha = i === n ? 1 : 0.28;
          g.beginPath(); if (g.roundRect) g.roundRect(x, y, w, h, e); else g.rect(x, y, w, h); g.fill();
        }
      });
      var url = "url(" + m.toDataURL() + ")";
      canvas.style.webkitMaskImage = canvas.style.maskImage = url;
      canvas.style.webkitMaskSize = canvas.style.maskSize = "100% 100%";
    }
    // Text boxes in canvas pixels (resting hero only).
    function clearAreas() {
      var c = canvas.getBoundingClientRect();
      return covers.map(function (el) {
        var r = el.getBoundingClientRect();
        return r.width ? { x: (r.left - c.left) * dpr, y: (r.top - c.top) * dpr, w: r.width * dpr, h: r.height * dpr } : null;
      }).filter(Boolean);
    }
    function placeLabels() {
      var W = canvas.width / dpr, H = canvas.height / dpr, m = CLEAR + FEATHER / 2;
      places.forEach(function (el) { el.hidden = !data.labels[el.dataset.place]; });
      var size = places.map(function (el) { return [el.offsetWidth / 2, el.offsetHeight / 2]; }); // read all sizes first, then move: one layout, not five
      places.forEach(function (el, i) {
        var at = data.labels[el.dataset.place];
        if (!at) return;
        var q = xy(at[0], at[1]), x = q[0] / dpr, y = q[1] / dpr, w = size[i][0], h = size[i][1];
        var under = holes.some(function (r) { // a label never sits on or beside text
          return x + w > r.x / dpr - m && x - w < (r.x + r.w) / dpr + m && y + h > r.y / dpr - m && y - h < (r.y + r.h) / dpr + m;
        });
        el.hidden = under || x - w < 4 || x + w > W - 4 || y - h < 4 || y + h > H - 4;
        el.style.left = x + "px"; el.style.top = y + "px";
      });
    }
    // Size, text boxes and labels change only on resize or theme; the replay redraws many times a second without them.
    function redraw() { queued = 0; fit(); ink = css("--muted"); holes = clearAreas(); maskUnderText(); placeLabels(); render(); }
    var queued = 0;
    function later() { if (!queued) queued = requestAnimationFrame(redraw); } // many triggers in one frame: one redraw

    // Explore mode: the street map is built the first time the dialog opens (sky.js, which holds it, may still be loading).
    var slot = dialog.querySelector("[data-sky-slot]"), opener = null, built = false;
    function build() {
      if (built) return;
      if (!window.islands.stationmap) return setTimeout(build, 100);
      built = true;
      slot.dataset.src = bar.dataset.src;
      if (bar.dataset.live) slot.dataset.live = bar.dataset.live;
      window.islands.stationmap(slot);
    }
    openers.forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault(); // the "Live map" link: open here rather than jump to #live-map
        opener = el;
        hero.classList.add("is-exploring");
        dialog.showModal(); // modal: Esc closes it, focus stays inside, the rest of the page is inert
        build();
      });
    });
    dialog.querySelector("[data-explore-close]").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("close", function () {
      hero.classList.remove("is-exploring");
      if (location.hash === "#live-map") history.replaceState(history.state, "", location.pathname + location.search);
      (opener || openers[0]).focus();
    });

    if (window.ResizeObserver) { var ro = new ResizeObserver(later); [canvas].concat(covers).forEach(function (el) { ro.observe(el); }); } // text boxes too: fonts and the demo change their size
    else window.addEventListener("resize", later);
    new MutationObserver(later).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    later();
    fetch(bar.dataset.outlines).then(function (r) { return r.json(); }).then(function (j) {
      data = j; hero.classList.add("has-sky"); later();
    }).catch(function () {}); // no outlines: the stations still draw on their own
    return map;
  };
})();
