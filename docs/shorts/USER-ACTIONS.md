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
- **P01 헤디 라마르** — 최종본 `ep-p01_ko.mp4` (42.5s, 음악·자막 포함). 영어판은 2·4·5·6·7비트 재생성 대기.
- **대본 12편(P01~P12) 전부 게이트 통과**, 편별 특허 원문 검증 완료.
- **편집 스펙 + 스틸 + 음악 + 커버 12편분 확보** — 클립 생성 없이 0크레딧으로 조립 가능.
- **드라이런 프리뷰**(자리표시 무음) 로 비주얼·자막 배치까지 눈으로 검수 완료.
- P13(에디슨 전구)은 **스틸까지만** — 대본 전 검증 3건이 남아 README에 적어 뒀습니다.

**나레이션만 남았습니다.** 아래 쿼터 항목이 풀리면 명령 두 줄로 12편이 자동 완성됩니다.

### 막힌 것 — Gemini 무료 티어 TTS 일일 쿼터 (3개 모델 전부 소진)
- 리셋: **매일 07:00 UTC (16:00 KST)**.
- 그때까지 신규 나레이션 생성 불가 → 대본·스틸·편집 스펙만 선행 작업.
- **해소 방법: Google AI Studio 결제 연결(tier 1).** 위 "계정·결제" 항목 참조.

### 리셋 후 — **명령 두 줄이면 전 편이 알아서 완성됩니다**

두 프로세스를 같이 띄워 두면 됩니다. 앞의 것이 쿼터가 열릴 때마다 나레이션을 조금씩 채우고,
뒤의 것이 다 찬 편을 감지해 조립까지 끝냅니다. 사람이 07:00 UTC에 깨어 있을 필요가 없습니다.

```bash
python3 scripts/shorts/patient_tts.py p01:en:1,2 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11 \
    --lang ko --minutes 600 &
python3 scripts/shorts/finish_episodes.py --lang ko --font <Pretendard-Bold.ttf> --minutes 600 &
```

`p01:en:1,2` 가 맨 앞인 이유: P01 영어 나레이션 중 **2·4·5·6·7비트가 낡았습니다.**
대본 v3 리라이트(2026-08-27 14:42) 이전에 만들어진 음성이라 옛 문장을 읽고 있습니다.
파일에 소리가 멀쩡히 들어 있어서 자동 탐지로는 못 잡기 때문에 청크 1·2를 직접 지정합니다.
이것만 다시 만들면 P01 영어판이 완성됩니다.

편 하나만 손으로 돌릴 때:
```
python3 scripts/shorts/chunked_tts.py docs/shorts/ep-pNN-beats.json --lang ko --model gemini-3.1-flash-tts-preview
python3 scripts/shorts/compress_silence.py docs/shorts/ep-pNN_output/beat*_ko.wav
python3 scripts/shorts/assemble.py docs/shorts/ep-pNN-beats.json --lang ko --edit docs/shorts/ep-pNN-edit.json --font <Pretendard-Bold.ttf> --music docs/shorts/ep-pNN_output/music_bed.mp3
```
자리표시 무음 나레이션으로 비주얼만 미리 보려면: `python3 scripts/shorts/placeholder_wavs.py docs/shorts/ep-pNN-beats.json --lang ko`
