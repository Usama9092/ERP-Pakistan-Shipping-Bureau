import unittest

from maritime_module import (
    build_theme_css,
    calculate_completion_percentage,
    get_project_config,
    normalize_checklist_item,
    sanitize_text_input,
)


class MaritimeModuleTests(unittest.TestCase):
    def test_project_config_contains_required_keys(self):
        config = get_project_config()
        self.assertIn("project_name", config)
        self.assertIn("version", config)
        self.assertIn("modules", config)

    def test_completion_percentage_caps_between_zero_and_hundred(self):
        self.assertEqual(calculate_completion_percentage(3, 10), 30)
        self.assertEqual(calculate_completion_percentage(12, 10), 100)
        self.assertEqual(calculate_completion_percentage(-1, 10), 0)

    def test_sanitize_text_input_strips_html_and_trim(self):
        value = sanitize_text_input("  <script>alert(1)</script> Hello  ")
        self.assertEqual(value, "Hello")

    def test_normalize_checklist_item_returns_expected_fields(self):
        item = normalize_checklist_item({"section": "Safety", "subsection": "Fire", "checklist_item": "Extinguishers"})
        self.assertEqual(item["section"], "Safety")
        self.assertEqual(item["status"], "Pending")
        self.assertEqual(item["completion_pct"], 0)

    def test_build_theme_css_contains_theme_specific_tokens(self):
        dark_css = build_theme_css("dark")
        light_css = build_theme_css("light")
        self.assertIn("color-scheme: dark", dark_css)
        self.assertIn("color-scheme: light", light_css)
        self.assertIn(".theme-shell", dark_css)
        self.assertIn(".theme-card", light_css)
        self.assertIn("--psb-surface", dark_css)
        self.assertIn("--psb-surface-alt", light_css)


if __name__ == "__main__":
    unittest.main()
