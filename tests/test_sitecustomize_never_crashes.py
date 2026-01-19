import importlib

def test_sitecustomize_import_never_crashes():
    # Importing sitecustomize should never raise.
    importlib.import_module("sitecustomize")
