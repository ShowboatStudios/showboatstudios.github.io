#!/usr/bin/env python3
"""Build the site's images, screenshot zips and demo videos from the app repos.

Reads data/apps.json (shots list per app, paths relative to <repo>/AppStore/Screenshots) and the
current AppIcon from each repo's AppIcon.appiconset. Needs macOS `sips` and ffmpeg.
Run:  python3 tools/media.py [slug ...]      (no args = every app; skips files that already exist
                                              unless FORCE=1)
"""
import json, os, shutil, subprocess, sys, tempfile, zipfile

DEV = os.path.expanduser("~/Developer")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = os.environ.get("FFMPEG", os.path.expanduser("~/.local/bin/ffmpeg"))
FORCE = os.environ.get("FORCE") == "1"
FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
ICON_DIRS = {"Hingebox": "Hingebox", "KnockKnockDuo": "KnockKnock", "TacoDuo": "TacoFold",
             "WhereaboutsDuo": "Whereabouts", "PreambleDuo": "Preamble", "FourfoldDuo": "Fourfold",
             "Desktop95": "Desktop95"}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("FAILED: %s\n%s" % (" ".join(cmd), r.stderr[-2000:]))


def ff(*args):
    run([FFMPEG, "-loglevel", "error", "-y", *args])


def need(path):
    return FORCE or not os.path.exists(path)


def icon_src(repo):
    d = os.path.join(DEV, repo, ICON_DIRS[repo], "Assets.xcassets", "AppIcon.appiconset")
    c = json.load(open(os.path.join(d, "Contents.json")))
    for i in c["images"]:
        if i.get("filename") and not i.get("appearances"):
            return os.path.join(d, i["filename"])
    sys.exit("no icon for " + repo)


def dims(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    w = int(out.split("pixelWidth:")[1].split()[0]); h = int(out.split("pixelHeight:")[1].split()[0])
    return w, h


def build(app):
    slug, repo = app["slug"], app["repo_dir"]
    shots_dir = os.path.join(DEV, repo, "AppStore", "Screenshots")
    img = os.path.join(ROOT, "assets", "img", slug); os.makedirs(img, exist_ok=True)
    press = os.path.join(ROOT, "press", slug); os.makedirs(press, exist_ok=True)

    # icon
    ic = icon_src(repo)
    big = os.path.join(press, f"{slug}-icon-1024.png")
    if need(big): shutil.copyfile(ic, big)
    for size, ext in ((256, "webp"), (512, "png")):
        out = os.path.join(img, f"icon-{size}.{ext}")
        if need(out): ff("-i", ic, "-vf", f"scale={size}:{size}:flags=lanczos", *(["-quality", "85"] if ext == "webp" else []), out)

    # screenshots: web sizes + record dimensions for width/height attributes
    meta = []
    for n, s in enumerate(app["shots"], 1):
        src = os.path.join(shots_dir, s["src"])
        w, h = dims(src)
        lg = os.path.join(img, f"{n:02d}.webp"); sm = os.path.join(img, f"{n:02d}-sm.webp")
        if need(lg): ff("-i", src, "-vf", "scale='if(gt(iw,ih),1600,-2)':'if(gt(iw,ih),-2,1600)':flags=lanczos", "-quality", "80", lg)
        if need(sm): ff("-i", src, "-vf", "scale=-2:520:flags=lanczos", "-quality", "78", sm)
        meta.append({"w": w, "h": h})
    json.dump(meta, open(os.path.join(img, "shots.json"), "w"))

    # screenshot zip: full resolution, high-quality JPEG (originals are 3-8 MB PNGs each)
    z = os.path.join(press, f"{slug}-screenshots.zip")
    if need(z):
        with tempfile.TemporaryDirectory() as t, zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
            for n, s in enumerate(app["shots"], 1):
                kind = "cover" if "outer" in s["src"] else "inner"
                name = f"{slug}-{n:02d}-{kind}.jpg"
                out = os.path.join(t, name)
                run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "92", os.path.join(shots_dir, s["src"]), "--out", out])
                zf.write(out, f"{slug}-screenshots/{name}")
            zf.write(big, f"{slug}-screenshots/{slug}-icon-1024.png")
            zf.writestr(f"{slug}-screenshots/README.txt",
                        f"{app['name']} (App Store: {app['store_name']}) by Showboat Studios\n"
                        "Real iPhone Duo device captures. 'inner' = the big folding screen, 'cover' = the outside screen.\n"
                        "Free to use for coverage of the app. Contact: showboatcontact@gmail.com\n")

    # demo video: Ken Burns slideshow on the app's colour, 1080x1080, ~20 s, then an end card
    mp4 = os.path.join(press, f"{slug}-demo.mp4")
    if need(mp4):
        make_video(app, shots_dir, ic, mp4)
        ff("-ss", "5", "-i", mp4, "-frames:v", "1", "-vf", "scale=720:-2", "-quality", "80", os.path.join(img, "demo-poster.webp"))
    print("done", slug)


def make_video(app, shots_dir, icon, out):
    fps, seg, fade = 30, 3.6, 0.5
    color = app["accent"].lstrip("#")
    picks = [app["shots"][i] for i in app["video_shots"]]
    with tempfile.TemporaryDirectory() as t:
        parts = []
        for k, s in enumerate(picks):
            src = os.path.join(shots_dir, s["src"])
            p = os.path.join(t, f"p{k}.mp4")
            frames = int(seg * fps)
            zin = k % 2 == 0  # alternate zoom in / zoom out
            z = f"1+0.07*on/{frames}" if zin else f"1.07-0.07*on/{frames}"
            vf = (f"scale=1880:1880:force_original_aspect_ratio=decrease:flags=lanczos,"
                  f"pad=2160:2160:(ow-iw)/2:(oh-ih)/2:color=0x{color},setsar=1,"
                  f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1080:fps={fps},format=yuv420p")
            ff("-loop", "1", "-i", src, "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "20", p)
            parts.append(p)
        # end card
        endc = os.path.join(t, "end.mp4")
        txt1 = "Made for iPhone Duo"; txt2 = "Plays on every iPhone too"
        vf = (f"color=c=0x{color}:s=1080x1080:d=3:r={fps}[bg];[0]scale=360:360[ic];"
              f"[bg][ic]overlay=(W-w)/2:250,"
              f"drawtext=fontfile='{FONT}':text='{app['name']}':fontcolor=white:fontsize=76:x=(w-tw)/2:y=650,"
              f"drawtext=fontfile='{FONT}':text='{txt1}':fontcolor=white@0.92:fontsize=44:x=(w-tw)/2:y=760,"
              f"drawtext=fontfile='{FONT}':text='{txt2}':fontcolor=white@0.8:fontsize=34:x=(w-tw)/2:y=830,"
              f"drawtext=fontfile='{FONT}':text='showboatstudios.github.io':fontcolor=white@0.7:fontsize=28:x=(w-tw)/2:y=960,format=yuv420p")
        ff("-i", icon, "-filter_complex", vf, "-frames:v", str(3 * fps), "-c:v", "libx264", "-crf", "20", endc)
        parts.append(endc)
        # chain with crossfades
        inputs = []
        for p in parts: inputs += ["-i", p]
        chain, last, offset = [], "[0:v]", 0.0
        durs = [seg] * (len(parts) - 1) + [3.0]
        for i in range(1, len(parts)):
            offset += durs[i - 1] - fade
            lab = f"[x{i}]"
            chain.append(f"{last}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.2f}{lab}")
            last = lab
        ff(*inputs, "-filter_complex", ";".join(chain), "-map", last, "-c:v", "libx264", "-preset", "slow",
           "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out)


def main():
    data = json.load(open(os.path.join(ROOT, "data", "apps.json")))
    want = set(sys.argv[1:])
    for a in data["apps"]:
        if not want or a["slug"] in want:
            build(a)


if __name__ == "__main__":
    main()
