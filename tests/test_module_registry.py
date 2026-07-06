import unittest

from modules.registry import module_registry, ModuleRegistry


class ModuleRegistryTest(unittest.TestCase):
    def test_register_and_retrieve_page(self):
        registry = ModuleRegistry()
        registry.register_module({"name": "Test", "description": "Test module"})

        def dummy_page(actor):
            return None

        registry.register_page("Dummy Page", dummy_page, module_name="Test")
        self.assertEqual(registry.get_page_handler("Dummy Page").__name__, "dummy_page")
        self.assertIn("Dummy Page", registry.list_pages())


if __name__ == "__main__":
    unittest.main()
