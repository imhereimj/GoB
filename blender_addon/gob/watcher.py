"""
GoB Watcher - shared folder auto-polling module.

Polls the GoB shared folder using bpy.app.timers.
CLO writes files in stages (mtime changes multiple times).
Stability Check: only imports a file when mtime is unchanged across 2 consecutive polls.
"""

import os
import time
import bpy

from . import core

# ── State ──────────────────────────────────────────────

# Watcher start time — only detect files newer than this
_start_time = 0.0

# Already-imported files {abs_path: mtime}
# Files imported manually via Get from CLO are also registered here to prevent re-import
_known_files = {}

# Files currently being written by CLO {abs_path: mtime from last poll}
# Only import when mtime is the same across 2 consecutive polls (Stability Check)
_pending_files = {}

# Whether polling is active
_polling_active = False

# Poll interval in seconds
POLL_INTERVAL = 1.0


def register_imported_files(file_paths):
    """
    Register manually-imported files (Get from CLO) into _known_files.
    Without this, the watcher treats them as unseen and re-imports them.
    """
    for filepath in file_paths:
        try:
            mtime = os.path.getmtime(filepath)
            _known_files[filepath] = mtime
            _pending_files.pop(filepath, None)
            core.gob_log(f"[Watcher] Registered as known: {os.path.basename(filepath)}")
        except OSError:
            pass


def _poll_gob_folder():
    """
    Timer callback.
    Stability Check: import only when a file's mtime is unchanged across 2 consecutive polls.
    Prevents multiple imports caused by CLO writing files in multiple stages.
    """
    global _polling_active

    if not _polling_active:
        return None

    try:
        prefs = bpy.context.preferences.addons["gob"].preferences
        gob_path = prefs.gob_folder_path
        max_history = prefs.max_folder_history
    except (KeyError, AttributeError):
        gob_path = core.DEFAULT_GOB_PATH
        max_history = 5

    if not os.path.isdir(gob_path):
        return POLL_INTERVAL

    # Auto-clean oldest folders when exceeding the history limit
    core.enforce_folder_limit(max_history, gob_path)

    mesh_extensions = {".obj", ".fbx"}
    ready_to_import = []  # Files that passed Stability Check
    current_mtimes = {}   # mtime snapshot from this poll cycle

    # Recursive scan including sub-folders (os.walk)
    for root_dir, _, filenames in os.walk(gob_path):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in mesh_extensions:
                continue

            filepath = os.path.join(root_dir, filename)
            if not os.path.isfile(filepath):
                continue

            try:
                mtime = os.path.getmtime(filepath)
            except OSError:
                continue

            # Skip files older than watcher start time
            if mtime <= _start_time:
                continue

            # Skip already-imported files (including manual Get from CLO)
            if _known_files.get(filepath) == mtime:
                continue

            current_mtimes[filepath] = mtime

            # ── Stability Check ──
            # If mtime matches the previous poll → file write complete → ready to import
            if _pending_files.get(filepath) == mtime:
                core.gob_log(f"[Watcher] Stable — queued for import: {os.path.relpath(filepath, gob_path)}")
                ready_to_import.append((filepath, mtime))
            else:
                # New file or mtime changed — still being written, wait next poll
                core.gob_log(f"[Watcher] Pending (mtime changed): {os.path.relpath(filepath, gob_path)}")
                _pending_files[filepath] = mtime

    # Clean up pending entries no longer visible this poll
    for fp in list(_pending_files.keys()):
        if fp not in current_mtimes and fp not in _known_files:
            _pending_files.pop(fp, None)

    if not ready_to_import:
        return POLL_INTERVAL

    core.gob_log(f"[Watcher] Starting import — {len(ready_to_import)} file(s) stable")

    from . import operators

    imported = 0
    for filepath, mtime in ready_to_import:
        try:
            core.gob_log(f"[Watcher] Importing: {os.path.basename(filepath)}")
            if operators.import_and_setup(filepath):
                imported += 1
            # Move from pending to known after successful import
            _known_files[filepath] = mtime
            _pending_files.pop(filepath, None)
        except Exception as e:
            core.gob_log(f"[Watcher] Import error: {os.path.basename(filepath)} -> {e}")
            print(f"[GoB Watcher] Import error: {filepath} - {e}")

    if imported > 0:
        core.gob_log(f"[Watcher] Auto-import complete: {imported} object(s)")
        print(f"[GoB Watcher] Auto-imported {imported} object(s)")

    return POLL_INTERVAL


# ── Polling Control ────────────────────────────────────

def start_polling():
    """Start polling. Only files created after this point will be imported."""
    global _polling_active, _start_time, _known_files, _pending_files

    if _polling_active:
        return

    _polling_active = True
    _start_time = time.time()
    _known_files.clear()
    _pending_files.clear()

    bpy.app.timers.register(_poll_gob_folder, first_interval=POLL_INTERVAL)
    core.gob_log(f"[Watcher] Polling started — start_time={_start_time:.2f}")
    print("[GoB Watcher] Polling started (ignoring existing files)")


def stop_polling():
    """Stop polling."""
    global _polling_active
    _polling_active = False
    core.gob_log("[Watcher] Polling stopped")
    print("[GoB Watcher] Polling stopped")


def is_polling():
    """Return whether polling is currently active."""
    return _polling_active
