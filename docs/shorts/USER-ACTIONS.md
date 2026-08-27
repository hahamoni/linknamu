# 사용자가 해야 할 일 (모아두기)

세션 중 Claude가 할 수 없어 사람 손이 필요한 항목만 모읍니다. 완료하면 체크.

## 계정·결제

- [ ] **Higgsfield** — free 플랜이라 생성 불가("Requires basic plan or higher"). 쓸 계획이면 basic 이상 필요.
      (현재는 Gemini 경로로 우회 중이라 급하지 않음)
- [ ] **Google AI Studio 과금(tier 1)** — 무료 티어는 ①이미지·비디오 생성 쿼터 0 ②TTS 하루 약 10회/모델.
      켜면 클립 생성이 자동화되고, 나레이션 재생성 때마다 쿼터로 막히는 일이 사라짐. **가장 효과 큰 항목.**

## 영상 소재 (Gemini 앱, Plus 구독으로 가능)

각 편의 생성 클립은 앱에서 직접 뽑아 첨부해 주세요. 프롬프트는 편별 패키지 문서에 있습니다.
방법: 스틸 첨부 → "이미지→영상" → 세로 선택. (P01에서 검증된 경로)

- [ ] P02 모노폴리 — 클립 프롬프트는 `ep-p02-*.md` 참조 (없어도 스틸만으로 편집 가능)

## 업로드 (편별)

- [ ] P01 — Studio "변형·합성 콘텐츠" 라벨 ON / 설명란에 특허 원문 링크 / 커버 텍스트 오버레이
      ("당신의 블루투스, 그 시작"), 고정 댓글 후보: 헤디 라마르의 수상 소감 "이제야 왔군요."

## 참고 (액션 아님)

- 음악은 Claude가 Pixabay(무귀속·상업 허용)에서 직접 확보 중 — 유튜브 오디오 라이브러리 선호 시에만 사람 손 필요.
- 아카이브 스틸은 Wikimedia에서 직접 수집 가능(429 시 재시도로 해결).

---

## 진행 로그 (2026-08-27 세션)

### 완료
- **P01 헤디 라마르** — 최종본 `ep-p01_ko.mp4` (42.5s, 음악·자막 포함). 영어판은 5개 비트 나레이션 재생성 대기.
- **P02~P05 대본 4편** — 전부 게이트 통과, 특허 원문 검증 완료.
  - P02 모노폴리(리지 매기) 43.3s · P03 위저 보드 44.2s · P04 니콜스 큐브 41.8s · P05 링컨 40.9s
- **P02·P05 편집 스펙 + 아카이브 스틸** 확보 — 클립 생성 없이 0크레딧으로 조립 가능.

### 막힌 것 — Gemini 무료 티어 TTS 일일 쿼터 (3개 모델 전부 소진)
- 리셋: **매일 07:00 UTC (16:00 KST)**.
- 그때까지 신규 나레이션 생성 불가 → 대본·스틸·편집 스펙만 선행 작업.
- **해소 방법: Google AI Studio 결제 연결(tier 1).** 위 "계정·결제" 항목 참조.

### 리셋 후 바로 실행 (편별 1줄씩)
```
python3 scripts/shorts/chunked_tts.py docs/shorts/ep-pNN-beats.json --lang ko --model gemini-3.1-flash-tts-preview
python3 scripts/shorts/compress_silence.py docs/shorts/ep-pNN_output/beat*_ko.wav
python3 scripts/shorts/assemble.py docs/shorts/ep-pNN-beats.json --lang ko --edit docs/shorts/ep-pNN-edit.json --font <Pretendard-Bold.ttf> --music <track.mp3>
```
자리표시 무음 나레이션으로 비주얼만 미리 보려면: `python3 scripts/shorts/placeholder_wavs.py docs/shorts/ep-pNN-beats.json --lang ko`
