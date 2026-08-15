"""Public package interface for neonify."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .animation import REST_FRAMES, SHINE_WIDTH, GlowStyle, render_frame
from .palette import RAINBOW, Color, Hue, gradient
from .renderer import DEFAULT_INTERVAL_MS, AnimationConfig, animate

try:
    __version__ = version("neonify")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "DEFAULT_INTERVAL_MS",
    "RAINBOW",
    "REST_FRAMES",
    "SHINE_WIDTH",
    "AnimationConfig",
    "Color",
    "GlowStyle",
    "Hue",
    "__version__",
    "animate",
    "gradient",
    "render_frame",
]
