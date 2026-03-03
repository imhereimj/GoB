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

from . import core
from . import watcher


# ── 텍스처 → 셰이더 자동 연결 ──────────────────────────

# 파일명 키워드 → Principled BSDF 소켓 매핑
_TEXTURE_MAP_KEYWORDS = {
    "diffuse":   "Base Color",
    "metalness": "Metallic",
    "roughness": "Roughness",
    "normal":    "Normal",
    "opacity":   "Alpha",
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


def _apply_auto_shader_to_mat(mat, texture_map):
    """
    Material에 기존 노드를 지우고 Principled BSDF 및 텍스처 노드를 자동 연결.
    일반 텍스처와 UDIM 텍스처 모두 지원.
    """
    if not texture_map:
        return

    if not mat.use_nodes:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 기존 노드 초기화 (MTL 생성 노드 제거)
    nodes.clear()

    # Material Output 생성
    mat_out = nodes.new(type='ShaderNodeOutputMaterial')
    mat_out.location = (300, 300)

    # Principled BSDF 생성
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 300)

    # BSDF -> Output 연결
    links.new(principled.outputs['BSDF'], mat_out.inputs['Surface'])

    # 텍스처 노드 배치 시작 위치 (Principled BSDF 기준으로 상대 위치)
    x_offset = principled.location.x - 400
    y_offset = principled.location.y
    y_step = -300

    # Frame 노드들 세팅 (Mapping, Textures)
    frame_mapping = nodes.new(type='NodeFrame')
    frame_mapping.name = "Frame_Mapping"
    frame_mapping.label = "Mapping"

    frame_textures = nodes.new(type='NodeFrame')
    frame_textures.name = "Frame_Textures"
    frame_textures.label = "Textures"

    # Mapping 노드 블록 구성
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.name = "Texture Coordinate"
    tex_coord.location = (x_offset - 600, y_offset)
    tex_coord.parent = frame_mapping

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.name = "Mapping"
    mapping.location = (x_offset - 400, y_offset)
    mapping.parent = frame_mapping

    reroute = nodes.new(type='NodeReroute')
    reroute.name = "Reroute_Mapping"
    reroute.location = (x_offset - 200, y_offset - 100)
    
    # 링크 연결 (UV -> Mapping -> Reroute)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], reroute.inputs[0])

    connected_count = 0
    # 출력 순서를 정의하여 노드들이 깔끔하게 세로로 정렬되도록 함
    order = {"Base Color": 0, "Metallic": 1, "Roughness": 2, "Alpha": 3, "Normal": 4}
    sorted_items = sorted(texture_map.items(), key=lambda x: order.get(x[0], 99))

    for idx, (socket_name, tex_info) in enumerate(sorted_items):
        # 이미지 로드 (UDIM vs 일반)
        if tex_info["is_udim"]:
            img = _load_udim_image(tex_info)
        else:
            img = bpy.data.images.load(tex_info["path"], check_existing=True)

        # Image Texture 노드 찾기 또는 생성
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.label = socket_name
            
        tex_node.image = img
        tex_node.location = (x_offset, y_offset + y_step * idx)
        tex_node.parent = frame_textures

        # Vector 입력에 Reroute 연결
        links.new(reroute.outputs[0], tex_node.inputs['Vector'])

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
            img.colorspace_settings.name = 'Non-Color'
            if 'Alpha' in principled.inputs:
                links.new(tex_node.outputs['Color'], principled.inputs['Alpha'])
                mat.blend_method = 'CLIP'  # EEVEE용
                connected_count += 1

        else:
            # Base Color 등
            img.colorspace_settings.name = 'sRGB'
            if socket_name in principled.inputs:
                links.new(tex_node.outputs['Color'], principled.inputs[socket_name])
                connected_count += 1

    if connected_count > 0:
        print(f"[GoB] Shader: {mat.name} ← {connected_count} texture(s) connected")


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
            report_fn({'WARNING'}, f"[GoB] Import failed: {os.path.basename(filepath)} — {e}")
        return False

    # 새로 Import된 오브젝트 감지
    after = set(bpy.data.objects[:])
    new_objects = after - before

    # 텍스처 Auto-Shader 연결 (MTL 기반)
    # 기존: 지정된 폴더 안의 모든 텍스처를 스캔하고 같은 유형별 1장만 추출
    # 변경: 각 머테리얼별로 이미 연결된 Diffuse 맵(Base Color)의 파일명을 분석하여
    # 해당 머테리얼에 맞는 Roughness, Normal 등을 유추하여 연결

    if new_objects:
        new_materials = set()
        for obj in new_objects:
            if obj.type == 'MESH':
                for mat in obj.data.materials:
                    if mat and mat.use_nodes:
                        new_materials.add(mat)
                        
        for mat in new_materials:
            nodes = mat.node_tree.nodes
            base_color_path = None
            
            # 1. 블렌더가 MTL로 자동 연결한 Image Texture 노드 찾기
            # Base Color에 연결된 노드이거나, 그냥 첫 번째 Image Texture 노드 활용
            for node in nodes:
                if node.type == 'TEX_IMAGE' and node.image and node.image.filepath:
                    # 간단하게 첫 번째 이미지를 메인 디퓨즈로 간주
                    base_color_path = bpy.path.abspath(node.image.filepath)
                    break
                    
            if not base_color_path or not os.path.exists(base_color_path):
                continue
                
            # 2. 경로 문자열 분석을 통해 나머지 텍스처 파일 찾기
            # 예: "output_diffuse_1001.png" -> folder: "...", prefix: "output_", suffix: "_1001"
            folder_path = os.path.dirname(base_color_path)
            filename = os.path.basename(base_color_path)
            name_no_ext, ext = os.path.splitext(filename)
            
            # 정규식을 통해 diffuse 글자를 찾고 치환 (대소문자 무시)
            # diffuse가 포함되어 있지 않다면 치환 생략
            diffuse_match = re.search(r'diffuse', name_no_ext, re.IGNORECASE)
            
            texture_map = {}
            if diffuse_match:
                # "diffuse" (또는 "Diffuse") 부분만 교체해가면서 파일 존재 확인
                start, end = diffuse_match.span()
                prefix = name_no_ext[:start]
                suffix = name_no_ext[end:]
                
                # Base Color 등록
                texture_map["Base Color"] = {
                    "path": base_color_path,
                    "is_udim": False
                }
                
                # UDIM 체크 (suffix가 숫자로만 이루어져 있는지)
                udim_match = _UDIM_PATTERN.search(filename)
                if udim_match:
                    tile_num = int(udim_match.group(2))
                    if 1001 <= tile_num <= 1099:
                        # UDIM 처리
                        for key, socket in _TEXTURE_MAP_KEYWORDS.items():
                            if socket == "Base Color":
                                continue
                            
                            # 치환할 키워드의 대소문자를 맞춰줌 (원본이 소문자면 소문자, 대문자면 대문자)
                            replace_word = key if name_no_ext[start].islower() else key.capitalize()
                            test_name = f"{prefix}{replace_word}{suffix}{ext}"
                            test_path = os.path.join(folder_path, test_name)
                            
                            if os.path.exists(test_path):
                                # UDIM 타일 찾기
                                base_name_for_udim = f"{prefix}{replace_word}"
                                tiles = []
                                for f in os.listdir(folder_path):
                                    if f.startswith(base_name_for_udim) and f.endswith(ext):
                                        m = _UDIM_PATTERN.match(os.path.splitext(f)[0])
                                        if m and m.group(1) == base_name_for_udim:
                                            tiles.append(int(m.group(2)))
                                tiles.sort()
                                udim_path = os.path.join(folder_path, f"{base_name_for_udim}.{tiles[0]}{ext}")
                                
                                texture_map[socket] = {
                                    "path": udim_path,
                                    "is_udim": True,
                                    "tiles": tiles,
                                    "base_name": base_name_for_udim,
                                    "ext": ext,
                                    "folder": folder_path
                                }
                                
                        # Base Color 도 UDIM 정보로 덮어쓰기
                        base_name_for_udim = f"{prefix}{name_no_ext[start:end]}"
                        tiles = []
                        for f in os.listdir(folder_path):
                            if f.startswith(base_name_for_udim) and f.endswith(ext):
                                m = _UDIM_PATTERN.match(os.path.splitext(f)[0])
                                if m and m.group(1) == base_name_for_udim:
                                    tiles.append(int(m.group(2)))
                        tiles.sort()
                        udim_path = os.path.join(folder_path, f"{base_name_for_udim}.{tiles[0]}{ext}")
                        texture_map["Base Color"] = {
                            "path": udim_path,
                            "is_udim": True,
                            "tiles": tiles,
                            "base_name": base_name_for_udim,
                            "ext": ext,
                            "folder": folder_path
                        }
                                
                if not texture_map.get("Base Color").get("is_udim"):
                    # 일반(UDIM 아님) 텍스처 찾기
                    for key, socket in _TEXTURE_MAP_KEYWORDS.items():
                        if socket == "Base Color":
                            continue
                        replace_word = key if name_no_ext[start].islower() else key.capitalize()
                        test_name = f"{prefix}{replace_word}{suffix}{ext}"
                        test_path = os.path.join(folder_path, test_name)
                        if os.path.exists(test_path):
                            texture_map[socket] = {
                                "path": test_path,
                                "is_udim": False
                            }
            else:
                # 파일명에 diffuse가 없으면 그냥 Base Color만 연결
                texture_map["Base Color"] = {
                    "path": base_color_path,
                    "is_udim": False
                }
                
            if texture_map:
                _apply_auto_shader_to_mat(mat, texture_map)

    return True


# ── Import / Export 오퍼레이터 ──────────────────────────

class GOB_OT_import_from_clo(bpy.types.Operator):
    """GoB 공유 폴더에서 CLO가 내보낸 파일을 Import"""
    bl_idname = "gob.import_from_clo"
    bl_label = "Get from CLO"
    bl_description = "Import OBJ/FBX files from the GoB shared folder into Blender"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        gob_path = prefs.gob_folder_path

        # 최대 폴더 수 초과 시 오래된 내역 청소
        core.enforce_folder_limit(prefs.max_folder_history, gob_path)

        # 1. Manifest가 있으면 → manifest가 가리키는 파일만 Import (최신 1세트)
        manifest = core.read_manifest(gob_path)
        if manifest and manifest["files"]:
            files = manifest["files"]
            core.gob_log(f"[Import] Via manifest: {[os.path.basename(f) for f in files]}")
        else:
            # 2. Manifest 없으면 → 가장 최신 GoB_* 서브폴더 1개의 OBJ만 Import
            files = core.get_latest_gob_files(gob_path)
            core.gob_log(f"[Import] Via latest folder: {[os.path.basename(f) for f in files]}")

        if not files:
            self.report({'WARNING'}, "[GoB] No files found in the shared folder")
            return {'CANCELLED'}

        imported = 0
        for filepath in files:
            if import_and_setup(filepath, self.report):
                imported += 1

        # 수동 Import한 파일을 Watcher에 등록 → 중복 Auto-Import 방지
        watcher.register_imported_files(files)

        self.report({'INFO'}, f"[GoB] {imported} object(s) imported")
        return {'FINISHED'}


class GOB_OT_send_to_clo(bpy.types.Operator):
    """선택된 메시를 GoB 공유 폴더로 Export (CLO에서 Import 가능)"""
    bl_idname = "gob.send_to_clo"
    bl_label = "Send to CLO"
    bl_description = "Export selected mesh(es) as OBJ to the GoB shared folder"
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
            self.report({'ERROR'}, "[GoB] Failed to create shared folder")
            return {'CANCELLED'}

        core.clean_gob_folder(gob_path)

        # 2. 선택된 메시 필터링
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not mesh_objects:
            self.report({'WARNING'}, "[GoB] Please select a mesh object")
            return {'CANCELLED'}

        # 3. OBJ Export
        obj_name = _sanitize_filename(mesh_objects[0].name)
        obj_path = os.path.join(folder, f"{obj_name}.obj")

        try:
            _export_obj(obj_path, mesh_objects, context)
        except Exception as e:
            self.report({'ERROR'}, f"[GoB] Export failed: {e}")
            return {'CANCELLED'}

        # 4. Manifest 작성
        core.write_manifest(
            [obj_path],
            core.DIR_BLENDER_TO_CLO,
            gob_path,
            fmt="obj",
        )

        self.report({'INFO'}, f"[GoB] Export complete → {obj_path}")
        return {'FINISHED'}




class GOB_OT_open_folder(bpy.types.Operator):
    """GoB 공유 폴더를 파일 탐색기에서 열기"""
    bl_idname = "gob.open_folder"
    bl_label = "Open GoB Folder"
    bl_description = "Open the GoB shared folder in the system file explorer"

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

        self.report({'ERROR'}, "[GoB] Cannot open folder")
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
    bl_description = "Automatically import new files when CLO exports to the shared folder"

    def execute(self, context):
        if watcher.is_polling():
            watcher.stop_polling()
            self.report({'INFO'}, "[GoB] Auto-Import OFF")
        else:
            watcher.start_polling()
            self.report({'INFO'}, "[GoB] Auto-Import ON — files exported from CLO will be imported automatically")
        return {'FINISHED'}


class GOB_OT_clear_all_history(bpy.types.Operator):
    """모든 GoB 임시 데이터를 수동으로 지우는 기능"""
    bl_idname = "gob.clear_all_history"
    bl_label = "Delete All GoB Temp Data"
    bl_description = "WARNING: Permanently deletes all GoB_* export folders and loose files from the shared folder"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        import shutil
        prefs = context.preferences.addons[__package__].preferences
        gob_path = prefs.gob_folder_path
        
        folder = core.ensure_gob_folder(gob_path)
        if not folder:
            return {'CANCELLED'}
            
        folders = core.get_history_folders(folder)
        deleted = 0
        for f in folders:
            try:
                shutil.rmtree(f)
                deleted += 1
            except Exception as e:
                self.report({'WARNING'}, f"Delete failed: {os.path.basename(f)} - {e}")
                
        # 루트에 떠도는 manifest나 예전 OBJ도 함께 삭제
        core.clean_gob_folder(folder)

        self.report({'INFO'}, f"[GoB] {deleted} export folder(s) deleted.")
        return {'FINISHED'}


# ── 등록 ──────────────────────────────────────────────

classes = (
    GOB_OT_import_from_clo,
    GOB_OT_send_to_clo,
    GOB_OT_open_folder,
    GOB_OT_toggle_watch,
    GOB_OT_clear_all_history,
)
