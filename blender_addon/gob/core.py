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
LOG_FILE = "GoB_debug.log"

# 전송 방향 상수
DIR_CLO_TO_BLENDER = "CLO_TO_BLENDER"
DIR_BLENDER_TO_CLO = "BLENDER_TO_CLO"


# ── 로그 ────────────────────────────────────────────────

def gob_log(message, gob_path=None):
    """
    GoB_debug.log 파일에 타임스탬프와 함께 메시지를 추가.
    디버깅 목적 — 공유 폴더에 저장되어 외부에서 확인 가능.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    log_path = os.path.join(folder, LOG_FILE)
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{timestamp}] {message}\n"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    print(f"[GoB] {message}")


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
        print(f"[GoB ERROR] Failed to create shared folder: {folder} — {e}")
        return None


def clean_gob_folder(gob_path=None):
    """
    공유 폴더의 이전 교환 파일을 정리 (루트 경로만 정리).
    하위 폴더(CLO가 만든 격리 폴더)는 유지하여, 다른 작업물과 충돌하지 않게 함.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    if not os.path.isdir(folder):
        return

    safe_extensions = {".obj", ".mtl", ".fbx", ".png", ".jpg", ".txt", ".zprj"}
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            ext = os.path.splitext(filename)[1].lower()
            if ext in safe_extensions:
                try:
                    os.remove(filepath)
                except OSError:
                    pass

def get_history_folders(gob_path=None):
    """
    GoB 공유 폴더 내에 생성된 GoB_* 형태의 하위 폴더 목록을 반환.
    수정 시간 기준 오름차순(가장 오래된 것이 먼저)으로 정렬됨.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    if not os.path.isdir(folder):
        return []
    
    folders = []
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path) and item.startswith("GoB_"):
            folders.append(item_path)
            
    # 오래된 폴더가 맨 앞에 오도록 정렬
    folders.sort(key=lambda x: os.path.getmtime(x))
    return folders

def enforce_folder_limit(max_count=5, gob_path=None):
    """
    history 폴더 개수가 max_count를 초과하면 가장 오래된 폴더부터 삭제.
    """
    folders = get_history_folders(gob_path)
    if len(folders) <= max_count:
        return
        
    num_to_delete = len(folders) - max_count
    import shutil
    
    for i in range(num_to_delete):
        del_path = folders[i]
        print(f"[GoB] INFO Removing old history folder: {os.path.basename(del_path)}")
        try:
            shutil.rmtree(del_path)
        except Exception as e:
            print(f"[GoB] WARNING Failed to delete old folder {del_path}: {e}")


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
        print(f"[GoB ERROR] Failed to write manifest: {e}")
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
        print(f"[GoB ERROR] Failed to read manifest: {e}")
        return None


def get_gob_files(gob_path=None):
    """
    공유 폴더에서 OBJ/FBX 파일 목록을 재귀적으로 스캔합니다.
    (새로운 격리 폴더 구조 지원) — 모든 하위 폴더의 파일 반환.
    """
    folder = gob_path or DEFAULT_GOB_PATH
    if not os.path.isdir(folder):
        return []

    mesh_extensions = {".obj", ".fbx"}
    files = []
    
    # 하위 폴더까지 모두 검색 (os.walk)
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in mesh_extensions:
                files.append(os.path.join(root, filename))
                
    # 가장 최근에 수정된 파일 순서대로 정렬
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files


def get_latest_gob_files(gob_path=None):
    """
    가장 최신 GoB_* 서브폴더 1개 내의 OBJ/FBX 파일만 반환.
    Manifest가 없을 때 폴백으로 사용. 복수 폴더 중복 Import 방지.
    """
    folders = get_history_folders(gob_path)
    if not folders:
        return []
    
    # get_history_folders는 오래된순 정렬 → 마지막이 가장 최신
    latest_folder = folders[-1]
    mesh_extensions = {".obj", ".fbx"}
    files = []
    
    for filename in os.listdir(latest_folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext in mesh_extensions:
            files.append(os.path.join(latest_folder, filename))
            
    return files
