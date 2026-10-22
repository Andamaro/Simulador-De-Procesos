# -*- mode: python ; coding: utf-8 -*-
# PyInstaller, modo "un solo archivo": binarios y datos van directo al EXE (sin COLLECT).
# Resultado: dist/SimuladorProcesos.exe
import os

ROOT = os.path.abspath(SPECPATH)

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=[],
    # Único recurso que la app carga en tiempo de ejecución: las tipografías (app/utils/paths.py).
    datas=[(os.path.join(ROOT, "assets", "fonts"), os.path.join("assets", "fonts"))],
    # Solo hay imports estáticos de PySide6 (QtCore, QtGui, QtWidgets): no hace falta ningún hiddenimport.
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter", "unittest", "pytest", "pydoc", "test",
        "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
        "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtQuick3D",
        "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DInput", "PySide6.Qt3DLogic",
        "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras", "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets", "PySide6.QtCharts", "PySide6.QtDataVisualization",
        "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtSql", "PySide6.QtTest",
        "PySide6.QtBluetooth", "PySide6.QtNfc", "PySide6.QtSensors", "PySide6.QtSerialPort",
        "PySide6.QtWebSockets", "PySide6.QtWebChannel", "PySide6.QtPositioning",
        "PySide6.QtLocation", "PySide6.QtRemoteObjects", "PySide6.QtScxml", "PySide6.QtSvg",
        "PySide6.QtSvgWidgets", "PySide6.QtNetwork", "PySide6.QtDesigner", "PySide6.QtHelp",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SimuladorProcesos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
)
