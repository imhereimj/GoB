# GoB — CLO ↔ Blender Bridge (v0.2.1)

**[English](README.md) | [日本語](README_jp.md) | [한국어](README_ko.md)**

⚡ Fast Bridge between CLO and Blender  
🎨 Automatic PBR Shader Setup  
📦 UDIM Support  
🔄 Folder-Based Auto Import  
🗂 Export Folder Auto Cleanup  

> 🚧 **Beta** — 現在積極的に開発・改善中です。

GoBは、CLOからBlenderへ3D衣装データを素早く転送するためのブリッジアドオンです。  
テクスチャ（Diffuse, Normal, Roughness, Metalness, Opacity）を自動検出し、Principled BSDFに自動接続します。UDIMにも対応しています。

---

## Status

- ✅ CLO → Blender (OBJ + MTL + Texture + UDIM)
- ✅ ファイル名ベースのAuto Shader
- ✅ 共有フォルダによるAuto Import
- ✅ Exportフォルダ自動整理
- ✅ Debug Log生成
- ⚠️ Blender → CLO: OBJ Exportのみ（CLO自動Importは未対応）
- ⚠️ FBX: UIあり（機能未完成）

---

## 事前準備（共有フォルダ）

GoBは **共有フォルダ** 経由でファイルをやり取りします。OSにより既定パスが自動設定されます。

**Windows**
```
C:\Users\Public\GoB\
```

**macOS**
```
/Users/Shared/GoB/
```

※ パス変更する場合は、Blender側とCLO側を同じにしてください。

---

## インストール — Blender Add-on

### 方法1：ZIPからインストール（推奨）

1. GitHub Releasesから最新版ZIPをダウンロード
2. 解凍
3. `blender_addon/gob/` だけを再度ZIP化（例：gob.zip）
4. Blender → Edit → Preferences → Add-ons
5. Install from Disk… → `gob.zip`
6. GoBを有効化

### 方法2：手動インストール

`blender_addon/gob/` を以下へコピー：

**Windows**
```
%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\
```

**macOS**
```
~/Library/Application Support/Blender/<version>/scripts/addons/
```

その後、Add-onsでGoBを有効化。

---

## インストール — CLO Script

### Script Editorで実行

1. `clo_script/GoB_Send.py` を保存
2. CLO → Script Editor → ファイルを開く
3. **Run** をクリック

### Plug-in Managerに登録（推奨）

1. CLO → Plugins → Plug-in Manager
2. `GoB_Send.py` を登録
3. Pluginsメニューから実行

---

## 使い方

### CLO → Blender

1. CLOで `GoB_Send.py` を実行
2. Export Dialog設定 → OK
3. 共有フォルダにOBJ + MTL + テクスチャが出力
4. Blender → Nパネル → GoB → **Get from CLO**

### Auto Import

GoBパネルで **Auto-Import** をONにすると、CLOのExport後にBlenderへ自動Importされます。

---

## テクスチャ自動検出（現在の実装）

| ファイル名キーワード | 接続先 |
|----------------------|--------|
| `diffuse` | Base Color |
| `normal` | Normal（Normal Mapノード挿入） |
| `roughness` | Roughness |
| `metalness` | Metallic |
| `opacity` | Alpha |

---

## Add-on Preferences

Blender → Edit → Preferences → Add-ons → GoB

- 共有フォルダパス
- Exportフォルダ履歴数（自動整理）
- Export形式（OBJ / FBX）
- “Send to CLO”ボタン表示切替

---

## 必要環境

- Blender 3.6+
- CLO 2025+
- Windows / macOS

---

## License

MIT License © 2026 Jaeyong Lee
