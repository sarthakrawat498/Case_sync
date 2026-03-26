"""Routes package containing API endpoint handlers."""

from . import upload
from . import ner
from . import fir
from . import review
from . import pdf

__all__ = ["upload", "ner", "fir", "review", "pdf"]
