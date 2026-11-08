// Reads /data/apps.json at load so flipping an app's "status" (or setting PROVIDER_TOKEN)
// works straight from a GitHub web edit, without a rebuild. The HTML is pre-rendered, so the
// page is complete without this script; it only refreshes status, buttons and links.
(function () {
  "use strict";
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function storeLink(a, cfg, ct) {
    var t = (cfg.PROVIDER_TOKEN || "").trim();
    if (t && ct) return "https://apps.apple.com/app/apple-store/id" + a.app_id + "?pt=" + encodeURIComponent(t) + "&ct=" + encodeURIComponent(ct) + "&mt=8";
    return "https://apps.apple.com/app/id" + a.app_id;
  }
  function cta(a, cfg, ct) {
    if (a.status === "live") {
      var href = esc(storeLink(a, cfg, ct));
      if (cfg.APP_STORE_BADGE) return '<a class="badge-link" href="' + href + '"><img class="badge-img" src="' + esc(cfg.APP_STORE_BADGE) + '" alt="Download ' + esc(a.store_name) + ' on the App Store" width="144" height="48"></a>';
      return '<a class="btn" href="' + href + '">Download on the App Store<span class="sr"> : ' + esc(a.store_name) + '</span></a>';
    }
    return '<span class="btn soon" role="note">Coming soon<span class="small">to the App Store</span></span>';
  }
  function statusText(a) { return a.status === "live" ? "Out now on the App Store (free)" : (a.soon_note || "Coming soon: in App Review"); }
  window.SB = { storeLink: storeLink };

  fetch("/data/apps.json", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (d) {
    var cfg = d.config || {};
    document.querySelectorAll("[data-app]").forEach(function (el) {
      var a = d.apps.filter(function (x) { return x.slug === el.getAttribute("data-app"); })[0];
      if (!a) return;
      el.setAttribute("data-status", a.status);
      el.querySelectorAll("[data-cta]").forEach(function (c) { c.innerHTML = cta(a, cfg, c.getAttribute("data-cta")); });
      el.querySelectorAll("[data-pill]").forEach(function (p) { p.textContent = a.status === "live" ? "Out now" : "Coming soon"; });
      el.querySelectorAll("[data-status-text]").forEach(function (p) { p.textContent = statusText(a); });
    });
    var lt = document.getElementById("campaign-links");
    if (lt) renderLinks(lt, d, cfg);
  }).catch(function () {});

  function renderLinks(box, d, cfg) {
    var t = (cfg.PROVIDER_TOKEN || "").trim();
    var html = "";
    if (!t) html += '<p class="note">PROVIDER_TOKEN is empty in /data/apps.json, so these are plain store links. Paste the token (App Store Connect &gt; Analytics &gt; Acquisition &gt; Campaigns &gt; Generate Campaign Link, the <code>pt=</code> value) and every link below becomes a tracked campaign link.</p>';
    d.apps.forEach(function (a) {
      html += '<h3>' + esc(a.name) + ' <small>(' + esc(a.store_name) + ', id' + esc(a.app_id) + ')</small></h3><table class="linktable"><tbody>';
      (cfg.campaigns || []).forEach(function (ct) {
        html += "<tr><th>" + esc(ct) + '</th><td class="mono">' + esc(storeLink(a, cfg, t ? ct : "")) + "</td></tr>";
      });
      html += "</tbody></table>";
    });
    box.innerHTML = html;
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("button.copy");
    if (!b) return;
    var src = document.getElementById(b.getAttribute("data-copy"));
    if (!src || !navigator.clipboard) return;
    navigator.clipboard.writeText(src.innerText).then(function () {
      var old = b.textContent; b.textContent = "Copied!"; setTimeout(function () { b.textContent = old; }, 1400);
    });
  });
})();
