import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from services.photo_layout import (
    apply_background_finish,
    build_images_to_pdf,
    build_merged_photo_document,
    build_photo_sheet,
    get_sheet_capacity,
)


class DummyUpload:
    def __init__(self, name: str = "portrait.jpg"):
        image = Image.new("RGB", (1200, 1600), color="navy")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        self._content = buffer.getvalue()
        self.name = name

    def getvalue(self) -> bytes:
        return self._content


class PhotoLayoutTests(unittest.TestCase):
    def setUp(self):
        self.passport_config = {
            "width_mm": 35,
            "height_mm": 45,
        }

    def test_sheet_capacity_is_positive(self):
        layout = get_sheet_capacity(self.passport_config)
        self.assertGreater(layout["capacity"], 0)
        self.assertGreater(layout["columns"], 0)
        self.assertGreater(layout["rows"], 0)

    def test_photo_sheet_limits_to_capacity(self):
        upload = DummyUpload()
        generated, sheet_bytes, layout = build_photo_sheet(
            upload,
            "Passport (35x45 mm)",
            self.passport_config,
            photo_count=999,
        )
        self.assertTrue(generated.name.endswith("_sheet.jpg"))
        self.assertGreater(len(sheet_bytes), 0)
        self.assertLessEqual(layout["copies_rendered"], layout["capacity"])

    def test_photo_sheet_uses_requested_copy_count_when_possible(self):
        upload = DummyUpload()
        _, _, layout = build_photo_sheet(
            upload,
            "Passport (35x45 mm)",
            self.passport_config,
            photo_count=8,
        )
        self.assertEqual(layout["copies_rendered"], 8)

    def test_background_finish_replaces_border_color_only(self):
        image = Image.new("RGB", (40, 40), "white")
        for x in range(10, 30):
            for y in range(10, 30):
                image.putpixel((x, y), (210, 40, 40))

        changed = apply_background_finish(image, "Blue background")
        self.assertEqual(changed.getpixel((0, 0)), (140, 186, 255))
        self.assertEqual(changed.getpixel((20, 20)), (210, 40, 40))

    def test_photo_sheet_records_finish(self):
        upload = DummyUpload()
        _, _, layout = build_photo_sheet(
            upload,
            "Passport (35x45 mm)",
            self.passport_config,
            photo_count=4,
            finish="White background",
        )
        self.assertEqual(layout["finish"], "White background")

    def test_photo_sheet_draws_black_cut_borders(self):
        upload = DummyUpload()
        _, sheet_bytes, layout = build_photo_sheet(
            upload,
            "Passport (35x45 mm)",
            self.passport_config,
            photo_count=1,
        )
        sheet = Image.open(BytesIO(sheet_bytes)).convert("RGB")
        border_pixel = sheet.getpixel((layout["margin_px"], layout["margin_px"]))
        self.assertLess(sum(border_pixel), 80)

    def test_photo_sheet_can_output_pdf(self):
        upload = DummyUpload()
        generated, _, layout = build_photo_sheet(
            upload,
            "Passport (35x45 mm)",
            self.passport_config,
            photo_count=4,
            output_format="PDF",
        )
        self.assertEqual(generated.type, "application/pdf")
        self.assertTrue(generated.name.endswith(".pdf"))
        self.assertEqual(layout["output_format"], "PDF")

    def test_photo_sheet_can_include_optional_caption_strip(self):
        upload = DummyUpload()
        _, _, layout = build_photo_sheet(
            upload,
            "Passport (35x45 mm)",
            self.passport_config,
            photo_count=2,
            caption={
                "enabled": True,
                "name": "NAME-XYZ",
                "dob": "26/03/2001",
                "dop": "26/03/2021",
            },
        )
        self.assertTrue(layout["caption_enabled"])

    def test_images_to_pdf_builds_pdf(self):
        upload_one = DummyUpload("one.jpg")
        upload_two = DummyUpload("two.jpg")
        generated, preview_bytes, summary = build_images_to_pdf([upload_one, upload_two])
        self.assertEqual(generated.type, "application/pdf")
        self.assertTrue(generated.name.endswith(".pdf"))
        self.assertGreater(len(preview_bytes), 0)
        self.assertEqual(summary["page_count"], 2)

    def test_merged_photo_document_builds_pdf(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first_path = Path(temp_dir) / "one.jpg"
            second_path = Path(temp_dir) / "two.jpg"
            Image.new("RGB", (1200, 1600), color="navy").save(first_path, format="JPEG")
            Image.new("RGB", (1200, 1600), color="darkgreen").save(second_path, format="JPEG")

            generated, merged_bytes, summary = build_merged_photo_document(
                [
                    {
                        "source_file_path": str(first_path),
                        "copies": 4,
                        "service_meta": {"photo_finish": "Original"},
                    },
                    {
                        "source_file_path": str(second_path),
                        "copies": 5,
                        "service_meta": {"photo_finish": "White background"},
                    },
                ],
                "Passport (35x45 mm)",
                self.passport_config,
            )

            self.assertTrue(generated.name.endswith(".pdf"))
            self.assertEqual(generated.type, "application/pdf")
            self.assertGreater(len(merged_bytes), 0)
            self.assertEqual(summary["orders_merged"], 2)
            self.assertEqual(summary["total_photos"], 9)


if __name__ == "__main__":
    unittest.main()
