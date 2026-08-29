# P02 — 모노폴리를 만든 진짜 사람 (리지 매기 / US748626)

`patent-story-short` 포맷, 14비트 43.3초/37.5초. 게이트 통과 2026-08-27.
구조 원칙(사용자 확정): **① 도입 훅 ② 쉬운 설명 ③ 핵심 반전을 마지막에.**
반전 축: 세계에서 가장 유명한 '부자 되기' 게임은, **독점이 나쁘다고 가르치려고** 만들어졌다.

## 사실 검증

| 항목 | 판정 | 출처 |
|---|---|---|
| 발명자 "LIZZIE J. MAGIE", 특허 US748,626, 1904-01-05 등록(1903-03-23 출원) | ● | [특허 원문](https://patents.google.com/patent/US748626A/en) |
| 원래 이름 "The Landlord's Game" — 특허 본문에 직접 명시 | ● | 원문: *"My invention, which I have designated The landlord's game"* |
| 모노폴리와 동일한 규칙이 특허 본문에 존재 | ● | 원문에 감옥(jail·더블 던지면 석방·50달러 벌금), 철도(R.R.), 임대료(rent), 저당(mortgage), 은행(Bank), 증서(deed), 한 바퀴 돌면 임금 100달러(Mother earth) |
| **조지스트 교육 의도가 특허 본문에 흔적으로 남음** | ● | 원문: 생필품 칸 5달러 = *"This represents indirect taxation"*, "No trespassing" 칸 = *"property held out of use"*, 그 외 Poorhouse·Mother earth |
| 찰스 대로우, 1935년 파커브라더스에 판매 → 백만장자 | ● | 다수 출처 일치 |
| 파커브라더스가 매기에게 지급한 금액 500달러, 로열티 없음 | ● | womenshistory.org, HISTORY 등 |
| 진실 공개 계기 = 1973년 랄프 안스패치 'Anti-Monopoly' 소송 | ● | 다수 출처 |
| 매기 사망 1948년 (묘비 실물 확인) | ● | Commons 묘비 사진 |
| 걸러낸 과장: "매기가 모노폴리를 발명했다"는 단정 — 대로우 판본은 애틀랜틱시티 지명 등 독자 요소가 있음. 대본은 "원본이 있었다"로만 서술 | ✗ | — |

## 커버

- 한: **이 게임의 발명자는 지워졌다** (15자)
- 영: **THEY ERASED THE REAL INVENTOR**
- 커버 이미지: 매기 초상(1906) + 모노폴리 보드 흑백 합성, 텍스트는 편집 오버레이

## 비트 대본 — 14비트, 한 238음절(43.3s) / 영 105단어(37.5s)

| # | 유형 | 나레이션 (한) | 비주얼 |
|---|---|---|---|
| 1 | 인물 | 이 게임을 만든 건, 우리가 아는 그 남자가 아니었죠. | 매기 초상 1906 (아직 누군지 모름) |
| 2 | 인물 | 대공황 때 실직자가 만들었다고 알려졌죠. | 대로우 전신 (보드·지폐 더미) |
| 3 | 인물 | 그는 이 게임으로 백만장자가 됐습니다. | 대로우 미소 크롭 |
| 4 | 그래픽 | 그런데 31년 먼저 나온 원본이 있었습니다. | 지주 게임 보드 |
| 5 | 인물 | 만든 사람은 리지 매기라는 여성이었습니다. | 매기 초상 (시집) |
| 6 | 그래픽 | 감옥, 철도, 임대료, 한 바퀴 돌면 월급. | 보드 칸 매크로 |
| 7 | 그래픽 | 우리가 아는 규칙이 이미 다 있었죠. | 지주 게임 커버 |
| 8 | 인물 | 회사는 500달러에 권리를 사갔습니다. | **500달러 지폐를 건네는 대로우 사진** (아이러니 1:1) |
| 9 | 문서 | 서류에 적힌 이름은, 리지 제이 매기. | 특허 도면 크롭 — 64% 지점 |
| 10 | 인물 | 그게 전부였습니다. 로열티는 없었죠. | 매기 신문 초상 |
| 11 | 인물 | 진실은 1973년 법정에서 드러났습니다. | 매기 초상 어둡게 |
| 12 | 인물 | 그녀는 이미 세상을 떠난 뒤였고요. | **묘비 "ELIZABETH MAGIE 1866–1948"** |
| 13 | 인물 | 매기가 이 게임을 만든 이유는 돈이 아니었습니다. | 매기 초상 밝아지며 |
| 14 | 그래픽 | 독점이 나쁘다고 가르치려던 게임, '지주 게임'이었죠. | 지주 게임 커버 |

**나레이션 TTS 풀어쓰기**: 31년→삼십일 년 · 500달러→오백 달러 · 1973년→천구백칠십삼 년. 자막은 아라비아 표기.

게이트: 14비트 전부 OK, 인물 9/14(64%), 문서 1비트·62% 지점, 훅 통념+반박, 페이오프 인용 — 통과.

## 아카이브 스틸 (v6 — 비트마다 대본이 말하는 것을 보여준다)

규칙은 `PRD.md` §2. v5에서 "글자만 있는 그림"을 뺐고(2-1), v6에서 **대본과 그림을 1:1로 맞췄다**(2-2).
1924년 보드 벡터 재현본은 가운데가 흰 글자판이라 9:16으로 자르면 글자 덩어리로만 보여서 뺐다.
보드 사진은 색색의 칸이 보이는 가장자리로 미리 잘라 쓴다(`10b_board_1906_edge.jpg`).

| 비트 | 나레이션 | 파일 | 라이선스 | 크레딧 |
|---|---|---|---|---|
| 1 | 가장 많이 팔린 보드게임 | US748626 도면 → 주사위·주사위통 크롭·반전 (`12b`) | Public domain | — |
| 2·3 | 실직자가 만들었다 / 백만장자가 됐다 | Charles Darrow (51689999467) → MONOPOLY 글자 안 보이게 크롭 | **CC BY 2.0** | ✅ 설명란 |
| 4 | 31년 먼저 나온 원본 | Landlords board game cover | Public domain | — |
| 5 | 리지 매기라는 여성 | Lizzie Magie — My Betrothed, and Other Poems (초상) | Public domain | — |
| 6 | 감옥·철도·임대료·월급 | [Landlords Game 1906 실물 보드](https://commons.wikimedia.org/wiki/File:Landlords_Game_1906_image_courtesy_of_T_Forsyth_owner_of_the_registered_trademark_20151119.jpg) → 가장자리 크롭 (`10b`) | Public domain | — |
| 7 | 우리가 아는 규칙이 다 있었다 | US748626 도면 → BANK 상자 크롭·반전 (`11`) | Public domain | — |
| 8 | **500달러에 권리를 사갔다** | [500 USD note, series of 1934](https://commons.wikimedia.org/wiki/File:500_USD_note;_series_of_1934;_obverse.jpg) — 실제 500달러 지폐 | Public domain | — |
| 9·10 | 서류에 적힌 이름 / 그게 전부 | Elizabeth Magie, Washington Times (1906) | Public domain | — |
| 11 | **1973년 법정에서 드러났다** | [Courtroom of Cleburne County Courthouse](https://commons.wikimedia.org/wiki/File:Courtroom_of_Cleburne_County_Courthouse_in_Heber_Springs,_Arkansas.jpg) | CC0 | — |
| 12 | 이미 세상을 떠난 뒤 | Grave of Elizabeth Magie Phillips | **CC BY 2.0** | ✅ 설명란 |
| 13 | **독점이 나쁘다는 걸 가르치려 했다** | [The Bosses of the Senate, Joseph Keppler 1889](https://commons.wikimedia.org/wiki/File:The_Bosses_of_the_Senate_by_Joseph_Keppler_(cropped).jpg) — 당대 독점 풍자화 | Public domain | — |
| 14 | **(반전)** 이름은 모노폴리 | 모노폴리 실물 보드 (로고) | Public domain | — |

CC BY 2건은 설명란에 "사진: [작가명], CC BY 2.0, Wikimedia Commons" 형식으로 표기하면 조건 충족.
**대로우 사진은 원본에 MONOPOLY 글자가 보여** 위쪽만 잘라 쓴다 — 반전이 14비트 전에 새지 않게.
`04b_darrow_500_crop.jpg`(04와 같은 사진)와 `02_magie_1906_ew.jpg`(대응 비트 없음)는 쓰지 않는다.

## 생성 자산

- **생성 클립 없음 (0크레딧)** — 아카이브 스틸만으로 14비트 전부 커버. Ken Burns + 시네마틱 그레이드.
- 선택 보강(있으면 좋음, Gemini 앱): 1930년대 주사위/보드말 매크로 8초 클립 1개 → 비트 6·7 대체
  ```
  Vertical 9:16 shot. Extreme close-up of vintage 1930s wooden board-game pieces and dice on a worn game board, slow push-in, single warm lamp light, dust motes. Desaturated sepia and deep green, heavy film grain. Cinematic, no people, no text on screen, no legible writing.
  ```

## 오디오

- 음악: P01과 동일 계열(드라마틱 미드템포 피아노) — Pixabay `music_bed.mp3` 재사용 또는 동일 트랙 다른 구간.
- 나레이션: Gemini TTS Charon, 빠른 템포 스타일. **TTS 일일 쿼터 리셋(07:00 UTC) 후 생성.**

## 조립

```
python3 scripts/shorts/chunked_tts.py docs/shorts/ep-p02-beats.json --lang ko --model gemini-3.1-flash-tts-preview
python3 scripts/shorts/compress_silence.py docs/shorts/ep-p02_output/beat*_ko.wav
python3 scripts/shorts/qa_transcribe.py docs/shorts/ep-p02-beats.json --lang ko --beats 1,2,3,4,5,6,7 --model gemini-3.5-flash
python3 scripts/shorts/assemble.py docs/shorts/ep-p02-beats.json --lang ko --edit docs/shorts/ep-p02-edit.json \
    --font <Pretendard-Bold.ttf> --music docs/shorts/ep-p02_output/music_bed.mp3
```

## 업로드 체크

- Studio "변형·합성 콘텐츠" 라벨 ON (합성 나레이션)
- 설명란: 특허 원문 링크 + CC BY 사진 3건 크레딧
- 고정 댓글 후보: "특허 원문에는 이런 문장이 있습니다 — 생필품 칸은 '간접세를 나타낸다'."
