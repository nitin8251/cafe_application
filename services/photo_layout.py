from dataclasses import dataclass
from io import BytesIO
from math import floor
from pathlib import Path
from collections import deque
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps


DPI = 300
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
PAGE_MARGIN_MM = 10
GAP_MM = 4
BACKGROUND_MAP = {
    "White background": (255, 255, 255),
    "Blue background": (140, 186, 255),
}
CUT_BORDER_COLOR = (0, 0, 0)
CUT_BORDER_WIDTH = 2
TEXT_STRIP_RATIO = 0.18
TEXT_STRIP_PADDING = 8
TEXT_STRIP_GAP = 3


def _mm_to_px(mm: float) -> int:
    return max(1, round((mm / 25.4) * DPI))


@dataclass
class GeneratedUpload:
    name: str
    _content: bytes
    type: str = "image/jpeg"

    @property
    def size(self) -> int:
        return len(self._content)

    def getvalue(self) -> bytes:
        return self._content


def get_sheet_capacity(size_config: dict) -> dict:
    photo_width_px = _mm_to_px(float(size_config["width_mm"]))
    photo_height_px = _mm_to_px(float(size_config["height_mm"]))
    page_width_px = _mm_to_px(A4_WIDTH_MM)
    page_height_px = _mm_to_px(A4_HEIGHT_MM)
    margin_px = _mm_to_px(PAGE_MARGIN_MM)
    gap_px = _mm_to_px(GAP_MM)

    usable_width = page_width_px - (2 * margin_px)
    usable_height = page_height_px - (2 * margin_px)
    columns = max(1, floor((usable_width + gap_px) / (photo_width_px + gap_px)))
    rows = max(1, floor((usable_height + gap_px) / (photo_height_px + gap_px)))
    capacity = max(1, columns * rows)

    return {
        "columns": columns,
        "rows": rows,
        "capacity": capacity,
        "photo_width_px": photo_width_px,
        "photo_height_px": photo_height_px,
        "page_width_px": page_width_px,
        "page_height_px": page_height_px,
        "margin_px": margin_px,
        "gap_px": gap_px,
    }


def _estimate_background_color(source: Image.Image) -> tuple[int, int, int]:
    width, height = source.size
    sample_points = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
        (width // 2, 0),
        (width // 2, height - 1),
        (0, height // 2),
        (width - 1, height // 2),
    ]
    reds, greens, blues = [], [], []
    pixels = source.load()
    for x, y in sample_points:
        red, green, blue = pixels[x, y]
        reds.append(red)
        greens.append(green)
        blues.append(blue)
    return (
        round(sum(reds) / len(reds)),
        round(sum(greens) / len(greens)),
        round(sum(blues) / len(blues)),
    )


def _within_threshold(pixel: tuple[int, int, int], target: tuple[int, int, int], threshold: int) -> bool:
    return sum(abs(channel - target_channel) for channel, target_channel in zip(pixel, target)) <= threshold


def apply_background_finish(source: Image.Image, finish: str) -> Image.Image:
    background_color = BACKGROUND_MAP.get(finish)
    if not background_color:
        return source

    image = source.convert("RGB")
    width, height = image.size
    pixels = image.load()
    target = _estimate_background_color(image)
    threshold = 105
    queue = deque()
    visited = set()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if not _within_threshold(pixels[x, y], target, threshold):
            continue

        pixels[x, y] = background_color
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    return image


def _encode_jpeg_to_target(image: Image.Image, target_size_kb: int | None = None) -> bytes:
    quality_steps = [95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35]
    target_bytes = int(target_size_kb * 1024) if target_size_kb else 0
    best_bytes = b""

    for quality in quality_steps:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        encoded = buffer.getvalue()
        best_bytes = encoded
        if target_bytes and len(encoded) <= target_bytes:
            return encoded

    return best_bytes


def _encode_pdf(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PDF", resolution=DPI)
    return buffer.getvalue()


def _draw_cut_border(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    draw.rectangle(
        (
            x,
            y,
            x + width - 1,
            y + height - 1,
        ),
        outline=CUT_BORDER_COLOR,
        width=CUT_BORDER_WIDTH,
    )


def _build_caption_lines(caption: dict | None) -> list[str]:
    if not caption or not caption.get("enabled"):
        return []

    lines = []
    name = str(caption.get("name", "")).strip()
    dob = str(caption.get("dob", "")).strip()
    dop = str(caption.get("dop", "")).strip()
    if name:
        lines.append(name.upper())
    if dob:
        lines.append(f"DOB: {dob}")
    if dop:
        lines.append(f"DOP: {dop}")
    return lines


def _font_candidates(primary: bool) -> list[str]:
    windows_dir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = Path(windows_dir) / "Fonts"
    return [
        str(fonts_dir / "arialbd.ttf") if primary else str(fonts_dir / "arial.ttf"),
        str(fonts_dir / "calibrib.ttf") if primary else str(fonts_dir / "calibri.ttf"),
        "arialbd.ttf" if primary else "arial.ttf",
        "DejaVuSans-Bold.ttf" if primary else "DejaVuSans.ttf",
    ]


def _load_font_candidate(candidate: str, size: int) -> ImageFont.ImageFont | None:
    try:
        return ImageFont.truetype(candidate, size=size)
    except OSError:
        return None


def _fit_caption_font(draw: ImageDraw.ImageDraw, text: str, width: int, primary: bool) -> ImageFont.ImageFont:
    max_size = max(18, min(42, width // (8 if primary else 10)))
    min_size = 14 if primary else 12
    allowed_width = max(40, width - (TEXT_STRIP_PADDING * 2))

    for size in range(max_size, min_size - 1, -1):
        for candidate in _font_candidates(primary):
            font = _load_font_candidate(candidate, size)
            if font is None:
                continue
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= allowed_width:
                return font

    return ImageFont.load_default()


def _render_captioned_photo(fitted: Image.Image, caption: dict | None) -> Image.Image:
    lines = _build_caption_lines(caption)
    if not lines:
        return fitted

    width, height = fitted.size
    measurement = Image.new("RGB", (width, max(50, int(height * TEXT_STRIP_RATIO))), "white")
    measure_draw = ImageDraw.Draw(measurement)
    text_heights = []
    fonts = []
    for index, line in enumerate(lines):
        font = _fit_caption_font(measure_draw, line, width, primary=index == 0)
        fonts.append(font)
        bbox = measure_draw.textbbox((0, 0), line, font=font)
        text_heights.append(bbox[3] - bbox[1])

    strip_height = max(
        58,
        sum(text_heights) + (max(0, len(lines) - 1) * TEXT_STRIP_GAP) + (TEXT_STRIP_PADDING * 2),
    )
    canvas = Image.new("RGB", (width, height + strip_height), "white")
    canvas.paste(fitted, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, height, width - 1, height + strip_height - 1), fill="white")
    draw.line((0, height, width - 1, height), fill=(45, 45, 45), width=1)

    total_text_height = sum(text_heights) + (max(0, len(lines) - 1) * TEXT_STRIP_GAP)
    current_y = height + max(TEXT_STRIP_PADDING, (strip_height - total_text_height) // 2)
    for index, line in enumerate(lines):
        font = fonts[index]
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = max(TEXT_STRIP_PADDING, (width - text_width) // 2)
        draw.text((text_x, current_y), line, fill="black", font=font)
        current_y += text_height + TEXT_STRIP_GAP

    return canvas


def build_photo_sheet(
    uploaded_file,
    size_name: str,
    size_config: dict,
    photo_count: int,
    finish: str = "Original",
    output_format: str = "JPG",
    target_size_kb: int | None = None,
    caption: dict | None = None,
) -> tuple[GeneratedUpload, bytes, dict]:
    source = Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")
    source = apply_background_finish(source, finish)
    layout = get_sheet_capacity(size_config)

    base_photo_height = layout["photo_height_px"]
    caption_lines = _build_caption_lines(caption)
    caption_height = max(32, int(base_photo_height * TEXT_STRIP_RATIO)) if caption_lines else 0
    image_height = base_photo_height - caption_height if caption_height else base_photo_height
    fitted = ImageOps.fit(
        source,
        (layout["photo_width_px"], image_height),
        method=Image.Resampling.LANCZOS,
    )
    fitted = _render_captioned_photo(fitted, caption)
    page = Image.new("RGB", (layout["page_width_px"], layout["page_height_px"]), "white")
    draw = ImageDraw.Draw(page)
    copies_to_place = min(photo_count, layout["capacity"])

    for index in range(copies_to_place):
        row = index // layout["columns"]
        col = index % layout["columns"]
        x = layout["margin_px"] + col * (layout["photo_width_px"] + layout["gap_px"])
        y = layout["margin_px"] + row * (layout["photo_height_px"] + layout["gap_px"])
        page.paste(fitted, (x, y))
        _draw_cut_border(draw, x, y, layout["photo_width_px"], layout["photo_height_px"])

    preview_bytes = _encode_jpeg_to_target(page)
    normalized_format = output_format.strip().upper()
    if normalized_format == "PDF":
        generated_bytes = _encode_pdf(page)
        mime_type = "application/pdf"
        extension = "pdf"
    else:
        generated_bytes = _encode_jpeg_to_target(page, target_size_kb)
        mime_type = "image/jpeg"
        extension = "jpg"

    suffix = Path(uploaded_file.name).stem
    file_name = f"{suffix}_{size_name.replace(' ', '_').replace('/', '_')}_sheet.{extension}"
    layout["copies_rendered"] = copies_to_place
    layout["finish"] = finish
    layout["output_format"] = normalized_format
    layout["generated_size_kb"] = round(len(generated_bytes) / 1024, 2)
    layout["target_size_kb"] = target_size_kb or 0
    layout["caption_enabled"] = bool(caption_lines)
    return GeneratedUpload(file_name, generated_bytes, type=mime_type), preview_bytes, layout


def build_single_photo_document(
    uploaded_file,
    size_name: str,
    size_config: dict,
    finish: str = "Original",
    output_format: str = "JPG",
    target_size_kb: int | None = None,
) -> tuple[GeneratedUpload, bytes, dict]:
    source = Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")
    source = apply_background_finish(source, finish)

    width_px = _mm_to_px(float(size_config["width_mm"]))
    height_px = _mm_to_px(float(size_config["height_mm"]))
    fitted = ImageOps.fit(
        source,
        (width_px, height_px),
        method=Image.Resampling.LANCZOS,
    )

    normalized_format = output_format.strip().upper()
    preview_bytes = _encode_jpeg_to_target(fitted)
    if normalized_format == "PDF":
        generated_bytes = _encode_pdf(fitted)
        mime_type = "application/pdf"
        extension = "pdf"
    else:
        generated_bytes = _encode_jpeg_to_target(fitted, target_size_kb)
        mime_type = "image/jpeg"
        extension = "jpg"

    file_name = f"{Path(uploaded_file.name).stem}_{size_name.replace(' ', '_').replace('/', '_')}.{extension}"
    summary = {
        "width_px": width_px,
        "height_px": height_px,
        "finish": finish,
        "output_format": normalized_format,
        "generated_size_kb": round(len(generated_bytes) / 1024, 2),
        "target_size_kb": target_size_kb or 0,
    }
    return GeneratedUpload(file_name, generated_bytes, type=mime_type), preview_bytes, summary


def build_images_to_pdf(uploaded_files: list) -> tuple[GeneratedUpload, bytes, dict]:
    pages = [Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB") for uploaded_file in uploaded_files]
    pdf_buffer = BytesIO()
    first_page, *other_pages = pages
    first_page.save(pdf_buffer, format="PDF", save_all=True, append_images=other_pages, resolution=DPI)
    pdf_bytes = pdf_buffer.getvalue()
    file_name = f"{Path(uploaded_files[0].name).stem}_images_to_pdf.pdf" if uploaded_files else "images_to_pdf.pdf"
    preview_bytes = _encode_jpeg_to_target(first_page)
    summary = {
        "page_count": len(pages),
        "generated_size_kb": round(len(pdf_bytes) / 1024, 2),
    }
    return GeneratedUpload(file_name, pdf_bytes, type="application/pdf"), preview_bytes, summary


def build_merged_photo_document(
    photo_orders: list[dict],
    size_name: str,
    size_config: dict,
) -> tuple[GeneratedUpload, bytes, dict]:
    layout = get_sheet_capacity(size_config)
    page_images: list[Image.Image] = []
    current_page = Image.new("RGB", (layout["page_width_px"], layout["page_height_px"]), "white")
    draw = ImageDraw.Draw(current_page)
    slot_index = 0
    total_photos = 0

    for order in photo_orders:
        source_file_path = order.get("source_file_path")
        if not source_file_path or not Path(source_file_path).is_file():
            continue

        service_meta = order.get("service_meta", {})
        finish = service_meta.get("photo_finish", "Original")
        source = Image.open(source_file_path).convert("RGB")
        source = apply_background_finish(source, finish)
        fitted = ImageOps.fit(
            source,
            (layout["photo_width_px"], layout["photo_height_px"]),
            method=Image.Resampling.LANCZOS,
        )

        for _ in range(max(1, int(order.get("copies", 1)))):
            if slot_index and slot_index % layout["capacity"] == 0:
                page_images.append(current_page)
                current_page = Image.new("RGB", (layout["page_width_px"], layout["page_height_px"]), "white")
                draw = ImageDraw.Draw(current_page)
                slot_index = 0

            row = slot_index // layout["columns"]
            col = slot_index % layout["columns"]
            x = layout["margin_px"] + col * (layout["photo_width_px"] + layout["gap_px"])
            y = layout["margin_px"] + row * (layout["photo_height_px"] + layout["gap_px"])
            current_page.paste(fitted, (x, y))
            _draw_cut_border(draw, x, y, layout["photo_width_px"], layout["photo_height_px"])
            slot_index += 1
            total_photos += 1

    if slot_index or not page_images:
        page_images.append(current_page)

    pdf_buffer = BytesIO()
    first_page, *other_pages = page_images
    first_page.save(
        pdf_buffer,
        format="PDF",
        save_all=True,
        append_images=other_pages,
        resolution=DPI,
    )
    pdf_bytes = pdf_buffer.getvalue()
    file_name = f"merged_{size_name.replace(' ', '_').replace('/', '_')}_photo_orders.pdf"
    summary = {
        "orders_merged": len(photo_orders),
        "total_photos": total_photos,
        "page_count": len(page_images),
        "capacity_per_page": layout["capacity"],
        "photo_size_name": size_name,
    }
    return GeneratedUpload(file_name, pdf_bytes, type="application/pdf"), pdf_bytes, summary
