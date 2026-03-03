# GoB — CLO ↔ Blender Bridge (v0.2.1)

**[English](README.md) | [日本語](README_jp.md) | [한국어](README_ko.md)**

⚡ Fast Bridge between CLO and Blender  
🎨 Automatic PBR Shader Setup  
📦 UDIM Support  
🔄 Folder-Based Auto Import  
🗂 Export Folder Auto Cleanup  

> 🚧 **Beta** — 현재 적극적으로 개발 및 개선 중입니다.

CLO에서 내보낸 3D 의상 데이터를 Blender로 빠르게 가져오는 브릿지 도구입니다.  
텍스처(Diffuse, Normal, Roughness, Metalness, Opacity)를 자동 감지하여 Principled BSDF 셰이더에 연결하며, UDIM 텍스처를 지원합니다.

---

## Status

이 프로젝트는 현재 **Beta** 단계입니다.  
실사용을 기반으로 지속적으로 개선 중입니다.

- ✅ CLO → Blender (OBJ + MTL + Texture + UDIM)
- ✅ 파일명 기반 Auto-Shader 연결
- ✅ 공유 폴더 자동 감시 (Auto-Import)
- ✅ Export 폴더 자동 정리 기능
- ✅ Debug Log 생성
- ⚠️ Blender → CLO: OBJ Export 지원 (CLO 자동 Import 미지원)
- ⚠️ FBX: UI 존재 (기능 미완성)

---

## 사전 준비

GoB는 **공유 폴더**를 통해 CLO와 Blender 간 파일을 교환합니다.  
기본 경로는 OS에 따라 자동 설정됩니다.

### Windows
```
C:\Users\Public\GoB\
```

### macOS
```
/Users/Shared/GoB/
```

※ Add-on Preferences에서 변경 가능  
※ CLO 스크립트와 동일 경로로 맞춰야 정상 동작합니다.

---

# 설치 — Blender Add-on

## 방법 1: ZIP 파일로 설치 (권장)

1. GitHub Releases에서 최신 버전 ZIP 다운로드
2. 압축 해제
3. `blender_addon/gob/` 폴더만 다시 ZIP으로 압축 (예: gob.zip)
4. Blender 실행
5. Edit → Preferences → Add-ons
6. Install from Disk → gob.zip 선택
7. GoB 활성화

---

## 방법 2: 수동 설치

1. `blender_addon/gob/` 폴더를 아래 경로에 복사

### Windows
```
%APPDATA%\Blender Foundation\Blender\<버전>\scripts\addons\
```

### macOS
```
~/Library/Application Support/Blender/<버전>/scripts/addons/
```

2. Blender 실행 → Add-ons에서 GoB 검색 후 활성화

---

# 설치 — CLO Script

## Script Editor 실행

1. `clo_script/GoB_Send.py` 파일 저장
2. CLO 실행 → Script Editor 열기
3. 파일 열기
4. Run 클릭

---

## Plug-in Manager 등록 (권장)

1. CLO → Plugins → Plug-in Manager
2. `GoB_Send.py` 등록
3. Plugins 메뉴에서 바로 실행 가능

---

# 사용법

## CLO → Blender

1. CLO에서 `GoB_Send.py` 실행
2. Export Dialog 설정 후 OK
3. OBJ + MTL + Texture가 공유 폴더에 생성
4. Blender → 3D View → N 패널 → GoB 탭
5. **Get from CLO** 클릭

---

## Auto-Import

GoB 패널에서 **Auto-Import 활성화** 시  
CLO에서 Export하면 자동으로 Blender에 Import됩니다.

---

# 주요 기능

| 기능 | 설명 |
|------|------|
| Auto-Shader | 파일명 기반 Principled BSDF 자동 연결 |
| UDIM 지원 | `name.1001.png` 패턴 자동 감지 |
| Auto-Import | 공유 폴더 감시 후 자동 Import |
| Folder Cleanup | 오래된 Export 폴더 자동 삭제 |
| Debug Log | GoB_debug.log 자동 생성 |

---

# 텍스처 자동 감지 키워드 (현재 구현 기준)

| 파일명 키워드 | Principled BSDF 소켓 |
|--------------|---------------------|
| `diffuse` | Base Color |
| `normal` | Normal (Normal Map 노드 자동 삽입) |
| `roughness` | Roughness |
| `metalness` | Metallic |
| `opacity` | Alpha |

※ 위 키워드 외 파일명은 자동 연결되지 않습니다.

---

# Add-on Preferences

Blender → Edit → Preferences → Add-ons → GoB

설정 항목:

- 📁 공유 폴더 경로 변경
- 🗂 유지할 Export 폴더 최대 개수
- 🔄 Export Format (OBJ / FBX)
- 📤 Send to CLO 버튼 표시 여부

---

# 요구사항

- Blender 3.6+
- CLO 2025+
- Windows / macOS

---

# License

MIT License © 2026 Jaeyong Lee
