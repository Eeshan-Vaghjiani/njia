"""Offline caption-only correction of the existing final video; no app/API calls."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright
from record_demo import caption, probe

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
VIDEO = OUT / "njia-demo-90s.webm"
BACKUP = OUT / "njia-demo-90s-before-caption-correction.webm"
RESULTS = OUT / "njia-coach-demo-results.json"
EDITS = [
    (53, 57, "Draft rewrites need factual review. Verify every claim against your CV and answers; AI can add unsupported details."),
    (76, 83, "AI feedback suggests structure. Verify every fact; it can add unsupported details."),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transition(ffmpeg, source, cue):
    """Find the caption-copy transition in actual encoded frames near the cue."""
    first, last = round((cue - .6) * 25), round((cue + .6) * 25)
    width, height = 1180, 48
    raw = subprocess.check_output([
        ffmpeg, "-v", "error", "-i", str(source), "-vf",
        f"select='between(n,{first},{last})',crop={width}:{height}:44:642,format=gray",
        "-fps_mode", "passthrough", "-f", "rawvideo", "pipe:1",
    ])
    size = width * height
    images = [Image.frombytes("L", (width, height), raw[i:i + size]) for i in range(0, len(raw), size)]
    changes = [(ImageStat.Stat(ImageChops.difference(a, b)).mean[0], first + i)
               for i, (a, b) in enumerate(zip(images, images[1:]), 1)]
    delta, frame = max(changes)
    assert delta > 1, (cue, changes)
    print(f"Caption transition near {cue}s: frame {frame}, {frame / 25:.3f}s, delta {delta:.3f}", flush=True)
    return frame


def main():
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    assert ffmpeg and ffprobe
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert result["status"] == "passed" and not result.get("caption_corrections"), "Already corrected or not a passed recording."
    assert not BACKUP.exists(), "Caption backup already exists; inspect before repeating."
    shutil.copy2(VIDEO, BACKUP)
    shutil.copy2(RESULTS, OUT / "njia-coach-demo-results-before-caption-correction.json")
    corrections = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        page.route("**/*", lambda route: route.abort())
        page.set_content('<html><body style="margin:0;background:transparent"></body></html>')
        for cue, end, text in EDITS:
            entry = next(item for item in result["timeline"] if item["cue_seconds"] == cue)
            start_frame, end_frame = transition(ffmpeg, BACKUP, cue), transition(ffmpeg, BACKUP, end)
            caption(page, entry["section"], text)
            # The original caption shadow remains in the source. Replace only its box.
            page.evaluate("document.getElementById('demo-caption').style.boxShadow='none'; document.getElementById('demo-sync')?.remove()")
            png = OUT / f"caption-correction-{cue}.png"
            page.screenshot(path=str(png), clip={"x": 20, "y": 600, "width": 1240, "height": 100}, omit_background=True)
            corrections.append({"cue_seconds": cue, "start_frame": start_frame, "end_frame_exclusive": end_frame,
                                "start_seconds": start_frame / 25, "end_seconds_exclusive": end_frame / 25,
                                "original_caption": entry["caption"], "corrected_caption": text,
                                "section": entry["section"], "overlay_png": png.name})
            entry["caption"] = text
        browser.close()
    target = OUT / "njia-demo-90s-caption-corrected.webm"
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(BACKUP)]
    for item in corrections:
        command += ["-i", str(OUT / item["overlay_png"])]
    filters = []
    for i, item in enumerate(corrections):
        source = "0:v" if i == 0 else f"v{i}"
        # Overlay n is one-indexed; use timestamps to select exact 25fps frames.
        filters.append(f"[{source}][{i+1}:v]overlay=20:600:enable='gte(t,{item['start_seconds']})*lt(t,{item['end_seconds_exclusive']})':format=yuv420[v{i+1}]")
    command += ["-filter_complex", ";".join(filters), "-map", f"[v{len(corrections)}]", "-an",
                "-c:v", "libvpx-vp9", "-lossless", "1", "-deadline", "good", "-cpu-used", "4",
                "-frames:v", "2250", str(target)]
    subprocess.run(command, check=True)
    meta = probe(target, ffprobe)
    assert float(meta["format"]["duration"]) == 90
    assert len(meta["streams"]) == 1
    stream = meta["streams"][0]
    assert (stream["width"], stream["height"], stream["r_frame_rate"]) == (1280, 720, "25/1")
    # Decoded pixel equality outside the two correction windows and outside the box
    # proves lossless re-encoding did not alter the actual application footage.
    def frame_hashes(path, filter_text):
        return subprocess.check_output([ffmpeg, "-v", "error", "-i", str(path), "-vf", filter_text,
                                        "-fps_mode", "passthrough", "-f", "framemd5", "pipe:1"])
    unaffected = "not(" + "+".join(f"between(n,{x['start_frame']},{x['end_frame_exclusive']-1})" for x in corrections) + ")"
    assert frame_hashes(BACKUP, f"select='{unaffected}'") == frame_hashes(target, f"select='{unaffected}'"), "Changed frame outside caption windows"
    assert frame_hashes(BACKUP, "crop=1280:600:0:0") == frame_hashes(target, "crop=1280:600:0:0"), "Changed application pixels above caption"
    assert frame_hashes(BACKUP, "crop=1280:20:0:700") == frame_hashes(target, "crop=1280:20:0:700"), "Changed pixels below caption"
    for x in (0, 1260):
        assert frame_hashes(BACKUP, f"crop=20:100:{x}:600") == frame_hashes(target, f"crop=20:100:{x}:600"), "Changed pixels beside caption"
    result["caption_corrections"] = {
        "method": "Offline PNG caption overlays with ffmpeg; lossless VP9 re-encode. Only narration captions changed.",
        "segments": corrections, "bounds": {"x": 20, "y": 600, "width": 1240, "height": 100},
        "model_or_application_outputs_edited": False, "new_api_requests": 0, "playback_speed": "1x",
        "original_video": BACKUP.name, "original_sha256": digest(BACKUP), "corrected_sha256": digest(target),
        "verification": "Decoded frame hashes identical outside correction windows; decoded pixels identical outside caption rectangle in every frame.",
    }
    result["video"]["probe"] = meta
    shutil.copy2(target, VIDEO)
    shutil.copy2(target, OUT / "njia-coach-demo-90s.webm")
    RESULTS.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["caption_corrections"], indent=2))


if __name__ == "__main__":
    main()
