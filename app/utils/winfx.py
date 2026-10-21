"""Acrylic de Windows 11 (22H2 o posterior) vía DWM. Si no está disponible,
devuelve False y la app usa su fondo propio opaco."""
import ctypes
import sys
from ctypes import Structure, byref, c_int, c_void_p


class _Margins(Structure):
    _fields_ = [("l", c_int), ("r", c_int), ("t", c_int), ("b", c_int)]


def set_acrylic(hwnd: int, enabled: bool) -> bool:
    if sys.platform != "win32":
        return False
    try:
        dwm = ctypes.windll.dwmapi
        h = c_void_p(hwnd)
        for attr, val in ((20, 1), (19, 1), (35, 0x00000000), (36, 0x00ECECEC)):   # título oscuro, caption negro
            dwm.DwmSetWindowAttribute(h, attr, byref(c_int(val)), 4)
        dwm.DwmExtendFrameIntoClientArea(h, byref(_Margins(-1, -1, -1, -1)))
        kind = c_int(3 if enabled else 1)                              # 3 = acrylic, 1 = ninguno
        return dwm.DwmSetWindowAttribute(h, 38, byref(kind), 4) == 0
    except Exception:
        return False
