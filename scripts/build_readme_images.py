"""Crop actual synthetic-profile demo captures for the repository overview.

Requires Pillow. No image content is generated or changed beyond crop/resize.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
destination = ROOT / "docs/images"
destination.mkdir(exist_ok=True)
for name, height in (("coach-desktop", 1700), ("coach-mobile", 2500)):
    source = Image.open(ROOT / "artifacts" / f"{name}.png").convert("RGB")
    image = source.crop((0, 0, source.width, min(height, source.height)))
    if image.width > 1440:
        image.thumbnail((1440, 3000))
    image.save(destination / f"{name}.png", optimize=True)
    print(f"Saved {name}.png: {image.width}x{image.height}")
