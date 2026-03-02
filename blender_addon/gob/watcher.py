"""
GoB Watcher - shared folder auto-polling module.

bpy.app.timers를 사용하여 GoB 공유 폴더를 주기적으로 감시.
watcher 시작 시점 이후에 새로 들어온 OBJ/FBX만 자동 Import.
"""

import os
import time
import bpy

from . import core

# ── 상태 관리 ──────────────────────────────────────────

# watcher 시작 시간 (이 시간 이후에 수정된 파일만 Import)
_start_time = 0.0
# 이미 Import 완료한 파일 {경로: mtime}
_known_files = {}
# 폴링 활성화 여부
_polling_active = False
# 폴링 간격 (초)
POLL_INTERVAL = 1.0


def _poll_gob_folder():
    """
    타이머 콜백.
    watcher 시작 이후에 새로 생긴/수정된 파일만 Import.
    기존에 있던 파일은 절대 건드리지 않음.
    """
    global _polling_active

    if not _polling_active:
        return None

    try:
        prefs = bpy.context.preferences.addons["gob"].preferences
        gob_path = prefs.gob_folder_path
    except (KeyError, AttributeError):
        gob_path = core.DEFAULT_GOB_PATH

    if not os.path.isdir(gob_path):
        return POLL_INTERVAL

    mesh_extensions = {".obj", ".fbx"}
    new_files = []

    for filename in os.listdir(gob_path):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in mesh_extensions:
            continue

        filepath = os.path.join(gob_path, filename)
        if not os.path.isfile(filepath):
            continue

        try:
            mtime = os.path.getmtime(filepath)
        except OSError:
            continue

        # watcher 시작 이전 파일은 무시
        if mtime <= _start_time:
            continue

        # 이미 Import한 파일이면 스킵
        if _known_files.get(filepath) == mtime:
            continue

        new_files.append((filepath, mtime))

    if not new_files:
        return POLL_INTERVAL

    # operators.py의 공용 Import + Auto-Shader 함수 사용
    from . import operators

    imported = 0
    for filepath, mtime in new_files:
        try:
            if operators.import_and_setup(filepath):
                imported += 1
            _known_files[filepath] = mtime
        except Exception as e:
            print(f"[GoB Watcher] Import error: {filepath} - {e}")

    if imported > 0:
        print(f"[GoB Watcher] Auto-imported {imported} object(s)")

    return POLL_INTERVAL


# ── 폴링 제어 ──────────────────────────────────────────

def start_polling():
    """폴링 시작. 이 시점 이후에 새로 들어온 파일만 Import."""
    global _polling_active, _start_time, _known_files

    if _polling_active:
        return

    _polling_active = True
    _start_time = time.time()
    _known_files.clear()

    bpy.app.timers.register(_poll_gob_folder, first_interval=POLL_INTERVAL)
    print(f"[GoB Watcher] Polling started (ignoring existing files)")


def stop_polling():
    """폴링 중지."""
    global _polling_active
    _polling_active = False
    print("[GoB Watcher] Polling stopped")


def is_polling():
    """폴링 활성 여부."""
    return _polling_active
