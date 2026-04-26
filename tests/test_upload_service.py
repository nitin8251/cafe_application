import unittest
from io import BytesIO

from PIL import Image

from components.service_form import prepare_uploaded_document
from services.upload_service import _price_for_upload, _safe_file_name, _storage_file_name
from pages.upload_page import _multiplier_price, _slab_price


class DummyImageUpload:
    def __init__(self, name: str = "proof.jpg", mime_type: str = "image/jpeg"):
        image = Image.new("RGB", (500, 500), color="white")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        self._content = buffer.getvalue()
        self.name = name
        self.type = mime_type

    @property
    def size(self) -> int:
        return len(self._content)

    def getvalue(self) -> bytes:
        return self._content


class UploadServiceTests(unittest.TestCase):
    def test_safe_file_name_normalizes_spaces(self):
        self.assertEqual(_safe_file_name("My File.PDF"), "My_File.pdf")

    def test_safe_file_name_keeps_extension(self):
        self.assertEqual(_safe_file_name("passport photo.JPG"), "passport_photo.jpg")

    def test_storage_file_name_uses_customer_pickup_and_label(self):
        renamed = _storage_file_name("Nitin Kumar", "ADS-ABC123", "Aadhaar Card", "scan.JPG")
        self.assertEqual(renamed, "Nitin_Kumar_ADS-ABC123_Aadhaar_Card.jpg")

    def test_price_for_upload_applies_express_markup(self):
        regular = _price_for_upload({"unit_price": 10, "copies": 2, "urgent": False})
        express = _price_for_upload({"unit_price": 10, "copies": 2, "urgent": True})
        self.assertEqual(regular, 20.0)
        self.assertEqual(express, 25.0)

    def test_slab_price_scales_by_each_thousand(self):
        self.assertEqual(_slab_price(1000, 1000, 20), 20.0)
        self.assertEqual(_slab_price(2000, 1000, 20), 40.0)
        self.assertEqual(_slab_price(3000, 1000, 20), 60.0)
        self.assertEqual(_slab_price(2500, 1000, 20), 60.0)

    def test_multiplier_price_scales_by_units(self):
        self.assertEqual(_multiplier_price(1, 500), 500.0)
        self.assertEqual(_multiplier_price(3, 500), 1500.0)
        self.assertEqual(_multiplier_price(12, 15), 180.0)

    def test_prepare_uploaded_document_can_convert_image_to_pdf(self):
        upload = DummyImageUpload()
        prepared = prepare_uploaded_document(upload, convert_image_to_pdf=True)
        self.assertTrue(prepared.name.endswith(".pdf"))
        self.assertEqual(prepared.type, "application/pdf")
        self.assertGreater(prepared.size, 0)

    def test_prepare_uploaded_document_can_target_image_size(self):
        upload = DummyImageUpload()
        prepared = prepare_uploaded_document(upload, target_size_kb=60)
        self.assertTrue(prepared.name.endswith(".jpg"))
        self.assertEqual(prepared.type, "image/jpeg")
        self.assertGreater(prepared.size, 0)


if __name__ == "__main__":
    unittest.main()
