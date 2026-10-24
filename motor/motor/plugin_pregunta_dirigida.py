#!/usr/bin/env python3
"""Compatibility loader; implementation is centralized in plugin_pregunta_dirigida_v0_5_1.py."""
import importlib.util as _iu
import sys as _sys
from pathlib import Path as _Path
_impl_path = _Path(__file__).with_name("plugin_pregunta_dirigida_v0_5_1.py")
_spec = _iu.spec_from_file_location("_plugin_pregunta_dirigida_v051_impl", _impl_path)
_impl = _iu.module_from_spec(_spec)
_sys.modules[_spec.name] = _impl
_spec.loader.exec_module(_impl)
for _name, _value in vars(_impl).items():
    if not (_name.startswith("__") and _name.endswith("__")):
        globals()[_name] = _value
