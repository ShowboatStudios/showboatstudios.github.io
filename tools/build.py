#!/usr/bin/env python3
"""Render the static pages from data/apps.json.

  python3 tools/build.py

Writes index.html, press/index.html, press/<slug>/index.html, links/index.html, 404.html,
sitemap.xml. Images/zips/videos come from tools/media.py. assets/js/site.js re-reads
data/apps.json at load, so a status flip made on GitHub shows up even before a rebuild.
"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "apps.json")))
CFG, APPS = D["config"], D["apps"]
SITE = CFG.get("site", "https://showboatstudios.github.io").rstrip("/")
CONTACT = CFG.get("contact", "showboatcontact@gmail.com")
CSSV = str(int(os.path.getmtime(os.path.join(ROOT, "assets", "css", "site.css"))))
JSV = str(int(os.path.getmtime(os.path.join(ROOT, "assets", "js", "site.js"))))
e = lambda s: html.escape(str(s), quote=True)


def store_link(a, ct=None):
    t = (CFG.get("PROVIDER_TOKEN") or "").strip()
    if t and ct:
        return f"https://apps.apple.com/app/apple-store/id{a['app_id']}?pt={t}&ct={ct}&mt=8"
    return f"https://apps.apple.com/app/id{a['app_id']}"


def cta(a, ct):
    if a["status"] == "live":
        href = e(store_link(a, ct))
        if CFG.get("APP_STORE_BADGE"):
            return (f'<a class="badge-link" href="{href}"><img class="badge-img" src="{e(CFG["APP_STORE_BADGE"])}" '
                    f'alt="Download {e(a["store_name"])} on the App Store" width="144" height="48"></a>')
        return f'<a class="btn" href="{href}">Download on the App Store<span class="sr"> : {e(a["store_name"])}</span></a>'
    return '<span class="btn soon" role="note">Coming soon<span class="small">to the App Store</span></span>'


def pill(a):
    return f'<span class="pill" data-pill>{"Out now" if a["status"] == "live" else "Coming soon"}</span>'


def shots_meta(a):
    return json.load(open(os.path.join(ROOT, "assets", "img", a["slug"], "shots.json")))


def where(s):
    return "Cover screen" if "outer" in s["src"] else "Inner screen"


def page(title, desc, body, path, og_img=None, noindex=False, current=""):
    og = og_img or "/assets/img/og.png"
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if current == k else ""}>{t}</a>'
                  for k, h, t in (("apps", "/", "Apps"), ("press", "/press/", "Press kit")))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fff4e2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#17121f" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/site.css?v={CSSV}">
<script src="/assets/js/site.js?v={JSV}" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="wrap bar">
  <a class="brand" href="/"><span class="brand-mark" aria-hidden="true"></span><span class="brand-name">Showboat Studios</span></a>
  <nav class="nav" aria-label="Main">{nav}</nav>
</header>
<main id="main">
{body}
</main>
<footer class="wrap footer">
  <p><strong>Showboat Studios</strong> makes small, playful apps for iPhone Duo, Apple's book-style foldable. Every app also plays on any iPhone.
  Free. No ads, no accounts, no tracking, and this site has none either.</p>
  <p>Press and hello: <a href="mailto:{CONTACT}">{CONTACT}</a> &middot; <a href="/press/">Press kit</a></p>
  <p><small>iPhone and App Store are trademarks of Apple Inc., registered in the U.S. and other countries. Showboat Studios is not affiliated with Apple.</small></p>
</footer>
</body>
</html>
"""


def hub():
    cards = []
    for a in APPS:
        meta = shots_meta(a)
        strip = []
        for i in a["hub_shots"]:
            s, m = a["shots"][i], meta[i]
            h = 520; w = round(m["w"] * h / m["h"])
            strip.append(f'<li><figure style="margin:0"><img src="/assets/img/{a["slug"]}/{i+1:02d}-sm.webp" width="{w}" height="{h}" '
                         f'loading="lazy" decoding="async" alt="{e(s["alt"])}"><figcaption><span class="where">{where(s)}</span></figcaption></figure></li>')
        aka = ""
        if a["store_name"] != a["name"]:
            aka = f'<p class="aka">On the App Store as <strong>{e(a["store_name"])}</strong></p>'
        cards.append(f"""
<li class="card" id="{a['slug']}" data-app="{a['slug']}" data-status="{a['status']}" style="--accent:{a['accent']}">
  <div class="page page-a">
    <div class="head">
      <img class="icon" src="/assets/img/{a['slug']}/icon-256.webp" width="76" height="76" alt="">
      <div><h2>{e(a['name'])}</h2>{aka}{pill(a)}</div>
    </div>
    <p class="hook">{e(a['hook'])}</p>
    <p class="sub">{e(a['subtitle'])}. Free, and plays on every iPhone too.</p>
    <div class="actions"><span data-cta="hub">{cta(a, 'hub')}</span>
      <a class="btn ghost" href="/press/{a['slug']}/">Press kit<span class="sr"> for {e(a['name'])}</span></a></div>
    <p class="links-min"><a href="{e(a['support_url'])}">Support</a><a href="{e(a['privacy_url'])}">Privacy</a></p>
  </div>
  <div class="page page-b">
    <ul class="strip" aria-label="{e(a['name'])} screenshots on a real iPhone Duo">{''.join(strip)}</ul>
  </div>
</li>""")
    body = f"""
<section class="wrap hero">
  <span class="eyebrow">Showboat Studios</span>
  <h1>Apps made for the <span class="fold"><span>fold</span></span>.</h1>
  <p class="lede">Seven free games and toys for iPhone Duo where the hinge, the two inner halves and the cover screen are the whole point. Close it to fold a taco. Shut it and someone knocks. Open it like a laptop and type on a beige keyboard.</p>
  <ul class="chips" aria-label="What every app has">
    <li>Free</li><li>No ads</li><li>No accounts</li><li>No tracking</li><li>Plays on every iPhone</li>
  </ul>
</section>
<section class="wrap" aria-label="Apps">
  <ul class="apps">{''.join(cards)}
  </ul>
</section>
<section class="wrap section grid2">
  <div class="panel">
    <h2 class="big">Why the fold?</h2>
    <p>iPhone Duo opens like a book: a hinge you can feel, two inner halves and a screen on the cover. Most apps just stretch.
    These treat the hinge as a controller, the crease as a place things happen, and the cover as a second stage you can see with the phone shut.</p>
  </div>
  <div class="panel">
    <h2 class="big">Writing about them?</h2>
    <p>Fact sheets, descriptions, high-res icons, real-device screenshots and short demo videos for every app are in the <a href="/press/"><strong>press kit</strong></a>.
    Say hello at <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
  </div>
</section>"""
    return page("Showboat Studios: apps made for the fold",
                "Free games and toys for iPhone Duo that use the hinge, both inner screens and the cover screen. They play on every iPhone too.",
                body, "/", current="apps")


def press_index():
    items = "".join(f'<li data-app="{a["slug"]}" data-status="{a["status"]}"><a href="/press/{a["slug"]}/">'
                    f'<img src="/assets/img/{a["slug"]}/icon-256.webp" width="84" height="84" alt="">{e(a["name"])}{pill(a)}</a></li>'
                    for a in APPS)
    rows = "".join(f'<tr data-app="{a["slug"]}" data-status="{a["status"]}"><th>{e(a["name"])}</th><td>{e(a["store_name"])}</td>'
                   f'<td data-status-text>{"Out now on the App Store (free)" if a["status"] == "live" else a.get("soon_note", "Coming soon: in App Review")}</td></tr>'
                   for a in APPS)
    body = f"""
<section class="wrap hero" style="padding-bottom:20px">
  <span class="eyebrow">Press kit</span>
  <h1 style="font-size:clamp(2.6rem,11vw,5.6rem)">Seven apps, one fold.</h1>
  <p class="lede">Everything you need to write about Showboat Studios' iPhone Duo apps: fact sheets, copy, icons, real-device screenshots and demo videos. All of it is free to use for coverage.</p>
</section>
<section class="wrap section" style="padding-top:0">
  <ul class="mini-apps">{items}</ul>
</section>
<section class="wrap section grid2">
  <div class="panel">
    <h2 class="big">The studio</h2>
    <table class="facts"><tbody>
      <tr><th>Developer</th><td>Showboat Studios (Justin McCahill)</td></tr>
      <tr><th>Based in</th><td>United States</td></tr>
      <tr><th>Platform</th><td>iPhone, iOS 27 or later. Made for iPhone Duo; every app also plays on any iPhone.</td></tr>
      <tr><th>Price</th><td>Every app is free. No ads, no accounts, no tracking.</td></tr>
      <tr><th>Press contact</th><td><a href="mailto:{CONTACT}">{CONTACT}</a></td></tr>
      <tr><th>Web</th><td><a href="{SITE}/">{SITE.replace('https://', '')}</a></td></tr>
    </tbody></table>
  </div>
  <div class="panel">
    <h2 class="big">Release status</h2>
    <table class="facts"><tbody>{rows}</tbody></table>
    <div class="quote" style="margin-top:16px"><span class="tag">Placeholder: Justin to write</span>
      <p style="margin:6px 0 0">[Studio quote: one or two sentences in Justin's voice on why build apps only for the fold.]</p></div>
  </div>
</section>"""
    return page("Press kit | Showboat Studios", "Press kit for Showboat Studios' iPhone Duo apps: fact sheets, descriptions, icons, screenshots and demo videos.",
                body, "/press/", current="press")


def size(path):
    b = os.path.getsize(os.path.join(ROOT, path.lstrip("/")))
    return f"{b/1e6:.1f} MB" if b > 1e6 else f"{b/1e3:.0f} KB"


def press_app(a):
    slug = a["slug"]; meta = shots_meta(a)
    duo = [f["title"] + ": " + f["detail"] for f in a["features"][:2]]
    facts = [
        ("Name", e(a["name"]) + (f' (Home Screen name: {e(a["home_screen_name"])})' if a["home_screen_name"] != a["name"] else "")),
        ("App Store name", e(a["store_name"])),
        ("Developer", "Showboat Studios (Justin McCahill)"),
        ("Price", "Free"),
        ("Platforms", "iPhone, iOS 27 or later. Made for iPhone Duo; plays on every iPhone."),
        ("iPhone Duo features", "<ul>" + "".join(f"<li>{e(x)}</li>" for x in duo) + "</ul>"),
        ("Category", e(a["category"])),
        ("Version", e(a["version"])),
        ("Release status", f'<span data-status-text>{"Out now on the App Store (free)" if a["status"] == "live" else a.get("soon_note", "Coming soon: in App Review")}</span>'),
        ("App Store", f'<a href="{e(store_link(a))}">apps.apple.com/app/id{a["app_id"]}</a> <small>(live once Apple approves the app)</small>'),
        ("Support / privacy", f'<a href="{e(a["support_url"])}">Support</a> &middot; <a href="{e(a["privacy_url"])}">Privacy policy</a>'),
        ("Press contact", f'<a href="mailto:{CONTACT}?subject={e(a["name"])}%20press">{CONTACT}</a>'),
    ]
    facts_html = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in facts)
    icon = f"/press/{slug}/{slug}-icon-1024.png"; zipf = f"/press/{slug}/{slug}-screenshots.zip"; mp4 = f"/press/{slug}/{slug}-demo.mp4"
    gallery = "".join(
        f'<li><figure style="margin:0"><a href="/assets/img/{slug}/{i:02d}.webp"><img src="/assets/img/{slug}/{i:02d}-sm.webp" loading="lazy" decoding="async" '
        f'width="{round(m["w"]*520/m["h"])}" height="520" alt="{e(s["alt"])}"></a><figcaption><span class="where">{where(s)}</span>{e(s["alt"])}</figcaption></figure></li>'
        for i, (s, m) in enumerate(zip(a["shots"], meta), 1))
    feats = "".join(f'<li><b>{e(f["title"])}</b>{e(f["detail"])}</li>' for f in a["features"])

    def copyblock(id_, title, text, long=False):
        inner = f'<p class="txt" id="{id_}">{e(text)}</p>'
        if long:
            inner = f'<details class="long"><summary>Show the full App Store description</summary>{inner}</details>'
        return f'<div class="copyblock"><h3>{title}<button class="copy" type="button" data-copy="{id_}">Copy</button></h3>{inner}</div>'

    body = f"""
<div data-app="{slug}" data-status="{a['status']}" style="--accent:{a['accent']}">
<section class="wrap press-hero">
  <img class="icon" src="/assets/img/{slug}/icon-512.png" width="132" height="132" alt="{e(a['name'])} app icon">
  <div>
    <h1>{e(a['name'])}</h1>
    <p style="margin:8px 0 6px;font-weight:700;font-size:1.15rem">{e(a['hook'])}</p>
    {pill(a)}
    <div class="actions" style="margin-top:14px"><span data-cta="presskit">{cta(a, 'presskit')}</span>
      <a class="btn ghost" href="/#{slug}">See it on the hub</a></div>
  </div>
</section>
<section class="wrap grid2">
  <div class="panel"><h2 class="big">Fact sheet</h2><table class="facts"><tbody>{facts_html}</tbody></table></div>
  <div>
    <div class="panel" style="margin-bottom:22px">
      <h2 class="big">Downloads</h2>
      <ul class="dl">
        <li><a href="{icon}" download>High-res icon (1024&times;1024 PNG)<small>{size(icon)}</small></a></li>
        <li><a href="{zipf}" download>All screenshots, full resolution (ZIP)<small>{size(zipf)}</small></a></li>
        <li><a href="{mp4}" download>Demo video (MP4, 1080&times;1080, ~20 s)<small>{size(mp4)}</small></a></li>
      </ul>
      <p style="font-size:.88rem;color:var(--ink-2);margin:12px 0 0">Screenshots are real captures from an iPhone Duo. "Inner" is the big folding screen, "cover" the outside screen.</p>
    </div>
    <div class="video"><video controls preload="none" playsinline poster="/assets/img/{slug}/demo-poster.webp" width="1080" height="1080">
      <source src="{mp4}" type="video/mp4">Your browser can't play this video; <a href="{mp4}">download it</a>.</video></div>
  </div>
</section>
<section class="wrap section">
  <h2 class="big">Descriptions</h2>
  {copyblock('d-short', 'Short (one line)', a['short'])}
  {copyblock('d-medium', 'Medium (one paragraph)', a['medium'])}
  {copyblock('d-long', 'Long (App Store description)', a['long'], long=True)}
</section>
<section class="wrap section">
  <h2 class="big">Key features</h2>
  <ul class="features">{feats}</ul>
</section>
<section class="wrap section">
  <h2 class="big">Screenshots</h2>
  <ul class="gallery">{gallery}</ul>
</section>
<section class="wrap section">
  <h2 class="big">Quotes</h2>
  <div class="quote"><span class="tag">Placeholder: Justin to write</span><p style="margin:6px 0 0">[Developer quote on why {e(a['name'])} is built around the fold. Attribute to: Justin McCahill, Showboat Studios.]</p></div>
  <div class="quote"><span class="tag">Placeholder: Justin to write</span><p style="margin:6px 0 0">[A second quote: a favourite moment, a tester reaction, or how it plays on a regular iPhone.]</p></div>
</section>
</div>"""
    return page(f"{a['name']} press kit | Showboat Studios", f"{a['name']} for iPhone Duo: {a['short']}", body, f"/press/{slug}/",
                og_img=f"/assets/img/{slug}/icon-512.png", current="press")


def links_page():
    t = (CFG.get("PROVIDER_TOKEN") or "").strip()
    rows = []
    for a in APPS:
        rows.append(f"<h3>{e(a['name'])} <small>({e(a['store_name'])}, id{a['app_id']})</small></h3><table class='linktable'><tbody>")
        for ct in CFG.get("campaigns", []):
            rows.append(f"<tr><th>{e(ct)}</th><td class='mono'>{e(store_link(a, ct if t else None))}</td></tr>")
        rows.append("</tbody></table>")
    note = "" if t else ('<p class="note">PROVIDER_TOKEN is empty in /data/apps.json, so these are plain store links. Paste the token '
                         '(App Store Connect &gt; Analytics &gt; Acquisition &gt; Campaigns &gt; Generate Campaign Link, the <code>pt=</code> value) '
                         'and every link below becomes a tracked campaign link.</p>')
    body = f"""
<section class="wrap section">
  <h1 style="font:900 clamp(2rem,8vw,3.4rem)/1 var(--display)">Campaign links</h1>
  <p>One App Store link per app per channel, in Apple's campaign format
  <code>https://apps.apple.com/app/apple-store/id&lt;ID&gt;?pt=&lt;PROVIDER_TOKEN&gt;&amp;ct=&lt;campaign&gt;&amp;mt=8</code>.
  Downloads show up per campaign in App Store Connect &gt; Analytics &gt; Acquisition. Channels come from <code>config.campaigns</code> in <code>/data/apps.json</code>.</p>
  <div id="campaign-links">{note}{''.join(rows)}</div>
</section>"""
    return page("Campaign links | Showboat Studios", "App Store campaign links per app and channel.", body, "/links/", noindex=True)


def write(rel, text):
    p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text); print("wrote", rel)


def main():
    write("index.html", hub())
    write("press/index.html", press_index())
    for a in APPS:
        write(f"press/{a['slug']}/index.html", press_app(a))
    write("links/index.html", links_page())
    write("404.html", page("Not found | Showboat Studios", "Page not found.",
                           '<section class="wrap hero"><h1>Folded the wrong way.</h1><p class="lede">That page isn\'t here. '
                           '<a href="/">Back to the apps</a>.</p></section>', "/404.html", noindex=True))
    urls = ["/", "/press/"] + [f"/press/{a['slug']}/" for a in APPS]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")


if __name__ == "__main__":
    main()
