import sys

import pytest


@pytest.fixture(autouse=True)
def unload_m03_modules_after_each_test():
    yield
    for name in list(sys.modules):
        if name == "scrubbots_pixel_factory.generators" or name.startswith("scrubbots_pixel_factory.generators."):
            del sys.modules[name]
