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


def copy_to_gob(src_files, gob_folder):
    """
    Export 결과 파일들을 GoB 공유 폴더로 복사.
    OBJ와 동일 폴더의 관련 파일(MTL, 텍스처 이미지)도 함께 복사.
    Returns: GoB 폴더에 복사된 파일 경로 리스트.
    """
    copied = []
    seen_dirs = set()

    for src in src_files:
        src_dir = os.path.dirname(src)

        # 1) Export API가 반환한 파일 복사
        dst = os.path.join(gob_folder, os.path.basename(src))
        try:
            shutil.copy2(src, dst)
            copied.append(dst)
            print(f"[GoB] COPY {os.path.basename(src)}")
        except OSError as e:
            print(f"[GoB] ERROR copy {os.path.basename(src)}: {e}")

        # 2) 같은 폴더의 텍스처/MTL 파일도 함께 복사 (중복 방지)
        if src_dir not in seen_dirs:
            seen_dirs.add(src_dir)
            tex_extensions = {".png", ".jpg", ".jpeg", ".tga", ".bmp", ".tiff", ".mtl"}
            for filename in os.listdir(src_dir):
                ext = os.path.splitext(filename)[1].lower()
                if ext in tex_extensions:
                    tex_src = os.path.join(src_dir, filename)
                    tex_dst = os.path.join(gob_folder, filename)
                    if tex_dst not in copied:
                        try:
                            shutil.copy2(tex_src, tex_dst)
                            copied.append(tex_dst)
                            print(f"[GoB] COPY {filename}")
                        except OSError as e:
                            print(f"[GoB] ERROR copy {filename}: {e}")

    return copied


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

    # Export Dialog 표시 — 유저가 스케일/텍스처/UV 등 직접 설정
    print("[GoB] INFO Opening Export Dialog...")
    try:
        result = export_api.ExportOBJ()
    except Exception as e:
        print(f"[GoB] ERROR: {e}")
        return

    if not result:
        print("[GoB] INFO Export cancelled or failed")
        return

    print(f"[GoB] INFO Exported {len(result)} file(s)")

    # Export 결과 파일(OBJ + MTL + 텍스처)을 GoB 폴더로 복사
    copied = copy_to_gob(result, GOB_FOLDER)

    # Manifest 작성 (OBJ만 기록)
    objs = [f for f in copied if f.lower().endswith(".obj")]
    if objs:
        write_manifest(objs, GOB_FOLDER)

    print(f"[GoB] === Done: {len(copied)} file(s) copied to GoB folder ===")


main()
