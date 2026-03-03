# GoB — CLO ↔ Blender Bridge (v0.2.1 Beta)
**[한국어](README_ko.md) | [日本語](README_jp.md)**

⚡ Fast Bridge between CLO and Blender  
🎨 Automatic PBR Shader Setup  
📦 UDIM Support  
🔄 Folder-Based Auto Import  
🗂 Export Folder Auto Cleanup  

> 🚧 **Beta** — Actively developed and improving.

GoB is a bridge add-on that transfers 3D garment data from CLO to Blender quickly and cleanly.  
Textures (Diffuse, Normal, Roughness, Metalness, Opacity) are automatically detected and connected to a Principled BSDF shader. UDIM textures are supported.

---

## Status

- ✅ CLO → Blender (OBJ + MTL + Texture + UDIM)
- ✅ Filename-based Auto Shader
- ✅ Folder-based Auto Import
- ✅ Export Folder Auto Cleanup
- ✅ Debug Log generation
- ⚠️ Blender → CLO: OBJ export only (no auto-import in CLO)
- ⚠️ FBX: UI exists (feature not completed)

---

## Texture Auto Detection (Current Implementation)

| Filename Keyword | Principled BSDF Socket |
|------------------|------------------------|
| `diffuse` | Base Color |
| `normal` | Normal |
| `roughness` | Roughness |
| `metalness` | Metallic |
| `opacity` | Alpha |

---

## Requirements

- Blender 3.6+
- CLO 2025+
- Windows / macOS

---

## License

MIT License © 2026 Jaeyong Lee
