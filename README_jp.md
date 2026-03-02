# GoB — CLO ↔ Blender Bridge

**[English](README.md) | [한국어](README_ko.md)**

> ⚠️ **Beta** — 現在、CLO → Blender 転送は安定していますが、Blender → CLO は初期開発段階です。


CLOからエクスポートした3Dガーメントデータを素早くBlenderにインポートするブリッジツールです。  
テクスチャ（Diffuse、Normal、Roughness、Metalness、Opacity）をファイル名から自動検出し、Principled BSDFシェーダーに接続します。UDIMテクスチャにも対応しています。

## Status

🚧 このプロジェクトは現在 **Beta** 段階です。  
実際の使用を通じて継続的に改善していく予定です。

- ✅ CLO → Blender（OBJ + テクスチャ + UDIM）
- ✅ テクスチャファイル名ベースのAuto-Shader接続
- ✅ 共有フォルダ自動監視（Auto-Import）
- ⚠️ Blender → CLO: 共有フォルダへのOBJエクスポート支援（CLOでの自動インポートは今後サポート予定）
- 🔜 FBXフォーマット対応

バグ報告や提案は [Issues](../../issues) へどうぞ。

---

## 事前準備

GoBは**共有フォルダ**を介してCLOとBlender間でファイルをやり取りします。  
初回使用前に以下のフォルダを作成してください：

```
C:\Users\Public\GoB\
```

> 💡 スクリプト実行時に自動作成されますが、権限問題を防ぐため事前に作成しておくことを推奨します。

---

## インストール — Blender Add-on

1. `blender_addon/gob/` フォルダを**そのまま**以下のパスにコピーします：
   ```
   %APPDATA%\Blender Foundation\Blender\<バージョン>\scripts\addons\
   ```
   例（Blender 5.0）：
   ```
   C:\Users\<ユーザー名>\AppData\Roaming\Blender Foundation\Blender\5.0\scripts\addons\gob\
   ```
2. Blenderを起動 → **Edit → Preferences → Add-ons**
3. `GoB` で検索 → **GoB — CLO Bridge** にチェックを入れて有効化

---

## インストール — CLO Script

### 方法1：Script Editorで直接実行

1. `clo_script/GoB_Send.py` を任意の場所に保存
2. CLOを起動 → **Script Editor** を開く
3. `GoB_Send.py` を開く
4. 必要な時に **Run** ボタンを押して実行

### 方法2：Plug-in Managerに登録（推奨）

1. CLO上部メニュー → **Plugins → Plug-in Manager** をクリック
2. `GoB_Send.py` をプラグインとして登録
3. 登録後、**Plugins → Plug-in** メニューから直接実行可能

> 💡 Plug-in Managerに登録すると、Script Editorを開かずにメニューからワンクリックで実行できます。

---

## 使い方

### CLO → Blender

1. CLO Script Editorで `GoB_Send.py` を実行
2. **Export Dialog** が表示 → スケール、テクスチャ、UVなどを設定してOKをクリック
3. OBJ + MTL + テクスチャが自動的に `C:/Users/Public/GoB/` にコピーされます
4. Blender → 3D Viewport → Nキーサイドバー → **GoB** タブ → **Get from CLO** をクリック

### Auto-Import

GoBパネルで **Auto-Import** をトグル → CLOからExportすると自動的にBlenderにImportされます。

---

## 機能

| 機能 | 説明 |
|------|------|
| Export Dialog | CLO内蔵Export UIで設定をカスタマイズ |
| Auto-Shader | テクスチャファイル名ベースでPrincipled BSDFに自動接続 |
| UDIM対応 | `name.1001.png` 〜 `name.100N.png` パターンを自動検出 |
| Auto-Import | 共有フォルダ自動監視 + 自動Import |
| Drag & Drop | `.zprj` ファイルをBlenderビューポートにドロップ可能 |

## テクスチャ自動検出キーワード

| ファイル名キーワード | Principled BSDF ソケット |
|:-------------------|:------------------------|
| `diffuse`, `basecolor`, `albedo` | Base Color |
| `normal` | Normal（Normal Mapノード自動挿入） |
| `roughness` | Roughness |
| `metalness`, `metallic` | Metallic |
| `opacity`, `alpha` | Alpha |

---

## 共有フォルダ

デフォルトパス：`C:/Users/Public/GoB/`

パスを変更する場合は**両方を合わせる**必要があります：

| 側 | 変更方法 |
|---|---------|
| **CLO** | `GoB_Send.py` 上部の `GOB_FOLDER` 変数を修正 |
| **Blender** | GoBパネル → **Settings** → **Folder** で変更 |

## 動作環境

- **Blender** 5.0+
- **CLO** 2025+
- **OS**: Windows

## License

[MIT License](LICENSE) © 2026 Jaeyong Lee
