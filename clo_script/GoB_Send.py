"""
GoB_Send.py - CLO -> Blender GoB Export Script

CLO Script Editor에서 실행:
1. Export Dialog 표시 → 유저가 스케일/텍스처/UV 등 직접 설정
2. Export 결과 파일(OBJ + MTL + 텍스처)을 GoB 공유 폴더로 복사
3. GoB_ObjectList.txt 작성 → Blender Auto-Import 트리거

환경: CLO 2025+, Windows, Script Editor.
"""

import os
import shutil
import platform
from datetime import datetime

import export_api
import utility_api

# ── 설정 및 버전 ────────────────────────────────────────────
VERSION = "0.2.0-beta"

def get_default_folder():
    if platform.system() == "Darwin": # macOS
        return "/Users/Shared/GoB"
    return "C:/Users/Public/GoB"

GOB_FOLDER = get_default_folder()
MANIFEST_FILE = "GoB_ObjectList.txt"


# ── 유틸리티 ──────────────────────────────────────────

def get_project_name():
    """현재 프로젝트 이름 반환 (fallback: clo_export)."""
    try:
        path = utility_api.GetProjectFilePath()
        if path:
            name = os.path.splitext(os.path.basename(path))[0]
            if name:
                return name
    except Exception:
        pass
    return "clo_export"


def write_manifest(file_paths, gob_folder):
    """GoB_ObjectList.txt 작성 — Blender Auto-Import 트리거."""
    path = os.path.join(gob_folder, MANIFEST_FILE)
    lines = [
        "# GoB Object List",
        "# direction: CLO_TO_BLENDER",
        f"# timestamp: {datetime.now().isoformat()}",
        "# format: obj",
        "#",
    ]
    lines.extend(file_paths)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as e:
        print(f"[GoB] ERROR manifest: {e}")


# ── 메인 ──────────────────────────────────────────────

def main():
    print("[GoB] === CLO -> Blender Export ===")

    os.makedirs(GOB_FOLDER, exist_ok=True)

    # 1. 고유 프로젝트 이름과 타임스탬프 추출
    prj_name = get_project_name()
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    folder_name = f"GoB_{prj_name}_{timestamp}"
    
    # 2. 안전한 단독 격리 폴더 생성 (예: C:/Users/Public/GoB/GoB_MyShirt_260303_123456)
    target_folder = os.path.join(GOB_FOLDER, folder_name)
    os.makedirs(target_folder, exist_ok=True)
    
    # 3. Export될 파일의 타겟 경로 설정 (OBJ 파일명 지정)
    target_filepath = os.path.join(target_folder, f"GoB_{prj_name}.obj")
    target_filepath = target_filepath.replace("\\", "/")

    # 4. Export Dialog 표시 — 이 경로가 기본값으로 팝업 창에 나타납니다.
    print(f"[GoB] INFO Opening Export Dialog for: {target_filepath}")
    try:
        result = export_api.ExportOBJ(target_filepath)
    except Exception as e:
        print(f"[GoB] ERROR: {e}")
        return

    if not result:
        print("[GoB] INFO Export cancelled or failed")
        # 취소 시 생성했던 빈 격리 폴더 청소
        try:
            if not os.listdir(target_folder):
                os.rmdir(target_folder)
        except:
            pass
        return

    print(f"[GoB] INFO Exported {len(result)} file(s) safely to {folder_name}")

    # 5. Manifest 작성 (격리 폴더에 곧바로 저장되었으므로, 복사(Copy) 불필요)
    # result 배열의 첫 번째 원소는 OBJ 경로를 담고 있습니다.
    objs = [f for f in result if f.lower().endswith(".obj")]
    if objs:
        write_manifest(objs, GOB_FOLDER)

    print(f"[GoB] === Done: {len(result)} file(s) saved ===")


main()
