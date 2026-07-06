from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Callable

from .registry import ModuleRegistry, module_registry


def autoload_modules(
    registry: ModuleRegistry | None = None,
    page_handlers: dict[str, Callable[[dict], None]] | None = None,
    dependencies: dict[str, object] | None = None,
) -> None:
    """Dynamically import modules from the modules package and register their pages."""
    registry = registry or module_registry
    package_path = Path(__file__).resolve().parent

    for finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
        if name in {"__init__", "registry"} or ispkg:
            continue

        module_name = f"{__name__}.{name}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        register_fn = getattr(module, "register_module", None)
        if register_fn is None:
            continue

        try:
            parameters = inspect.signature(register_fn).parameters
            kwargs = {"registry": registry}
            if "page_handlers" in parameters and page_handlers is not None:
                kwargs["page_handlers"] = page_handlers
            if "dependencies" in parameters and dependencies is not None:
                kwargs["dependencies"] = dependencies
            register_fn(**kwargs)
        except Exception:
            continue


__all__ = ["ModuleRegistry", "module_registry", "autoload_modules"]
