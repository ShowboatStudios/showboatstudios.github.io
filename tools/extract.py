#!/usr/bin/env python3
"""One-off: seed data/apps.json from each repo's AppStore/listing.json.

Hand-edited fields (status, hook, colour, shots) are preserved if data/apps.json already exists.
Run:  python3 tools/extract.py
"""
import json, os, re, sys

DEV = os.path.expanduser("~/Developer")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "apps.json")

APPS = [
    # slug, display name, repo, project-pages repo, accent, hook
    ("hingebox", "Hingebox", "Hingebox", "hingebox", "#f2581b",
     "Fold the hinge to bend the beat. Close the phone and Bop dances to your groove on the cover screen."),
    ("knock-knock", "Knock Knock", "KnockKnockDuo", "knock-knock-duo", "#1f6b3c",
     "The hinge is the front door: shut the phone and someone knocks on the cover. Open it and the punchline is on the porch."),
    ("taco-fold", "Taco Fold", "TacoDuo", "taco-fold", "#f29a12",
     "Close the phone to fold the taco, plate it on the cover screen, then open up for three tough judges."),
    ("planet-pass", "Planet Pass", "WhereaboutsDuo", "whereabouts-duo", "#e3407a",
     "Close it to pass it on: the cover calls whose turn it is. Open it and you're standing on a real street somewhere on Earth."),
    ("user-agreement", "User Agreement", "PreambleDuo", "preamble-duo", "#2f2f8f",
     "Fold the hinge to exactly 75°, dial a lock with it, read codes off the cover screen. Setup microgames for a thing that never starts."),
    ("fourfold", "Fourfold", "FourfoldDuo", "fourfold-duo", "#2457c9",
     "Stand it up like a little board: one player on the inner screen, the other across the table on the cover screen."),
    ("desktop-95", "Desktop 95", "Desktop95", "desktop-95", "#0a7f7d",
     "Fold it like a laptop: the top half is a 90s monitor, the bottom half a clicky beige keyboard and trackpad."),
]

STORE_NAMES = {"knock-knock": "Knock Knock Simulator", "taco-fold": "Taco Simulator",
               "planet-pass": "Planet Pass Geo", "user-agreement": "User Agreement",
               "fourfold": "Fourfold: Four in a Row"}
HOME_NAMES = {"user-agreement": "Preamble"}


def features(desc):
    """ALL-CAPS heading lines become features; the following paragraph's first sentence is the detail."""
    paras = [p.strip() for p in desc.split("\n\n") if p.strip()]
    out = []
    for p in paras:
        lines = p.split("\n")
        head = lines[0].strip()
        if head.upper() == head and re.search(r"[A-Z]", head) and len(head) < 60:
            body = " ".join(l.strip("-• ").strip() for l in lines[1:]).strip()
            first = re.split(r"(?<=[.!?])\s", body, maxsplit=1)[0] if body else ""
            title = head.title().replace("Iphone", "iPhone").replace("'S", "'s")
            out.append({"title": title, "detail": first})
    return out


def main():
    old = {}
    if os.path.exists(OUT):
        for a in json.load(open(OUT))["apps"]:
            old[a["slug"]] = a
    apps = []
    for slug, name, repo, pages, accent, hook in APPS:
        L = json.load(open(os.path.join(DEV, repo, "AppStore", "listing.json")))
        vl, ai = L["version_localization"], L["app_info_localization"]
        desc = vl["description"].strip()
        paras = [p.strip() for p in desc.split("\n\n") if p.strip()]
        a = {
            "slug": slug,
            "name": name,
            "store_name": STORE_NAMES.get(slug, name),
            "home_screen_name": HOME_NAMES.get(slug, name),
            "app_id": L["app_id"],
            "status": "coming_soon",
            "accent": accent,
            "hook": hook,
            "subtitle": ai.get("subtitle", ""),
            "short": vl.get("promotionalText", ""),
            "medium": "\n\n".join(paras[:2]),
            "long": desc,
            "features": features(desc),
            "version": L.get("version", ""),
            "category": L["categories"]["primary"].replace("_", " ").title(),
            "support_url": vl.get("supportUrl"),
            "privacy_url": ai.get("privacyPolicyUrl"),
            "repo_dir": repo,
            "pages_repo": pages,
        }
        if slug in old:  # keep hand edits
            for k in ("status", "hook", "accent", "shots", "hub_shots", "video_shots", "features", "quotes"):
                if k in old[slug]:
                    a[k] = old[slug][k]
        apps.append(a)
    cfg = old and json.load(open(OUT)).get("config") or {
        "PROVIDER_TOKEN": "",
        "campaigns": ["hub", "presskit", "reddit", "x", "threads", "bluesky", "mastodon", "producthunt",
                      "hackernews", "discord", "youtube", "tiktok", "instagram", "press", "newsletter", "blog", "email"],
        "contact": "showboatcontact@gmail.com",
        "site": "https://showboatstudios.github.io",
    }
    json.dump({"_readme": "Flip an app live: set its \"status\" to \"live\" (or back to \"coming_soon\"). "
               "Paste the App Store Connect provider token into config.PROVIDER_TOKEN to turn on campaign links. "
               "The pages read this file at load, so edits work without a rebuild; run tools/build.py to bake them into the HTML too.",
               "config": cfg, "apps": apps}, open(OUT, "w"), indent=2, ensure_ascii=False)
    print("wrote", OUT)
    for a in apps:
        print(a["slug"], len(a["features"]), [f["title"] for f in a["features"]])


if __name__ == "__main__":
    main()
