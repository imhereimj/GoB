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
        description="GoB 공유 폴더 경로 (GoZ의 GoZProjects와 동일 역할)",
        default=core.DEFAULT_GOB_PATH,
        subtype='DIR_PATH',
    )

    # Export 포맷
    export_format: EnumProperty(
        name="Export Format",
        description="CLO ↔ Blender 교환 시 사용할 3D 포맷",
        items=[
            ('OBJ', "OBJ", "Wavefront OBJ (메시+UV, 가장 호환성 높음)"),
            ('FBX', "FBX", "FBX (향후 지원 예정)"),
        ],
        default='OBJ',
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Shared Folder", icon='FILE_FOLDER')
        box.prop(self, "gob_folder_path")

        box = layout.box()
        box.label(text="Exchange Format", icon='MESH_DATA')
        box.prop(self, "export_format")


classes = (
    GOBPreferences,
)
