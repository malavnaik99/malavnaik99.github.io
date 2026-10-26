// SQL console island: loads DuckDB-WASM (pinned, from jsDelivr) only when a visitor opens it. DuckDB runs in a Web Worker.
(function () {
  var DUCKDB = "https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@1.29.0/+esm";
  var TABLES = ["fct_station_hour", "dim_station", "dim_hour"];
  window.islands = window.islands || {};
  window.islands.sql = function (box) {
    var card = box.closest(".sandbox-card");
    box.innerHTML = '<label class="sr-only" for="sql-in">SQL query</label><textarea id="sql-in" class="sql-in" rows="5" spellcheck="false"></textarea>' +
      '<p class="actions"><button class="btn btn-accent" type="button" data-run disabled>Run</button> <span class="small muted" data-status role="status">Loading DuckDB…</span></p>' +
      '<div class="sql-out" data-out></div>';
    var input = box.querySelector("textarea"), run = box.querySelector("[data-run]"), status = box.querySelector("[data-status]"), out = box.querySelector("[data-out]");
    var conn = null, pending = null;
    function exampleSql(name) { return card.querySelector('[data-sql-text="' + name + '"]').textContent; }
    input.value = exampleSql("empty");
    function fmt(v, f) {
      if (v === null || v === undefined) return "";
      if (typeof v === "bigint") return v.toString();
      if (f.type && f.type.typeId === 10) return new Date(Number(v)).toISOString().replace("T", " ").slice(0, 16);
      if (typeof v === "number") return Math.round(v * 1000) / 1000;
      return String(v);
    }
    function execute() {
      var sql = input.value.trim();
      if (!/^(select|with|describe|summarize|show|explain)\b/i.test(sql) || /;\s*\S/.test(sql)) {
        status.textContent = "This console is read-only: one SELECT (or WITH / DESCRIBE / SUMMARIZE) at a time.";
        return;
      }
      if (!conn) { pending = sql; return; }
      status.textContent = "Running…"; var t0 = performance.now();
      conn.query(sql).then(function (res) {
        var fields = res.schema.fields, rows = res.toArray().slice(0, 200);
        var html = '<table><thead><tr>' + fields.map(function (f) { return "<th></th>"; }).join("") + "</tr></thead><tbody></tbody></table>";
        out.innerHTML = html;
        var ths = out.querySelectorAll("th"); fields.forEach(function (f, i) { ths[i].textContent = f.name; });
        var tb = out.querySelector("tbody");
        rows.forEach(function (r) {
          var tr = document.createElement("tr");
          fields.forEach(function (f) { var td = document.createElement("td"); td.textContent = fmt(r[f.name], f); tr.appendChild(td); });
          tb.appendChild(tr);
        });
        status.textContent = res.numRows + " row" + (res.numRows === 1 ? "" : "s") + (res.numRows > 200 ? " (first 200 shown)" : "") + " · " + Math.round(performance.now() - t0) + " ms";
      }).catch(function (e) { status.textContent = "Error: " + String(e.message || e).split("\n")[0]; });
    }
    run.addEventListener("click", execute);
    input.addEventListener("keydown", function (e) { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") execute(); });
    Array.prototype.forEach.call(card.querySelectorAll("[data-sql]"), function (b) {
      b.addEventListener("click", function () { input.value = exampleSql(b.dataset.sql); execute(); });
    });
    import(DUCKDB).then(function (duckdb) {
      return duckdb.selectBundle(duckdb.getJsDelivrBundles()).then(function (bundle) {
        var url = URL.createObjectURL(new Blob(['importScripts("' + bundle.mainWorker + '");'], { type: "text/javascript" }));
        var db = new duckdb.AsyncDuckDB(new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING), new Worker(url));
        return db.instantiate(bundle.mainModule, bundle.pthreadWorker).then(function () {
          URL.revokeObjectURL(url);
          status.textContent = "Loading the sample tables…";
          return Promise.all(TABLES.map(function (t) {
            return fetch(box.dataset.src + t + ".parquet").then(function (r) { return r.arrayBuffer(); })
              .then(function (buf) { return db.registerFileBuffer(t + ".parquet", new Uint8Array(buf)); });
          }));
        }).then(function () { return db.connect(); });
      });
    }).then(function (c) {
      conn = c;
      return Promise.all(TABLES.map(function (t) { return conn.query("create view " + t + " as select * from '" + t + ".parquet'"); }));
    }).then(function () {
      run.disabled = false; status.textContent = "Ready. Ctrl+Enter runs the query.";
      execute(); if (pending) pending = null;
    }).catch(function (e) { status.textContent = "DuckDB could not start in this browser: " + String(e.message || e).split("\n")[0]; });
  };
})();
