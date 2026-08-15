"""Public package interface for neonify."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .animation import GlowStyle, render_frame
from .palette import RAINBOW, Color
from .renderer import DEFAULT_INTERVAL_MS, AnimationConfig, animate

try:
    __version__ = version("neonify")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "DEFAULT_INTERVAL_MS",
    "RAINBOW",
    "AnimationConfig",
    "Color",
    "GlowStyle",
    "__version__",
    "animate",
    "render_frame",
]
