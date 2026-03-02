# GoB — CLO ↔ Blender Bridge (v0.2.0 Beta)

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
- ✅ **macOS 対応追加**
- ⚠️ Blender → CLO: 共有フォルダへのOBJエクスポート支援（CLOでの自動インポートは今後サポート予定）
- 🔜 FBXフォーマット対応

バグ報告や提案は [Issues](../../issues) へどうぞ。

---

## 事前準備

GoBは**共有フォルダ**を介してCLOとBlender間でファイルをやり取りします。  
初回使用前に以下のフォルダを作成してください：

### Windows:
```
C:\Users\Public\GoB\
```

### macOS:
```
/Users/Shared/GoB/
```

> 💡 スクリプト実行時に自動作成されますが、権限問題を防ぐため事前に作成しておくことを推奨します。

---

## インストール — Blender Add-on

### 方法 1：ZIP ファイルからインストール（推奨）

1. [Releases](../../releases) ページから **`GoB_v0.2.0_Beta.zip`** （フルパッケージ）をダウンロードして解凍します。
2. `blender_addon/` フォルダ内の **`gob/` フォルダのみを選択して、再度 ZIP 形式で圧縮**します（例：`gob.zip`）。
3. Blenderを起動 → **Edit → Preferences → Add-ons**
4. 右上の **矢印/歯車アイコン**（または Install ボタン）をクリック → **Install from Disk...** を選択
5. 先ほど作成した `gob.zip` を選択して **Install** をクリックします。
6. `GoB` で検索 → **GoB — CLO Bridge** にチェックを入れて有効化

### 方法 2：手動インストール（フォルダコピー）

1. 解凍したパッケージの `blender_addon/gob/` フォルダを以下のパスにコピーします：
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\<バージョン>\scripts\addons\gob\`
   - **macOS**: `~/Library/Application Support/Blender/<バージョン>/scripts/addons/gob/`
2. Blenderを起動 → **Edit → Preferences → Add-ons** → `GoB` で検索して有効化

---

## インストール — CLO Script

### 方法 1：Script Editorから直接実行

1. `clo_script/GoB_Send.py` を任意の場所に保存します。
2. CLOを起動 → **Script Editor** を開きます。
3. `GoB_Send.py` を開きます。
4. 必要な時に **Run** ボタンを押して実行します。

### 方法 2：Plug-in Managerに登録（推奨）

1. CLO上部メニュー → **Plugins → Plug-in Manager** をクリックします。
2. `GoB_Send.py` をプラグインとして登録します。
3. 登録後、**Plugins → Plug-in** メニューから直接実行可能です。

> 💡 Plug-in Managerに登録すると、Script Editorを開かずにメニューからワンクリックで実行できます。

---

## 使い方

### CLO → Blender

1. CLO Script Editorで `GoB_Send.py` を実行します。
2. **Export Dialog** が表示されます → スケール、テクスチャ、UVなど必要な設定を行って OK をクリックします。
3. OBJ + MTL + テクスチャが自動的に**共有フォルダ**（`C:/Users/Public/GoB/` または `/Users/Shared/GoB/`）にコピーされます。
4. Blender → 3D Viewport → Nキーサイドバー → **GoB** タブ → **Get from CLO** をクリックします。

### Auto-Import

GoBパネルで **Auto-Import** を有効化します → CLOからエクスポートすると自動的にBlenderにインポートされます。

---

## 機能

| 機能 | 説明 |
|------|------|
| Export Dialog | CLO内蔵のエクスポートUIで設定をカスタマイズ可能 |
| Auto-Shader | テクスチャファイル名に基づいてPrincipled BSDFに自動接続 |
| UDIM対応 | `name.1001.png` 〜 `name.100N.png` パターンを自動検出 |
| Auto-Import | 共有フォルダを自動監視し、自動インポート |

## テクスチャ自動検出キーワード

| ファイル名キーワード | Principled BSDF ソケット |
|:-------------------|:------------------------|
| `diffuse`, `basecolor`, `albedo` | Base Color |
| `normal` | Normal（Normal Mapノードを自動挿入） |
| `roughness` | Roughness |
| `metalness`, `metallic` | Metallic |
| `opacity`, `alpha` | Alpha |

---

## 共有フォルダ

デフォルトパス：
- **Windows**: `C:/Users/Public/GoB/`
- **macOS**: `/Users/Shared/GoB/`

> [!TIP]
> このフォルダにはエクスポートするたびに3Dデータやテクスチャが蓄積されます。ストレージ容量節約のため、**定期的にフォルダ内を整理**することをお勧めします。

パスを変更する場合は**両方を合わせる**必要があります：

| 側 | 変更方法 |
|---|---------|
| **CLO** | `GoB_Send.py` 上部の `GOB_FOLDER` 変数を修正 |
| **Blender** | GoBパネル → **Settings** → **Folder** で変更 |

## 動作環境

- **Blender**: 5.0+ (Windows 動作確認済み), 4.5+ (macOS Intel 動作確認済み)
- **CLO**: 2025+
- **OS**: Windows / macOS

## プロジェクト構造

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
