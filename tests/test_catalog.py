import unittest

from services.catalog import get_photo_size_options, get_photo_sizes, get_service_catalog


class CatalogTests(unittest.TestCase):
    def test_service_catalog_contains_core_services(self):
        catalog = get_service_catalog()
        self.assertIn("Document Print / Xerox", catalog)
        self.assertIn("Aadhaar Address Update", catalog)
        self.assertIn("Electricity Bill Payment", catalog)
        self.assertIn("Passport Photo Print", catalog)

    def test_service_catalog_supports_variants_and_optional_uploads(self):
        catalog = get_service_catalog()
        pan_card = catalog["PAN Card"]
        bill_payment = catalog["Electricity Bill Payment"]
        self.assertTrue(pan_card.get("variants"))
        self.assertFalse(bill_payment.get("upload_required", True))

    def test_service_catalog_includes_checklists_for_service_desk_items(self):
        catalog = get_service_catalog()
        self.assertTrue(catalog["Aadhaar Address Update"].get("checklist"))
        self.assertTrue(catalog["Government Exam Form"].get("checklist"))

    def test_document_print_service_supports_file_color_modes(self):
        catalog = get_service_catalog()
        document_print = catalog["Document Print / Xerox"]
        self.assertTrue(document_print.get("show_print_style"))
        self.assertTrue(document_print.get("show_color_mode"))
        self.assertEqual(len(document_print.get("color_modes", [])), 2)

    def test_photo_size_options_include_dimensions(self):
        options = get_photo_size_options()
        self.assertTrue(any(name == "Passport (35x45 mm)" for name, _, _ in options))
        passport = next(label for name, label, _ in options if name == "Passport (35x45 mm)")
        self.assertIn("35", passport)
        self.assertIn("45", passport)

    def test_photo_sizes_have_geometry(self):
        photo_sizes = get_photo_sizes()
        for config in photo_sizes.values():
            self.assertIn("width_mm", config)
            self.assertIn("height_mm", config)


if __name__ == "__main__":
    unittest.main()
