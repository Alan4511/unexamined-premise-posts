#!/usr/bin/env python3
"""Render a typeset 1080x1350 Instagram carousel from slides.json.

Dependencies: Pillow (PIL). Does not publish or upload the result.
"""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

SIGNATURE_TEXT = "A second thought, not a final answer."
OPENING_EYEBROW = "THE QUESTION"
COUNTERPOINT_EYEBROW = "THE COUNTERPOINT"
LANDING_EYEBROW = "WHERE IT LEAVES US"
SIGNATURE_ALT = "Closing reflection slide titled A second thought, not a final answer. "
BRAND_NAME = "UNEXAMINED PREMISE"
DISPLAY_BRAND = "THE UNEXAMINED PREMISE"
CAPTION_BRAND = "THE UNEXAMINED PREMISE"


def caption_heading(post_number: int) -> str:
    return f"{CAPTION_BRAND} · {post_number:03d}"
ALLOWED_LAYOUTS = ("standard", "statement", "contrast", "annotation")


def signature_slide(reflection: str) -> dict[str, str]:
    """One identity-locked conclusion with a unique editorial reflection."""
    return {"type": "signature", "eyebrow": "", "headline": SIGNATURE_TEXT,
            "body": reflection, "alt": SIGNATURE_ALT + reflection}


W, H = 1080, 1350
BG = "#F3F0E9"
INK = "#282822"
MUTED = "#77736D"
ACCENT = "#AD715C"
RULE = "#D8D4CB"
MARGIN = 80

FONT_FAMILIES = {
    "serif": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
}


def font(size: int, family: str = "sans") -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_FAMILIES[family]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def text_width(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.ImageFont) -> float:
    return draw.textbbox((0, 0), text, font=f)[2]


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.ImageFont, width: int) -> list[str]:
    all_lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            all_lines.append("")
            continue
        line = ""
        for word in paragraph.split():
            candidate = word if not line else f"{line} {word}"
            if text_width(draw, candidate, f) <= width:
                line = candidate
                continue
            if line:
                all_lines.append(line)
                line = ""
            if text_width(draw, word, f) > width:
                raise ValueError(f"Unbreakable word too wide for slide: {word[:32]}")
            line = word
        if line:
            all_lines.append(line)
    return all_lines


def fitted(draw: ImageDraw.ImageDraw, text: str, family: str, max_size: int,
           min_size: int, width: int, max_height: int, spacing_ratio: float = 1.2):
    for size in range(max_size, min_size - 1, -2):
        f = font(size, family)
        lines = wrap(draw, text, f, width)
        advance = round(size * spacing_ratio)
        total_h = len(lines) * advance
        if total_h <= max_height:
            return f, lines, advance, total_h
    raise ValueError(
        f"Slide text does not fit without becoming unreadable: {text[:90]!r}. "
        "Shorten it, split it into two slides, or reduce the number of paragraphs."
    )


def draw_lines(draw: ImageDraw.ImageDraw, lines: list[str], x: int, y: int,
               f: ImageFont.ImageFont, advance: int, fill: str):
    for line in lines:
        if line:
            draw.text((x, y), line, font=f, fill=fill, anchor="lt")
        y += advance
    return y


def load_slides(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or not isinstance(obj.get("slides"), list):
        raise ValueError("Input must be a JSON object with a slides array")
    if not (4 <= len(obj["slides"]) <= 9):
        raise ValueError("Expect 4–9 narrative slides; the total includes one automatic signature slide")
    post_number = obj.get("post_number")
    if type(post_number) is not int or not (1 <= post_number <= 999):
        raise ValueError("post_number must be an integer from 1 to 999, assigned from publication history")
    reflection = obj.get("closing_reflection")
    if not isinstance(reflection, str) or not (20 <= len(reflection.split()) <= 55):
        raise ValueError("closing_reflection requires 20–55 original words specific to this discussion")
    if SIGNATURE_TEXT.casefold() in reflection.casefold():
        raise ValueError("closing_reflection must not repeat the signature heading")
    if obj.get("brand", BRAND_NAME) != BRAND_NAME:
        raise ValueError("This account requires brand UNEXAMINED PREMISE")
    for i, slide in enumerate(obj["slides"], 1):
        if not isinstance(slide, dict):
            raise ValueError(f"Slide {i} is not an object")
        for key in ("eyebrow", "headline", "body", "alt"):
            if not isinstance(slide.get(key), str):
                raise ValueError(f"Slide {i}: {key} must be a string")
        if not slide["headline"].strip():
            raise ValueError(f"Slide {i}: headline must not be empty")
        if slide.get("layout", "standard") not in ALLOWED_LAYOUTS:
            raise ValueError(f"Slide {i}: unknown layout; expected one of {ALLOWED_LAYOUTS}")
        if not slide["alt"].strip():
            raise ValueError(f"Slide {i}: alt text must not be empty")
        if slide.get("type") == "signature" or any(SIGNATURE_TEXT.casefold() in slide[field].casefold() for field in ("eyebrow", "headline", "body")):
            raise ValueError("Do not author the signature phrase inside narrative slides: it is added exactly once by the renderer")
    narrative = obj["slides"]
    if narrative[0]["eyebrow"].strip() != OPENING_EYEBROW:
        raise ValueError(f"First narrative slide eyebrow must be {OPENING_EYEBROW}")
    if narrative[-1]["eyebrow"].strip() != LANDING_EYEBROW:
        raise ValueError(f"Last narrative slide eyebrow must be {LANDING_EYEBROW}")
    count_counterpoint = sum(slide["eyebrow"].strip() == COUNTERPOINT_EYEBROW for slide in narrative[1:-1])
    if count_counterpoint != 1:
        raise ValueError(f"Exactly one intermediate {COUNTERPOINT_EYEBROW} slide is required")
    obj["slides"].append(signature_slide(reflection.strip()))
    return obj


def render_signature_slide(path: Path, reflection: str) -> None:
    """Fixed editorial typography and spacing; unique, source-grounded final paragraph."""
    if not (20 <= len(reflection.split()) <= 55):
        raise ValueError("Closing reflection must be 20–55 words")
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((MARGIN, 102, MARGIN + 58, 113), fill=ACCENT)
    brand_f = font(25, "sans")
    d.text((MARGIN + 81, 93), DISPLAY_BRAND, font=brand_f, fill=MUTED, anchor="lt")
    d.line((MARGIN, 155, W - MARGIN, 155), fill=RULE, width=2)
    d.text((MARGIN, 300), "A REFLECTION, NOT A VERDICT", font=font(24), fill=ACCENT, anchor="lt")

    # The full recurring phrase is a large, actual headline, not an eyebrow.
    heading_font, heading_lines, heading_advance, _ = fitted(
        d, SIGNATURE_TEXT, "serif", 62, 50, W - 2 * MARGIN, 250, 1.4)
    heading_bottom = draw_lines(d, heading_lines, MARGIN, 382,
                                heading_font, heading_advance, INK)
    d.line((MARGIN, heading_bottom + 35, MARGIN + 84, heading_bottom + 35),
           fill=ACCENT, width=4)
    reflection_y = heading_bottom + 100
    body_font, body_lines, advance, _ = fitted(
        d, reflection, "sans", 35, 27, W - 2 * MARGIN, 1050 - reflection_y, 1.55)
    draw_lines(d, body_lines, MARGIN, reflection_y, body_font, advance, MUTED)
    d.line((MARGIN, 1183, W - MARGIN, 1183), fill=RULE, width=2)
    handle_font = font(23, "sans")
    handle = "@unexaminedpremise"
    d.text(((W - text_width(d, handle, handle_font)) // 2, 1220),
           handle, font=handle_font, fill=MUTED, anchor="lt")
    im.save(path, format="PNG", optimize=True)


def render_slide(slide: dict[str, str], idx: int, total: int, brand: str, path: Path, post_number: int = 1) -> None:
    if slide.get("type") == "signature":
        render_signature_slide(path, slide["body"])
        return
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    fw = W - 2 * MARGIN

    # Brand line + minimal accent anchor
    d.rectangle((MARGIN, 102, MARGIN + 58, 113), fill=ACCENT)
    brand_f = font(25, "sans")
    if text_width(d, DISPLAY_BRAND, brand_f) > fw - 100:
        brand_f = font(19, "sans")
    d.text((MARGIN + 81, 93), DISPLAY_BRAND, font=brand_f, fill=MUTED, anchor="lt")
    d.line((MARGIN, 155, W - MARGIN, 155), fill=RULE, width=2)

    layout = slide.get("layout", "standard")
    eyebrow = slide["eyebrow"].upper()
    eyebrow_f = font(25, "sans")
    eyebrow_y = 265 if layout == "statement" else 276
    d.text((MARGIN, eyebrow_y), eyebrow[:66], font=eyebrow_f, fill=ACCENT, anchor="lt")
    if layout == "annotation":
        d.rectangle((MARGIN, 350, MARGIN + 5, 1085), fill=ACCENT)
    elif layout == "contrast":
        d.line((MARGIN, 690, W - MARGIN, 690), fill=RULE, width=3)
        d.rectangle((MARGIN, 688, MARGIN + 67, 693), fill=ACCENT)

    # Content uses two fixed height budgets to guarantee readable spacing.
    headline_max = 620 if not slide["body"].strip() else (310 if layout == "contrast" else 488)
    headline_start = {"standard": 355, "statement": 445, "contrast": 342, "annotation": 385}[layout]
    headline_size = {"standard": 78 if idx == 1 else 67,
                     "statement": 88 if idx == 1 else 79,
                     "contrast": 68, "annotation": 60}[layout]
    headline_font, headline_lines, hl_advance, headline_h = fitted(
        d, slide["headline"], "serif", headline_size,
        40, fw, headline_max, 1.27
    )
    y_after_head = draw_lines(d, headline_lines, MARGIN + (30 if layout == "annotation" else 0), headline_start,
                              headline_font, hl_advance, INK)

    body = slide["body"].strip()
    if body:
        body_y = (745 if layout == "contrast" else
                  max(y_after_head + (90 if layout == "statement" else 55),
                      800 if layout == "statement" else (730 if idx == 1 else 700)))
        body_h_budget = 1090 - body_y
        if body_h_budget <= 70:
            raise ValueError("Insufficient space for body; shorten headline")
        body_font, lines, advance, _ = fitted(
            d, body, "sans", 38, 27, fw - 18,
            body_h_budget, 1.47
        )
        draw_lines(d, lines, MARGIN + (30 if layout == "annotation" else 0), body_y, body_font, advance, MUTED)

    # Footer and slide progress
    d.line((MARGIN, 1183, W - MARGIN, 1183), fill=RULE, width=2)
    d.text((MARGIN, 1220), f"UNFINISHED ARGUMENT {post_number:03d}", font=font(20), fill=MUTED, anchor="lt")
    page_label = f"{idx:02d} / {total:02d}"
    page_font = font(21)
    page_x = W - MARGIN - text_width(d, page_label, page_font)
    d.text((page_x, 1220), page_label, font=page_font, fill=ACCENT, anchor="lt")

    im.save(path, format="PNG", optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Slides JSON")
    parser.add_argument("--outdir", type=Path, required=True, help="Output directory")
    args = parser.parse_args()
    source = load_slides(args.input)
    slides = source["slides"]
    args.outdir.mkdir(parents=True, exist_ok=True)
    brand = BRAND_NAME
    exported = []
    for idx, slide in enumerate(slides, 1):
        dest = args.outdir / f"slide-{idx:02d}.png"
        render_slide(slide, idx, len(slides), brand, dest, source["post_number"])
        exported.append({"index": idx, "filename": dest.name, "type": slide.get("type", "content"),
                         "alt": slide["alt"],
                         "sha256": hashlib.sha256(dest.read_bytes()).hexdigest()})
        print(f"Rendered {dest}")
    (args.outdir / "manifest.json").write_text(
        json.dumps({"brand": brand, "post_number": source["post_number"],
                    "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
                    "slides": exported}, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
