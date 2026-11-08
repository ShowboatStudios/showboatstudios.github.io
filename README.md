# showboatstudios.github.io

The Showboat Studios app hub and press kit, served by GitHub Pages at
https://showboatstudios.github.io/ (root org site, `main` branch, `/`).

- `/` hub: one card per app
- `/press/` studio press kit, `/press/<app>/` per-app press kit (fact sheet, copy, icon, screenshot zip, demo video)
- `/links/` App Store campaign links per app and channel (noindex)

The per-app support and privacy pages are **not** here: they are project Pages from each app repo
(`showboatstudios.github.io/<repo>/support.html`). GitHub serves a project site in preference to
a same-named folder here, so never add a top-level folder named after an app repo
(`hingebox`, `knock-knock-duo`, `taco-fold`, `whereabouts-duo`, `preamble-duo`, `fourfold-duo`, `desktop-95`, ...).

## Flip an app to live (when Apple approves it)

Edit `data/apps.json` (the GitHub web editor is fine): set that app's `"status"` from
`"coming_soon"` to `"live"`. The pages read this file at load, so the button changes at once;
running `python3 tools/build.py` afterwards bakes it into the HTML too (for no-JS visitors and previews).

## Campaign links

Paste the App Store Connect provider token into `config.PROVIDER_TOKEN` in `data/apps.json`
(App Store Connect > Analytics > Acquisition > Campaigns > Generate Campaign Link: the `pt=` value).
Then every Download button uses `https://apps.apple.com/app/apple-store/id<ID>?pt=<token>&ct=<campaign>&mt=8`
(`ct=hub` on the hub, `ct=presskit` on press pages) and `/links/` lists one link per channel in `config.campaigns`.

## App Store badge

Buttons are plain text ("Download on the App Store") because the official badge artwork has to come
from Apple's marketing resources (https://developer.apple.com/app-store/marketing/guidelines/).
To use it, download the black "Download on the App Store" SVG there, save it as
`assets/img/app-store-badge.svg`, and set `config.APP_STORE_BADGE` to `/assets/img/app-store-badge.svg`.
Apple's guidelines only allow the badge for apps that are available, so coming-soon apps keep the text label.

## Rebuild

```bash
python3 tools/extract.py   # re-seed copy from ~/Developer/<Repo>/AppStore/listing.json (keeps status, hooks, shots)
python3 tools/media.py     # icons, web images, screenshot zips, demo videos (needs sips + ~/.local/bin/ffmpeg); FORCE=1 to redo
python3 tools/build.py     # HTML from data/apps.json
python3 -m http.server 8765  # preview at http://127.0.0.1:8765/
```

No trackers, no analytics, no external requests: system fonts, and CSS/JS served from this repo only.

## Changes

Follow the ShowboatStudios playbook (showboat-ops/PLAYBOOK.md): issue, claim, branch, PR, merge.
