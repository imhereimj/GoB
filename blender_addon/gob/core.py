import os
import platform
from datetime import datetime


# ── 버전 및 상수 ──────────────────────────────────────────
VERSION = "0.2.0-beta"

def get_default_gob_path():
    """OS별 기본 GoB 공유 폴더 경로 반환."""
    if platform.system() == "Darwin":  # macOS
        return "/Users/Shared/GoB"
    else:  # Windows
        return os.path.join("C:\\Users\\Public", "GoB")

DEFAULT_GOB_PATH = get_default_gob_path()
MANIFEST_FILE = "GoB_ObjectList.txt"

# 전송 방향 상수
DIR_CLO_TO_BLENDER = "CLO_TO_BLENDER"
DIR_BLENDER_TO_CLO = "BLENDER_TO_CLO"


# ── 공유 폴더 관리 ──────────────────────────────────────

def ensure_gob_folder(gob_path=None):
    """
    GoB 공유 폴더가 존재하는지 확인하고, 없으면 생성.
    GoZ의 GoZProjects 폴더와 동일한 역할.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    try:
        os.makedirs(folder, exist_ok=True)
        return folder
    except OSError as e:
        print(f"[GoB ERROR] 공유 폴더 생성 실패: {folder} — {e}")
        return None


def clean_gob_folder(gob_path=None):
    """
    공유 폴더의 이전 교환 파일을 정리.
    매 전송 전에 호출하여 깨끗한 상태 유지.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    if not os.path.isdir(folder):
        return

    safe_extensions = {".obj", ".mtl", ".fbx", ".png", ".jpg", ".txt"}
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            ext = os.path.splitext(filename)[1].lower()
            if ext in safe_extensions:
                try:
                    os.remove(filepath)
                except OSError:
                    pass


# ── Manifest (GoB_ObjectList.txt) ──────────────────────

def write_manifest(file_paths, direction, gob_path=None, fmt="obj"):
    """
    GoB_ObjectList.txt 작성 — GoZ의 GoZ_ObjectList.txt와 동일 역할.
    교환할 파일 목록과 메타데이터를 기록.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    manifest_path = os.path.join(folder, MANIFEST_FILE)
    timestamp = datetime.now().isoformat()

    lines = [
        "# GoB Object List",
        f"# direction: {direction}",
        f"# timestamp: {timestamp}",
        f"# format: {fmt}",
        "#",
    ]
    for fp in file_paths:
        lines.append(fp)

    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return manifest_path
    except OSError as e:
        print(f"[GoB ERROR] Manifest 쓰기 실패: {e}")
        return None


def read_manifest(gob_path=None):
    """
    GoB_ObjectList.txt 읽기.

    Returns:
        dict: {"direction", "timestamp", "format", "files": [...]}
        또는 에러 시 None
    """
    folder = gob_path or DEFAULT_GOB_PATH
    manifest_path = os.path.join(folder, MANIFEST_FILE)

    if not os.path.isfile(manifest_path):
        return None

    result = {
        "direction": "",
        "timestamp": "",
        "format": "obj",
        "files": [],
    }

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("# direction:"):
                    result["direction"] = line.split(":", 1)[1].strip()
                elif line.startswith("# timestamp:"):
                    result["timestamp"] = line.split(":", 1)[1].strip()
                elif line.startswith("# format:"):
                    result["format"] = line.split(":", 1)[1].strip()
                elif line.startswith("#"):
                    continue
                else:
                    if os.path.isfile(line):
                        result["files"].append(line)
        return result
    except OSError as e:
        print(f"[GoB ERROR] Manifest 읽기 실패: {e}")
        return None


def get_gob_files(gob_path=None):
    """
    공유 폴더에서 OBJ/FBX 파일 목록을 직접 스캔.
    Manifest 없이도 사용 가능.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    if not os.path.isdir(folder):
        return []

    mesh_extensions = {".obj", ".fbx"}
    files = []
    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext in mesh_extensions:
            files.append(os.path.join(folder, filename))
    return files
