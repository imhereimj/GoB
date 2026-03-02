"""
GoB Operators — Blender 오퍼레이터

GoZ와 동일한 공유 폴더 방식으로 메시를 교환.
CLO → Blender: Import + 텍스처 Auto-Shader 연결.
Blender → CLO: OBJ Export.

워크플로우:
  CLO → Blender: CLO에서 GoB 폴더로 OBJ Export → Blender에서 Import 클릭
  Blender → CLO: Blender에서 Send 클릭 → GoB 폴더에 OBJ → CLO에서 Import
"""

import os
import re
import bpy
from bpy.props import StringProperty
from bpy.types import FileHandler

from . import core
from . import watcher


# ── 텍스처 → 셰이더 자동 연결 ──────────────────────────

# 파일명 키워드 → Principled BSDF 소켓 매핑
_TEXTURE_MAP_KEYWORDS = {
    "diffuse":   "Base Color",
    "basecolor": "Base Color",
    "base_color": "Base Color",
    "albedo":    "Base Color",
    "normal":    "Normal",
    "roughness": "Roughness",
    "metalness": "Metallic",
    "metallic":  "Metallic",
    "opacity":   "Alpha",
    "alpha":     "Alpha",
}

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tga", ".bmp", ".tiff"}

# UDIM 타일 번호 패턴: name.1001.ext, name.1002.ext, ...
_UDIM_PATTERN = re.compile(r'^(.+)\.(\d{4})$')


def _detect_texture_type(name_no_ext):
    """
    파일명(확장자 제외)에서 텍스처 타입을 감지.
    CLO가 내보내는 텍스처 파일명 패턴: ...Diffuse.png, ...Normal.png 등
    Returns: Principled BSDF 소켓 이름 또는 None.
    """
    name_lower = name_no_ext.lower()
    for keyword, socket in _TEXTURE_MAP_KEYWORDS.items():
        if keyword in name_lower:
            return socket
    return None


def _find_textures_in_folder(folder):
    """
    폴더에서 이미지 파일을 스캔하고 텍스처 타입별로 분류.
    UDIM 텍스처(name.1001.png ~ name.100N.png)도 자동 감지하여 그룹화.

    Returns: {
        "Base Color": {"path": filepath, "is_udim": False},
        "Normal":     {"path": filepath, "is_udim": True, "tiles": [1001, 1002, ...]},
        ...
    }
    """
    texture_map = {}
    # UDIM 그룹: { (base_name, socket_name): [tile_numbers] }
    udim_groups = {}

    if not os.path.isdir(folder):
        return texture_map

    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in _IMAGE_EXTENSIONS:
            continue

        name_no_ext = os.path.splitext(filename)[0]

        # UDIM 패턴 체크: name.1001 → base=name, tile=1001
        udim_match = _UDIM_PATTERN.match(name_no_ext)
        if udim_match:
            base_name = udim_match.group(1)
            tile_num = int(udim_match.group(2))
            # 1001~1099 범위의 유효한 UDIM 타일 번호인지 확인
            if 1001 <= tile_num <= 1099:
                socket_name = _detect_texture_type(base_name)
                if socket_name:
                    key = (base_name, socket_name, ext)
                    if key not in udim_groups:
                        udim_groups[key] = []
                    udim_groups[key].append(tile_num)
                continue

        # 일반 텍스처 (UDIM 아닌 경우)
        socket_name = _detect_texture_type(name_no_ext)
        if socket_name and socket_name not in texture_map:
            texture_map[socket_name] = {
                "path": os.path.join(folder, filename),
                "is_udim": False,
            }

    # UDIM 그룹을 texture_map에 추가
    for (base_name, socket_name, ext), tiles in udim_groups.items():
        tiles.sort()
        # UDIM 경로: base_name.<UDIM>.ext (Blender 규격)
        udim_path = os.path.join(folder, f"{base_name}.{tiles[0]}{ext}")
        texture_map[socket_name] = {
            "path": udim_path,
            "is_udim": True,
            "tiles": tiles,
            "base_name": base_name,
            "ext": ext,
            "folder": folder,
        }

    return texture_map


def _load_udim_image(tex_info):
    """
    UDIM 타일 이미지를 Blender Tiled Image로 로드.
    Returns: bpy.types.Image
    """
    first_tile_path = tex_info["path"]
    tiles = tex_info["tiles"]
    base_name = tex_info["base_name"]

    # 첫 번째 타일 로드
    img = bpy.data.images.load(first_tile_path, check_existing=True)
    img.source = 'TILED'

    # 나머지 타일 추가 (1001은 이미 기본 포함)
    for tile_num in tiles:
        if tile_num == 1001:
            continue
        # 타일이 아직 없으면 추가
        existing_tiles = {t.number for t in img.tiles}
        if tile_num not in existing_tiles:
            img.tiles.new(tile_number=tile_num)

    print(f"[GoB] UDIM: {base_name} → {len(tiles)} tile(s): {tiles}")
    return img


def _apply_auto_shader(obj, texture_map):
    """
    오브젝트에 Principled BSDF Material 생성 후 텍스처 노드 자동 연결.
    일반 텍스처와 UDIM 텍스처 모두 지원.
    기존 Material이 있으면 그 위에 텍스처만 연결.
    """
    if not texture_map:
        return

    # Material 확보 (없으면 생성)
    if not obj.data.materials:
        mat = bpy.data.materials.new(name=f"GoB_{obj.name}")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]
        if not mat.use_nodes:
            mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Principled BSDF 찾기 (없으면 생성)
    principled = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled = node
            break
    if not principled:
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')

    # 텍스처 노드 배치 시작 위치
    x_offset = principled.location.x - 400
    y_offset = principled.location.y + 200
    y_step = -300

    connected_count = 0
    for idx, (socket_name, tex_info) in enumerate(texture_map.items()):
        # 이미지 로드 (UDIM vs 일반)
        if tex_info["is_udim"]:
            img = _load_udim_image(tex_info)
        else:
            img = bpy.data.images.load(tex_info["path"], check_existing=True)

        # Image Texture 노드 생성
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.image = img
        tex_node.location = (x_offset, y_offset + y_step * idx)
        tex_node.label = socket_name

        if socket_name == "Normal":
            # Normal Map 노드 삽입
            img.colorspace_settings.name = 'Non-Color'
            normal_node = nodes.new(type='ShaderNodeNormalMap')
            normal_node.location = (x_offset + 300, y_offset + y_step * idx)
            links.new(tex_node.outputs['Color'], normal_node.inputs['Color'])
            if 'Normal' in principled.inputs:
                links.new(normal_node.outputs['Normal'], principled.inputs['Normal'])
                connected_count += 1

        elif socket_name in ("Roughness", "Metallic"):
            # Non-Color 데이터
            img.colorspace_settings.name = 'Non-Color'
            if socket_name in principled.inputs:
                links.new(tex_node.outputs['Color'], principled.inputs[socket_name])
                connected_count += 1

        elif socket_name == "Alpha":
            if 'Alpha' in principled.inputs:
                links.new(tex_node.outputs['Color'], principled.inputs['Alpha'])
                mat.blend_method = 'CLIP'  # EEVEE용
                connected_count += 1

        else:
            # Base Color 등
            if socket_name in principled.inputs:
                links.new(tex_node.outputs['Color'], principled.inputs[socket_name])
                connected_count += 1

    if connected_count > 0:
        print(f"[GoB] Shader: {obj.name} ← {connected_count} texture(s) connected")


def import_and_setup(filepath, report_fn=None):
    """
    OBJ/FBX Import + 텍스처 Auto-Shader 연결.
    operators.py와 watcher.py 양쪽에서 공용 사용.
    Returns: True if import 성공.
    """
    ext = os.path.splitext(filepath)[1].lower()
    folder = os.path.dirname(filepath)

    # Import 전 오브젝트 목록 스냅샷
    before = set(bpy.data.objects[:])

    try:
        if ext == ".obj":
            bpy.ops.wm.obj_import(filepath=filepath)
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=filepath)
        else:
            return False
    except Exception as e:
        if report_fn:
            report_fn({'WARNING'}, f"[GoB] Import 실패: {os.path.basename(filepath)} — {e}")
        return False

    # 새로 Import된 오브젝트 감지
    after = set(bpy.data.objects[:])
    new_objects = after - before

    # 텍스처 Auto-Shader 연결
    texture_map = _find_textures_in_folder(folder)
    if texture_map:
        for obj in new_objects:
            if obj.type == 'MESH':
                _apply_auto_shader(obj, texture_map)

    return True


# ── Import / Export 오퍼레이터 ──────────────────────────

class GOB_OT_import_from_clo(bpy.types.Operator):
    """GoB 공유 폴더에서 CLO가 내보낸 파일을 Import"""
    bl_idname = "gob.import_from_clo"
    bl_label = "Get from CLO"
    bl_description = "GoB 공유 폴더의 OBJ/FBX 파일을 Blender에 Import"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        gob_path = prefs.gob_folder_path

        # 1. Manifest가 있으면 manifest 기반 Import
        manifest = core.read_manifest(gob_path)
        if manifest and manifest["files"]:
            files = manifest["files"]
        else:
            # 2. Manifest 없으면 폴더 직접 스캔
            files = core.get_gob_files(gob_path)

        if not files:
            self.report({'WARNING'}, "[GoB] 공유 폴더에 Import할 파일이 없습니다")
            return {'CANCELLED'}

        imported = 0
        for filepath in files:
            if import_and_setup(filepath, self.report):
                imported += 1

        self.report({'INFO'}, f"[GoB] {imported}개 오브젝트 Import 완료")
        return {'FINISHED'}


class GOB_OT_send_to_clo(bpy.types.Operator):
    """선택된 메시를 GoB 공유 폴더로 Export (CLO에서 Import 가능)"""
    bl_idname = "gob.send_to_clo"
    bl_label = "Send to CLO"
    bl_description = "선택된 메시를 OBJ로 GoB 공유 폴더에 Export"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.selected_objects
            and any(obj.type == 'MESH' for obj in context.selected_objects)
        )

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        gob_path = prefs.gob_folder_path

        # 1. 공유 폴더 준비
        folder = core.ensure_gob_folder(gob_path)
        if not folder:
            self.report({'ERROR'}, "[GoB] 공유 폴더 생성 실패")
            return {'CANCELLED'}

        core.clean_gob_folder(gob_path)

        # 2. 선택된 메시 필터링
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not mesh_objects:
            self.report({'WARNING'}, "[GoB] 메시 오브젝트를 선택하세요")
            return {'CANCELLED'}

        # 3. OBJ Export
        obj_name = _sanitize_filename(mesh_objects[0].name)
        obj_path = os.path.join(folder, f"{obj_name}.obj")

        try:
            _export_obj(obj_path, mesh_objects, context)
        except Exception as e:
            self.report({'ERROR'}, f"[GoB] Export 실패: {e}")
            return {'CANCELLED'}

        # 4. Manifest 작성
        core.write_manifest(
            [obj_path],
            core.DIR_BLENDER_TO_CLO,
            gob_path,
            fmt="obj",
        )

        self.report({'INFO'}, f"[GoB] Export 완료 → {obj_path}")
        return {'FINISHED'}


class GOB_OT_import_zprj(bpy.types.Operator):
    """ZPRJ를 GoB 공유 폴더에 복사 (드래그앤드롭 대응, CLO에서 직접 열기 안내)"""
    bl_idname = "gob.import_zprj"
    bl_label = "Import ZPRJ via GoB"
    bl_description = ".zprj 파일을 GoB 공유 폴더에 복사"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH')
    directory: StringProperty(subtype='DIR_PATH')
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'

    def execute(self, context):
        import shutil
        prefs = context.preferences.addons[__package__].preferences
        gob_path = prefs.gob_folder_path

        # 파일 경로 결정
        if self.files and self.directory:
            zprj_path = os.path.join(self.directory, self.files[0].name)
        elif self.filepath:
            zprj_path = self.filepath
        else:
            self.report({'ERROR'}, "[GoB] ZPRJ 파일 경로가 없습니다")
            return {'CANCELLED'}

        if not zprj_path.lower().endswith('.zprj'):
            self.report({'ERROR'}, "[GoB] .zprj 파일만 지원됩니다")
            return {'CANCELLED'}

        # 공유 폴더에 복사
        folder = core.ensure_gob_folder(gob_path)
        if not folder:
            self.report({'ERROR'}, "[GoB] 공유 폴더 생성 실패")
            return {'CANCELLED'}

        dest = os.path.join(folder, os.path.basename(zprj_path))
        try:
            shutil.copy2(zprj_path, dest)
        except OSError as e:
            self.report({'ERROR'}, f"[GoB] 파일 복사 실패: {e}")
            return {'CANCELLED'}

        # Manifest 작성
        core.write_manifest([dest], core.DIR_CLO_TO_BLENDER, gob_path, fmt="zprj")

        self.report(
            {'INFO'},
            f"[GoB] ZPRJ → GoB 폴더 복사 완료. CLO에서 GoB 폴더의 파일을 열고 OBJ Export 후 'Get from CLO' 클릭",
        )
        return {'FINISHED'}

    def invoke(self, context, event):
        if self.filepath or self.files:
            return self.execute(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class GOB_FH_zprj(FileHandler):
    """.zprj 파일 드래그앤드롭 핸들러"""
    bl_idname = "GOB_FH_zprj"
    bl_label = "ZPRJ File Handler"
    bl_import_operator = "gob.import_zprj"
    bl_file_extensions = ".zprj"

    @classmethod
    def poll_drop(cls, context):
        return context.area and context.area.type == 'VIEW_3D'


class GOB_OT_open_folder(bpy.types.Operator):
    """GoB 공유 폴더를 파일 탐색기에서 열기"""
    bl_idname = "gob.open_folder"
    bl_label = "Open GoB Folder"
    bl_description = "GoB 공유 폴더를 파일 탐색기에서 엽니다"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        folder = core.ensure_gob_folder(prefs.gob_folder_path)

        if folder and os.path.isdir(folder):
            import subprocess
            import platform
            
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', folder])
            else:  # Windows
                subprocess.Popen(f'explorer "{folder}"')
            return {'FINISHED'}

        self.report({'ERROR'}, "[GoB] 폴더를 열 수 없습니다")
        return {'CANCELLED'}


# ── 유틸리티 ──────────────────────────────────────────

def _sanitize_filename(name):
    """파일명에 사용할 수 없는 문자 제거."""
    invalid_chars = '<>:"/\\|?*'
    return "".join(c for c in name if c not in invalid_chars).strip() or "untitled"


def _export_obj(filepath, objects, context):
    """선택된 오브젝트를 OBJ Export."""
    original_selection = context.selected_objects[:]
    original_active = context.view_layer.objects.active

    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    context.view_layer.objects.active = objects[0]

    try:
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True,
            export_uv=True,
            export_materials=True,
            export_triangulated_mesh=False,
            forward_axis='NEGATIVE_Z',
            up_axis='Y',
        )
    finally:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selection:
            try:
                obj.select_set(True)
            except ReferenceError:
                pass
        if original_active:
            try:
                context.view_layer.objects.active = original_active
            except ReferenceError:
                pass


# ── Auto-Polling ──────────────────────────────────────

class GOB_OT_toggle_watch(bpy.types.Operator):
    """GoB 공유 폴더 자동 감시 ON/OFF"""
    bl_idname = "gob.toggle_watch"
    bl_label = "Toggle Auto-Import"
    bl_description = "CLO가 공유 폴더에 파일을 넣으면 자동으로 Import (GoZ 스타일)"

    def execute(self, context):
        if watcher.is_polling():
            watcher.stop_polling()
            self.report({'INFO'}, "[GoB] Auto-Import OFF")
        else:
            watcher.start_polling()
            self.report({'INFO'}, "[GoB] Auto-Import ON — CLO에서 Export하면 자동 Import됩니다")
        return {'FINISHED'}


# ── 등록 ──────────────────────────────────────────────

classes = (
    GOB_OT_import_from_clo,
    GOB_OT_send_to_clo,
    GOB_OT_import_zprj,
    GOB_FH_zprj,
    GOB_OT_open_folder,
    GOB_OT_toggle_watch,
)
