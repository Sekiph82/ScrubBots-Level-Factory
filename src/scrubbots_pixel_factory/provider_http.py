"""The only network-capable import boundary besides offline.py.

The owner-approved PixelLab provider transport (studio_extensions) uses these
standard-library HTTP primitives. Keeping them here keeps every other
production module free of network imports (tests/integration/test_offline_boundary.py).
"""

from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

__all__ = ["HTTPError", "Request", "URLError", "urlopen", "urlparse"]
