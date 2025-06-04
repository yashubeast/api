import importlib
import pkgutil
import os

from fastapi import APIRouter

from types import ModuleType

def iter_modules_recursive(package: ModuleType, base_path: str, prefix: str):
	for _, name, ispkg in pkgutil.iter_modules([base_path]):
		full_name = f"{package.__name__}.{name}"
		module = importlib.import_module(full_name)

		if hasattr(module, "router"):
			yield (f"{prefix}/{name}", module.router)

		if ispkg:
			sub_path = os.path.join(base_path, name)
			yield from iter_modules_recursive(module, sub_path, f"{prefix}/{name}")

def collect_routers() -> list[tuple[str, APIRouter]]:
	import routers
	base_path = os.path.dirname(__file__)
	return list(iter_modules_recursive(routers, base_path, ""))