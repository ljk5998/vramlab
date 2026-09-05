#!/usr/bin/env python3
"""Render VRAM Lab's two text-only 1200x630 social cards.

Requires Pillow and Windows Segoe UI/Consolas fonts. For another environment,
pass --font-dir pointing at a licensed copy of those same font files. The script
creates new images from typography and geometric layout; it does not read or
modify any previous social card. Run again to regenerate these two outputs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = (1200, 630)
SCALE = 2
BACKGROUND = "#1B1B1B"
FOREGROUND = "#F8F8F5"
SECONDARY = "#C4C4BC"
ACCENT = "#438FE5"
CHIP_BACKGROUND = "#25282D"
BORDER = "#3A3E43"
MARGIN = 68


class Card:
    def __init__(self, font_dir: Path) -> None:
        self.font_dir = font_dir
        self.image = Image.new("RGB", (SIZE[0] * SCALE, SIZE[1] * SCALE), BACKGROUND)
        self.draw = ImageDraw.Draw(self.image)

    def font(self, size: int, *, bold: bool = False, mono: bool = False):
        filename = "consolab.ttf" if mono else "segoeuib.ttf" if bold else "segoeui.ttf"
        return ImageFont.truetype(str(self.font_dir / filename), size * SCALE)

    def text(self, value: str, x: int, y: int, size: int, *, color=FOREGROUND,
             bold: bool = False, mono: bool = False) -> None:
        font = self.font(size, bold=bold, mono=mono)
        position = (x * SCALE, y * SCALE)
        bounds = self.draw.textbbox(position, value, font=font, anchor="lt")
        assert 0 <= bounds[0] < bounds[2] <= SIZE[0] * SCALE, (value, bounds)
        assert 0 <= bounds[1] < bounds[3] <= SIZE[1] * SCALE, (value, bounds)
        self.draw.text(position, value, font=font, fill=color, anchor="lt")

    def chips(self, labels: tuple[str, ...], y: int) -> None:
        x = MARGIN
        font = self.font(23)
        for label in labels:
            width = round(self.draw.textlength(label, font=font) / SCALE) + 36
            assert x + width <= SIZE[0] - MARGIN, (label, x, width)
            box = (x * SCALE, y * SCALE, (x + width) * SCALE, (y + 49) * SCALE)
            self.draw.rounded_rectangle(box, radius=9 * SCALE, fill=CHIP_BACKGROUND,
                                        outline=BORDER, width=SCALE)
            self.text(label, x + 18, y + 10, 23, color=SECONDARY)
            x += width + 14

    def footer(self) -> None:
        self.draw.line((MARGIN * SCALE, 552 * SCALE, (SIZE[0] - MARGIN) * SCALE,
                        552 * SCALE), fill=BORDER, width=SCALE)
        self.text("vramlab.com", MARGIN, 576, 24, color=ACCENT, bold=True)

    def save(self, output: Path) -> None:
        self.image.resize(SIZE, Image.Resampling.LANCZOS).save(output, format="PNG",
                                                           optimize=True)
        print(f"{output} ({SIZE[0]} x {SIZE[1]})")


def render_brand(font_dir: Path, output: Path) -> None:
    card = Card(font_dir)
    card.text("VRAM Lab", MARGIN, 48, 31, color=ACCENT, bold=True)
    card.text("Local AI, tested", MARGIN, 137, 68, bold=True)
    card.text("on consumer hardware", MARGIN, 220, 68, bold=True)
    card.chips(("Windows + WSL2", "CUDA compatibility", "8 GB inference"), 340)
    card.text("Exact versions, commands,", MARGIN, 426, 31, color=SECONDARY)
    card.text("measurements and logs.", MARGIN, 468, 31, color=SECONDARY)
    card.footer()
    card.save(output)


def render_dataset_report(font_dir: Path, output: Path) -> None:
    card = Card(font_dir)
    card.text("VRAM Lab", MARGIN, 48, 31, color=ACCENT, bold=True)
    card.text("HF_DATASETS_CACHE", MARGIN, 138, 66, mono=True)
    card.text("on WSL2", MARGIN, 221, 66, bold=True)
    card.text("Where the other files go", MARGIN, 319, 39, color=SECONDARY)
    card.chips(("Hub sources", "Arrow files", "Imports", "Cleanup"), 393)
    card.text("17 conditions × 3 runs", MARGIN, 481, 27, bold=True)
    card.text("Measured 2026-09-06", 720, 481, 26, color=SECONDARY)
    card.footer()
    card.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    for filename in ("segoeui.ttf", "segoeuib.ttf", "consolab.ttf"):
        if not (args.font_dir / filename).is_file():
            parser.error(f"Required font not found: {args.font_dir / filename}")
    output_dir = Path(__file__).resolve().parents[1] / "static" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    render_brand(args.font_dir, output_dir / "og-local-ai.png")
    render_dataset_report(args.font_dir, output_dir / "og-hf-datasets-cache-wsl2.png")


if __name__ == "__main__":
    main()
