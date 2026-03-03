# GoB — CLO ↔ Blender Bridge (v0.2.1)

**[English](README.md) | [日本語](README_jp.md) | [한국어](README_ko.md)**

⚡ Fast Bridge between CLO and Blender  
🎨 Automatic PBR Shader Setup  
📦 UDIM Support  
🔄 Folder-Based Auto Import  
🗂 Export Folder Auto Cleanup  

> 🚧 **Beta** — Actively developed and improving.

GoB is a bridge add-on that transfers 3D garment data exported from CLO into Blender quickly and cleanly.  
It auto-detects textures (Diffuse, Normal, Roughness, Metalness, Opacity) and connects them to a Principled BSDF shader. UDIM textures are supported.

---

## Status

- ✅ CLO → Blender (OBJ + MTL + Texture + UDIM)
- ✅ Filename-based Auto Shader
- ✅ Folder-based Auto Import
- ✅ Export folder auto cleanup
- ✅ Debug log generation
- ⚠️ Blender → CLO: OBJ export only (CLO auto-import not supported)
- ⚠️ FBX: UI exists (feature not completed)

---

## Shared Folder (Prerequisite)

GoB exchanges files via a **shared folder**. Default path is auto-selected by OS.

**Windows**
```
C:\Users\Public\GoB\
```

**macOS**
```
/Users/Shared/GoB/
```

> If you change the path, make sure **Blender Add-on** and **CLO script** use the same folder.

---

## Install — Blender Add-on

### Option 1: Install from ZIP (Recommended)

1. Download the latest ZIP from GitHub Releases
2. Unzip it
3. Re-zip only `blender_addon/gob/` as `gob.zip`
4. Blender → Edit → Preferences → Add-ons
5. Install from Disk… → select `gob.zip`
6. Enable **GoB**

### Option 2: Manual Install

Copy `blender_addon/gob/` to:

**Windows**
```
%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\
```

**macOS**
```
~/Library/Application Support/Blender/<version>/scripts/addons/
```

Then enable GoB in Add-ons.

---

## Install — CLO Script

### Run via Script Editor

1. Save `clo_script/GoB_Send.py`
2. CLO → Script Editor → Open file
3. Click **Run**

### Register via Plug-in Manager (Recommended)

1. CLO → Plugins → Plug-in Manager
2. Register `GoB_Send.py`
3. Run it from Plugins menu

---

## Usage

### CLO → Blender

1. Run `GoB_Send.py` in CLO
2. Configure Export Dialog → OK
3. OBJ + MTL + textures are written to the shared folder
4. Blender → 3D View → N-panel → GoB → **Get from CLO**

### Auto Import

Enable **Auto-Import** in GoB panel.  
When CLO exports, Blender imports automatically.

---

## Texture Auto Detection (Current Implementation)

| Filename Keyword | Principled BSDF Socket |
|------------------|------------------------|
| `diffuse` | Base Color |
| `normal` | Normal (Normal Map node is inserted) |
| `roughness` | Roughness |
| `metalness` | Metallic |
| `opacity` | Alpha |

> Only the keywords above are supported in the current implementation.

---

## Add-on Preferences

Blender → Edit → Preferences → Add-ons → GoB

- Shared folder path
- Max export folder history (auto cleanup)
- Export format (OBJ / FBX)
- Show/Hide “Send to CLO” button

---

## Requirements

- Blender 3.6+
- CLO 2025+
- Windows / macOS

---

## License

MIT License © 2026 Jaeyong Lee
