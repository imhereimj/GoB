# GoB — CLO ↔ Blender Bridge

**[한국어](README_ko.md) | [日本語](README_jp.md)**

> ⚠️ **Beta** — Currently CLO → Blender transfer is fully supported. Blender → CLO is in early development.

A bridge tool for quickly importing 3D garment data exported from CLO into Blender.  
Automatically detects textures (Diffuse, Normal, Roughness, Metalness, Opacity) and connects them to Principled BSDF shader. UDIM textures are also supported.

## Status

🚧 This project is currently in **Beta**.  
We will continuously improve it through real-world usage.

- ✅ CLO → Blender (OBJ + Textures + UDIM)
- ✅ Auto-Shader based on texture filename keywords
- ✅ Shared folder auto-watch (Auto-Import)
- ⚠️ Blender → CLO: Manual export to shared folder (Automatic import in CLO is coming soon)
- 🔜 FBX format support

Bug reports and suggestions are welcome in [Issues](../../issues).

---

## Prerequisites

GoB exchanges files between CLO and Blender through a **shared folder**.  
Please create the following folder before first use:

```
C:\Users\Public\GoB\
```

> 💡 The folder is auto-created when the script runs, but creating it beforehand is recommended to avoid permission issues.

---

## Installation — Blender Add-on

1. Copy the `blender_addon/gob/` folder to Blender's addons path:
   ```
   %APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\
   ```
   Example (Blender 5.0):
   ```
   C:\Users\<username>\AppData\Roaming\Blender Foundation\Blender\5.0\scripts\addons\gob\
   ```
2. Open Blender → **Edit → Preferences → Add-ons**
3. Search `GoB` → Enable **GoB — CLO Bridge**

---

## Installation — CLO Script

### Option 1: Run from Script Editor

1. Save `clo_script/GoB_Send.py` to any location
2. Open CLO → **Script Editor**
3. Open `GoB_Send.py`
4. Click **Run** whenever needed

### Option 2: Register in Plug-in Manager (Recommended)

1. CLO top menu → **Plugins → Plug-in Manager**
2. Register `GoB_Send.py` as a plugin
3. Run directly from **Plugins → Plug-in** menu

> 💡 Registering in Plug-in Manager lets you run with one click from the menu without opening Script Editor.

---

## Usage

### CLO → Blender

1. Run `GoB_Send.py` in CLO Script Editor
2. **Export Dialog** appears → Set scale, textures, UV, etc. and click OK
3. OBJ + MTL + textures are automatically copied to `C:/Users/Public/GoB/`
4. Blender → 3D Viewport → N-key sidebar → **GoB** tab → **Get from CLO**

### Auto-Import

Toggle **Auto-Import** in the GoB panel → Objects are automatically imported when CLO exports.

---

## Features

| Feature | Description |
|---------|-------------|
| Export Dialog | Customize settings in CLO's built-in Export UI |
| Auto-Shader | Auto-connect textures to Principled BSDF based on filename |
| UDIM Support | Auto-detect `name.1001.png` ~ `name.100N.png` patterns |
| Auto-Import | Watch shared folder + auto import |
| Drag & Drop | Drop `.zprj` files into Blender viewport |

## Texture Auto-Detection Keywords

| Filename Keyword | Principled BSDF Socket |
|:----------------|:----------------------|
| `diffuse`, `basecolor`, `albedo` | Base Color |
| `normal` | Normal (Normal Map node auto-inserted) |
| `roughness` | Roughness |
| `metalness`, `metallic` | Metallic |
| `opacity`, `alpha` | Alpha |

---

## Shared Folder

Default path: `C:/Users/Public/GoB/`

To change the path, update **both sides**:

| Side | How to Change |
|------|--------------|
| **CLO** | Edit `GOB_FOLDER` variable at the top of `GoB_Send.py` |
| **Blender** | GoB panel → **Settings** → **Folder** |

## Requirements

- **Blender** 5.0+
- **CLO** 2025+
- **OS**: Windows

## Project Structure

```
GoB/
├── blender_addon/
│   └── gob/              ← Blender Add-on
│       ├── __init__.py
│       ├── core.py
│       ├── operators.py
│       ├── preferences.py
│       ├── ui.py
│       └── watcher.py
│
├── clo_script/
│   └── GoB_Send.py        ← CLO Script Editor
│
└── README.md
```

## License

[MIT License](LICENSE) © 2026 Jaeyong Lee
