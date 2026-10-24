#!/usr/bin/env python3
"""Compatibility loader; implementation is centralized in MOTOR_V15_3_NATIVO_V0_9_UNICO.py."""
import importlib.util as _iu
import sys as _sys
from pathlib import Path as _Path
_impl_path = _Path(__file__).with_name("MOTOR_V15_3_NATIVO_V0_9_UNICO.py")
_spec = _iu.spec_from_file_location("_motor_v15_3_nativo_v09_impl", _impl_path)
_impl = _iu.module_from_spec(_spec)
_sys.modules[_spec.name] = _impl
_spec.loader.exec_module(_impl)
for _name, _value in vars(_impl).items():
    if not (_name.startswith("__") and _name.endswith("__")):
        globals()[_name] = _value
