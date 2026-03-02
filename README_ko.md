# GoB — CLO ↔ Blender Bridge

**[English](README.md) | [日本語](README_jp.md)**

> ⚠️ **Beta** — 현재 CLO → Blender 전송은 안정적이나, Blender → CLO는 초기 개발 단계입니다.

CLO에서 내보낸 3D 의상 데이터를 Blender로 빠르게 가져오는 브릿지 도구입니다.  
텍스처(Diffuse, Normal, Roughness, Metalness, Opacity)를 자동으로 감지하여 Principled BSDF 셰이더에 연결하며, UDIM 텍스처도 지원합니다.

## Status

🚧 이 프로젝트는 현재 **Beta** 단계입니다.  
실사용하면서 지속적으로 개선해 나갈 예정입니다.

- ✅ CLO → Blender (OBJ + 텍스처 + UDIM)
- ✅ 텍스처 파일명 기반 Auto-Shader 연결
- ✅ 공유 폴더 자동 감시 (Auto-Import)
- ⚠️ Blender → CLO: 공유 폴더로 OBJ 추출 지원 (CLO 자동 임포트는 추후 지원 예정)
- 🔜 FBX 포맷 지원

버그 리포트나 제안은 [Issues](../../issues)에 남겨주세요.

---

## 사전 준비

GoB는 **공유 폴더**를 통해 CLO와 Blender 간 파일을 교환합니다.  
첫 사용 전에 아래 폴더를 생성해 주세요:

```
C:\Users\Public\GoB\
```

> 💡 스크립트 실행 시 자동 생성되지만, 권한 문제 방지를 위해 미리 만들어 두는 것을 권장합니다.

---

## 설치 — Blender Add-on

1. `blender_addon/gob/` 폴더를 **통째로** 아래 경로에 복사합니다:
   ```
   %APPDATA%\Blender Foundation\Blender\<버전>\scripts\addons\
   ```
   예시 (Blender 5.0):
   ```
   C:\Users\<사용자명>\AppData\Roaming\Blender Foundation\Blender\5.0\scripts\addons\gob\
   ```
2. Blender 실행 → **Edit → Preferences → Add-ons**
3. `GoB` 검색 → **GoB — CLO Bridge** 체크하여 활성화

---

## 설치 — CLO Script

### 방법 1: Script Editor에서 직접 실행

1. `clo_script/GoB_Send.py` 파일을 원하는 위치에 저장
2. CLO 실행 → **Script Editor** 열기
3. `GoB_Send.py` 파일 열기
4. 필요할 때마다 **Run** 버튼을 눌러 실행

### 방법 2: Plug-in Manager에 등록 (추천)

1. CLO 상단 메뉴 → **Plugins → Plug-in Manager** 클릭
2. `GoB_Send.py` 파일을 플러그인으로 등록
3. 등록 후 **Plugins → Plug-in** 메뉴에서 바로 실행 가능

> 💡 Plug-in Manager에 등록하면 매번 Script Editor를 열 필요 없이 메뉴에서 한 클릭으로 실행할 수 있습니다.

---

## 사용법

### CLO → Blender

1. CLO Script Editor에서 `GoB_Send.py` 실행
2. **Export Dialog**가 표시됨 → 스케일, 텍스처, UV 등 원하는 설정 후 OK
3. OBJ + MTL + 텍스처가 자동으로 `C:/Users/Public/GoB/` 폴더에 복사됨
4. Blender → 3D Viewport → N키 사이드바 → **GoB** 탭 → **Get from CLO** 클릭

### Auto-Import

GoB 패널에서 **Auto-Import** 토글 → CLO에서 Export하면 자동으로 Blender에 Import됩니다.

---

## 기능

| 기능 | 설명 |
|------|------|
| Export Dialog | CLO 내장 Export UI에서 설정 커스텀 |
| Auto-Shader | 텍스처 파일명 기반 Principled BSDF 자동 연결 |
| UDIM 지원 | `name.1001.png` ~ `name.100N.png` 패턴 자동 감지 |
| Auto-Import | 공유 폴더 자동 감시 + 자동 Import |
| Drag & Drop | `.zprj` 파일 Blender 뷰포트에 드롭 가능 |

## 텍스처 자동 감지 키워드

| 파일명 키워드 | Principled BSDF 소켓 |
|:-------------|:--------------------|
| `diffuse`, `basecolor`, `albedo` | Base Color |
| `normal` | Normal (Normal Map 노드 자동 삽입) |
| `roughness` | Roughness |
| `metalness`, `metallic` | Metallic |
| `opacity`, `alpha` | Alpha |

---

## 공유 폴더

기본 경로: `C:/Users/Public/GoB/`

경로를 변경하고 싶다면 **양쪽 모두** 맞춰줘야 합니다:

| 측 | 변경 방법 |
|---|----------|
| **CLO** | `GoB_Send.py` 상단의 `GOB_FOLDER` 변수를 수정 |
| **Blender** | GoB 패널 → **Settings** → **Folder** 에서 변경 |

## 요구사항

- **Blender** 5.0+
- **CLO** 2025+
- **OS**: Windows

## License

[MIT License](LICENSE) © 2026 Jaeyong Lee
