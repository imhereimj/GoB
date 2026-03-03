# GoB — CLO ↔ Blender Bridge (v0.2.1 Beta)

⚡ Fast Bridge between CLO and Blender  
🎨 Automatic PBR Shader Setup  
📦 UDIM Support  
🔄 Folder-Based Auto Import  
🗂 Export Folder Auto Cleanup  

> 🚧 **Beta** — 現在積極的に開発中です。

GoBは、CLOからBlenderへ3D衣装データを素早く転送するためのブリッジアドオンです。  
テクスチャ（Diffuse, Normal, Roughness, Metalness, Opacity）を自動検出し、Principled BSDFに自動接続します。UDIMにも対応しています。

---

## Status

- ✅ CLO → Blender (OBJ + MTL + Texture + UDIM)
- ✅ ファイル名ベースのAuto Shader
- ✅ 共有フォルダによるAuto Import
- ✅ Exportフォルダ自動整理
- ✅ Debug Log生成
- ⚠️ Blender → CLO: OBJ Exportのみ対応
- ⚠️ FBX: UIあり（機能未完成）

---

## テクスチャ自動検出（現在の実装）

| ファイル名キーワード | 接続先 |
|----------------------|--------|
| `diffuse` | Base Color |
| `normal` | Normal |
| `roughness` | Roughness |
| `metalness` | Metallic |
| `opacity` | Alpha |

---

## 必要環境

- Blender 3.6+
- CLO 2025+
- Windows / macOS

---

## License

MIT License © 2026 Jaeyong Lee
