# 특허 스토리 쇼츠 — 제작 인덱스

특허·1차 문서에서 출발하는 인물 반전 쇼츠(9:16, 30~45초, 14비트) 시리즈.
규칙은 `.claude/skills/patent-story-short/SKILL.md`, 근거는 `winning-pattern-analysis.md`.

**구조 3원칙 (전 편 공통)** — ① 도입 후킹 ② 쉬운 이야기 ③ **핵심 반전은 마지막 비트에**.

## 편 현황

| 편 | 소재 / 특허 | 길이 | 반전(마지막 비트) | 대본 | 스틸 | 편집스펙 | 나레이션 | 완성본 |
|---|---|---|---|---|---|---|---|---|
| **P01** | 헤디 라마르 · US2292387 | 42.5s | 정체 공개 — 할리우드의 전설 | ✅ | ✅ | ✅ | ✅ 한·영 | ✅ **한·영 완성** |
| **P02** | 리지 매기 · US748626 | 43.3s | 목적 반전 — 독점을 가르치려던 게임 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P03** | 위저 보드 · US446054 | 44.2s | 이름의 출처 — 그녀 목걸이 속 'Ouida' | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P04** | 니콜스 큐브 · US3655201 | 41.8s | 단어 하나 '여덟'이 판을 뒤집음 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P05** | 링컨 · US6469 | 40.9s | 정체 공개 — 특허를 가진 유일한 대통령 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P06** | 휴지 방향 · US465588 | 41.8s | 통설 자체를 뒤집음 — 방향을 없애려던 발명 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P07** | 지퍼 · US504038 | 40.0s | 이름이 붙기 14년 전에 죽은 발명가 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P08** | 전화 · US174465 | 44.9s | 두 시간 신화 붕괴 — 이긴 건 기계가 아니라 '방법' | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P09** | 라이트 형제 · US821393 | 43.8s | 엔진을 손으로 깎은 정비공이 증인란에 서명 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P10** | 그네 특허 · US6368227B1 | 41.1s | 변리사가 아버지, 발명자는 일곱 살 아들 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P11** | 페이지랭크 · US6285999B1 | 40.4s | 특허 주인은 스탠퍼드, 주식은 3억 3600만 달러 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P12** | 테슬라 · US645576 | 40.7s | 대법원은 아무것도 주지 않았고, 그는 5달 전 죽었다 | ✅ | ✅ | ✅ | ⏳ | 프리뷰만 |
| **P13** | 에디슨 전구 · US223898 | — | *(미정 — 대본 전 단계)* | ✗ | ✅ | ✗ | ✗ | — |

⏳ = TTS 일일 쿼터 대기 (리셋 07:00 UTC). ◐ = 일부 확보. ✗ = 미착수.

**P13은 스틸만 있습니다.** 도면 크롭(전구·필라멘트·마운트·에디슨 서명)은 블루프린트로
반전해 뒀고, 명세서 첫 문장이 *"have invented an Improvement in Electric Lamps"* 라는 것도
확인했습니다. **대본을 쓰려면 아래 세 가지 검증이 먼저 필요합니다** — 검증 없이 쓰지 않았습니다.

1. 청구항 1 원문 (이 스캔은 OCR이 깨져 있어 다른 판본으로 확인해야 합니다)
2. 조지프 스완과의 영국 건 — 소송이었는지 합의였는지, 합병 회사명(Ediswan)과 연도
3. 1883년 특허청의 무효 판단과 1889년 항소 결과의 정확한 경위

3번이 마지막 비트 후보라 특히 중요합니다.

## 파일 규칙

```
docs/shorts/
  ep-pNN-beats.json      대본 (게이트 입력) — {title, cover_ko, cover_en, beats[14]{ko,en,visual}}
  ep-pNN-edit.json       편집 스펙 — {edit[14], subs_ko, subs_en, bottom_beats, ambient}
  ep-pNN-<주제>.md        패키지 문서 — 사실 검증표·비트 표·스틸 라이선스·업로드 체크
  ep-pNN_output/
    stills/              아카이브 스틸·크롭·코드 렌더 카드
    beatNN_{ko,en}.wav   나레이션
    music_bed.mp3        음악 (구간 트림)
    ep-pNN_{ko,en}.mp4   완성본 (음악 포함) / _preview.mp4 (음악 없음)
```

## 파이프라인 (편당)

```bash
# 0) 대본 게이트 — 통과해야 다음 단계
python3 .claude/skills/patent-story-short/scripts/gate.py docs/shorts/ep-pNN-beats.json

# 1) 나레이션 (TTS 쿼터 필요)
python3 scripts/shorts/chunked_tts.py docs/shorts/ep-pNN-beats.json --lang ko --model gemini-3.1-flash-tts-preview
python3 scripts/shorts/compress_silence.py docs/shorts/ep-pNN_output/beat*_ko.wav

# 2) 검수 (STT 대조, 모델 교차)
python3 scripts/shorts/qa_transcribe.py docs/shorts/ep-pNN-beats.json --lang ko --beats 1,2,3,4,5,6,7 --model gemini-3.5-flash

# 3) 조립
python3 scripts/shorts/assemble.py docs/shorts/ep-pNN-beats.json --lang ko \
    --edit docs/shorts/ep-pNN-edit.json --font <Pretendard-Bold.ttf> --music docs/shorts/ep-pNN_output/music_bed.mp3

# TTS 없이 비주얼만 미리 보기 (자리표시 무음)
python3 scripts/shorts/placeholder_wavs.py docs/shorts/ep-pNN-beats.json --lang ko
```

## 도구

| 스크립트 | 하는 일 |
|---|---|
| `chunked_tts.py` | 4비트 묶음 TTS + 무음 분할 (무료 티어 호출수 1/3.5) |
| `compress_silence.py` | TTS 돌발 장침묵(>0.9s) 압축 |
| `qa_transcribe.py` | STT 받아쓰기 ↔ 대본 대조, 숫자 표기 정규화 |
| `assemble.py` | 나레이션 타임라인에 비주얼 조립 · Ken Burns · 그레이드 · libass 자막 · 오디오 믹스 |
| `placeholder_wavs.py` | 무음 자리표시(드라이런) |
| `patient_tts.py` | 쿼터가 열릴 때마다 자리표시 청크만 골라 채우는 인내형 러너 |
| `finish_episodes.py` | 나레이션이 다 찬 편을 감지해 **무음압축→조립까지 무인 실행** |
| `run_daily.sh` | 위 둘을 한 번에 띄우는 실행 스크립트 (**하루 한 번 이것만**) |
| `status.py` | 편별 나레이션·완성본 진행률 한 화면 |
| `render_diagram.py` | 88채널 도약 다이어그램 (정확히 88선) |
| `render_card.py` | 특허 원문 인용 카드 (핵심 단어 금색 강조) |
| `invert_drawing.py` | 특허 도면 → 블루프린트 반전 (자막 대비 확보) |
| `generate_visuals.py` | Gemini 이미지·Veo 클립 (유료 계정 전용) |

## 사람 손이 필요한 것

무료 티어로 갑니다(2026-08-27 결정). **쿼터가 열리는 한국시간 오후 4시 이후 하루 한 번**
아래 한 줄만 실행하면 됩니다. 나머지는 자동입니다.

```bash
bash scripts/shorts/run_daily.sh          # 나레이션 채우기 + 완성본 조립
python3 scripts/shorts/status.py          # 진행 상황
```

자막 폰트는 `assets/fonts/Pretendard-Bold.ttf` 를 저장소에 동봉했고 `assemble.py` 기본값입니다.
자세한 내용은 `USER-ACTIONS.md`.
