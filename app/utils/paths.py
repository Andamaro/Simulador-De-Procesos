import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Ruta a recursos, tanto en desarrollo como dentro de PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base.joinpath(*parts)
