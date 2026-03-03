# GoB — CLO ↔ Blender Bridge (v0.2.1 Beta)

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

- ✅ CLO → Blender (OBJ + MTL + Texture + UDIM)
- ✅ 파일명 기반 Auto Shader
- ✅ 공유 폴더 기반 Auto Import
- ✅ Export 폴더 자동 정리
- ✅ Debug Log 생성
- ⚠️ Blender → CLO: OBJ Export만 지원
- ⚠️ FBX: UI 존재 (기능 미완성)

---

## 텍스처 자동 감지 키워드 (현재 구현 기준)

| 파일명 키워드 | Principled BSDF 소켓 |
|--------------|---------------------|
| `diffuse` | Base Color |
| `normal` | Normal |
| `roughness` | Roughness |
| `metalness` | Metallic |
| `opacity` | Alpha |

---

## 요구사항

- Blender 3.6+
- CLO 2025+
- Windows / macOS

---

## License

MIT License © 2026 Jaeyong Lee
