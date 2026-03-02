"""
GoB - CLO <-> Blender Bridge Add-on

GoZ-style shared folder mesh exchange.
Shared folder: C:/Users/Public/GoB/
Format: OBJ (Mesh + UV)
"""

bl_info = {
    "name": "GoB — CLO Bridge",
    "author": "Jaeyong Lee",
    "version": (0, 2, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > GoB",
    "description": "CLO <-> Blender mesh exchange bridge (v0.2.0 Beta with macOS support)",
    "category": "Import-Export",
}

import importlib
from . import core
VERSION = core.VERSION
from . import preferences
from . import operators
from . import ui
from . import watcher

_modules = (core, preferences, operators, ui, watcher)


def register():
    import bpy
    for cls in preferences.classes:
        bpy.utils.register_class(cls)
    for cls in operators.classes:
        bpy.utils.register_class(cls)
    for cls in ui.classes:
        bpy.utils.register_class(cls)

    core.ensure_gob_folder()
    print(f"[GoB] Add-on registered (v{'.'.join(str(v) for v in bl_info['version'])})")


def unregister():
    import bpy
    # Auto-polling 중지
    watcher.stop_polling()

    for cls in reversed(ui.classes):
        bpy.utils.unregister_class(cls)
    for cls in reversed(operators.classes):
        bpy.utils.unregister_class(cls)
    for cls in reversed(preferences.classes):
        bpy.utils.unregister_class(cls)
    print("[GoB] Add-on unregistered")


if __name__ == "__main__":
    register()
