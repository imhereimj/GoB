"""
GoB UI — Blender N-Panel

3D Viewport의 N키 사이드바에 GoB 패널 표시.
GoZ 스타일의 심플한 인터페이스.
"""

import os
import bpy
from . import core
from . import watcher


class GOB_PT_main_panel(bpy.types.Panel):
    """GoB 메인 패널"""
    bl_label = "GoB"
    bl_idname = "GOB_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GoB"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        gob_path = prefs.gob_folder_path

        # ── 상태: 공유 폴더 내 파일 수 ──
        box = layout.box()
        row = box.row()
        row.scale_y = 0.8
        folders = core.get_history_folders(gob_path)
        if folders:
            row.label(text=f"GoB History: {len(folders)} record(s)", icon='CHECKMARK')
        else:
            row.label(text="GoB History: 0 records", icon='DOT')

        layout.separator()

        # ── 메인 버튼 ──
        col = layout.column(align=True)

        # CLO → Blender
        row = col.row(align=True)
        row.scale_y = 1.8
        row.operator("gob.import_from_clo", text="Get from CLO", icon='IMPORT')

        if prefs.show_send_to_clo:
            col.separator()
    
            # Blender → CLO
            row = col.row(align=True)
            row.scale_y = 1.8
            row.operator("gob.send_to_clo", text="Send to CLO", icon='EXPORT')

        layout.separator()

        # ── Auto-Import 토글 ──
        row = layout.row(align=True)
        row.scale_y = 1.4
        if watcher.is_polling():
            row.operator("gob.toggle_watch", text="Auto-Import ON", icon='REC', depress=True)
        else:
            row.operator("gob.toggle_watch", text="Auto-Import OFF", icon='PLAY')

        layout.separator()

        # ── 유틸리티 ──
        col = layout.column(align=True)
        col.operator("gob.open_folder", text="Open GoB Folder", icon='FILEBROWSER')


class GOB_PT_settings_panel(bpy.types.Panel):
    """GoB 설정 서브패널"""
    bl_label = "Settings"
    bl_idname = "GOB_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GoB"
    bl_parent_id = "GOB_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__package__].preferences

        layout.prop(prefs, "gob_folder_path", text="Folder")
        layout.prop(prefs, "export_format", text="Format")
        layout.prop(prefs, "show_send_to_clo", text="Show 'Send to CLO'")
        layout.prop(prefs, "max_folder_history", text="Max History")
        
        layout.separator()
        row = layout.row()
        row.alert = True
        row.operator("gob.clear_all_history", text="⚠️ Delete All GoB Temp Data", icon='TRASH')


classes = (
    GOB_PT_main_panel,
    GOB_PT_settings_panel,
)
