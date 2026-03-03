"""
GoB Preferences — Add-on 설정

편집 > 환경설정 > Add-ons에서 GoB 설정 관리.
"""

import bpy
from bpy.props import StringProperty, EnumProperty
from . import core


class GOBPreferences(bpy.types.AddonPreferences):
    """GoB Add-on 환경 설정"""
    bl_idname = __package__

    # GoB 공유 폴더 경로
    gob_folder_path: StringProperty(
        name="GoB Folder",
        description="Path to the GoB shared folder for CLO ↔ Blender mesh exchange",
        default=core.DEFAULT_GOB_PATH,
        subtype='DIR_PATH',
    )

    # Export 포맷
    export_format: EnumProperty(
        name="Export Format",
        description="3D format used for CLO ↔ Blender exchange",
        items=[
            ('OBJ', "OBJ", "Wavefront OBJ (mesh + UV, best compatibility)"),
            ('FBX', "FBX", "FBX (planned for future support)"),
        ],
        default='OBJ',
    )
    
    # Send to CLO 버튼 표시 여부
    show_send_to_clo: bpy.props.BoolProperty(
        name="Enable 'Send to CLO' Button",
        description="Show the 'Send to CLO' button in the main panel",
        default=False,
    )
    
    # 최대 유지 가능한 내보내기 폴더 수
    max_folder_history: bpy.props.IntProperty(
        name="Max Folder History",
        description="Maximum number of export folders to keep in the GoB shared folder (oldest are auto-deleted)",
        default=5,
        min=1,
        max=20,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Shared Folder", icon='FILE_FOLDER')
        box.prop(self, "gob_folder_path")

        box = layout.box()
        box.label(text="Exchange Format", icon='MESH_DATA')
        box.prop(self, "export_format")
        
        box = layout.box()
        box.label(text="UI Options", icon='WINDOW')
        box.prop(self, "show_send_to_clo")
        
        box = layout.box()
        box.label(text="History Management", icon='TIME')
        box.prop(self, "max_folder_history")


classes = (
    GOBPreferences,
)
