from __future__ import annotations

from typing import Callable, Dict, List


class ModuleRegistry:
    def __init__(self) -> None:
        self.modules: Dict[str, dict] = {}
        self.pages: Dict[str, dict] = {}

    def register_module(self, module_info: dict) -> None:
        name = module_info.get("name")
        if not name:
            raise ValueError("Module info must include a name.")
        self.modules[name] = module_info

    def register_page(self, page_name: str, page_handler: Callable[[dict], None], module_name: str = "Core") -> None:
        self.pages[page_name] = {
            "handler": page_handler,
            "module": module_name,
        }

    def get_page_handler(self, page_name: str) -> Callable[[dict], None] | None:
        page = self.pages.get(page_name)
        return page["handler"] if page else None

    def list_pages(self) -> List[str]:
        return list(self.pages.keys())


module_registry = ModuleRegistry()
