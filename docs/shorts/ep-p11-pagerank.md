# P11 — 구글을 만든 특허, 주인은 구글이 아니었다 (래리 페이지 / US6285999B1)

14비트 40.4초/37.9초. 게이트 통과 2026-08-27. 구조: **훅(그 특허 주인이 누구냐) → 쉬운 설명(가리키면 점수가 오른다) → 반전(주인은 스탠퍼드였고, 대학이 받은 주식은 3억 3600만 달러가 됐다).**

반전은 서류의 두 줄을 차례로 여는 것이다. 발명자란엔 **Lawrence Page 하나**, 양수인란엔 **스탠퍼드 이사회**.
착지는 스탠퍼드가 자기 연차보고서에 쓴 금액이다.

## 사실 검증

| 항목 | 판정 | 근거 |
|---|---|---|
| US6,285,999 B1 **"Method for node ranking in a linked database"**, 발명자 **Lawrence Page 단독**, 양수인 **The Board of Trustees of the Leland Stanford Junior University** | ● | [특허 원문](https://patents.google.com/patent/US6285999B1/en) · patentimages PDF 직접 확인 |
| 출원 1998-01-09 (09/004,827), 가출원 60/035,205 (1997-01-10), 등록 **2001-09-04**. **청구항 29개, 도면 3장** | ● | 원문 |
| 존속기간 조정 **0일**: *"the term of this patent is extended or adjusted under 35 U.S.C. 154(b) by 0 days."* → **만료 2018-01-09**(출원일로부터 20년) | ● | USPTO 원문 표지 |
| 초록: *"The rank assigned to a document is calculated from the ranks of documents citing it."* — 이 한 문장이 원리 전부 | ● | 원문 초록 |
| **브린의 이름은 특허에 있다 — 단, 발명자란이 아니라 본문 감사의 말에.** 원문 3단: *"For support in reducing the present invention to practice, the inventor acknowledges **Sergey Brin**, Scott Hassan, Rajeev Motwani, Alan Steremberg, and Terry Winograd."* | ● | 원문 7쪽 3단, 크롭 확인 |
| 라이선스는 **'인터넷 검색' 분야 한정 독점**. §3.2: 독점 기간은 **2011-09-04**에 끝나고 이후 만료까지 비독점 | ● | [SEC EDGAR 라이선스 계약서 Ex.10.10](https://www.sec.gov/Archives/edgar/data/1288776/000119312504141762/dex1010.htm) |
| 스탠퍼드는 현금 대신 **구글 주식**을 받았다. 계약서에 1999-04-14 Series A 우선주 발행 기록. **주식 수는 전량 [***] 로 비공개** | ● (사실) / — (수량) | 같은 문서 |
| **금액: 3억 3600만 달러.** 스탠퍼드 기술이전본부 2005년 연차보고서 원문: *"At **\$336 million**, this is by far the most lucrative invention we have ever licensed."* | ● | [Stanford OTL Annual Report 2005](https://www-leland.stanford.edu/group/OTL/documents/otlar05.pdf) |
| **주의 — 같은 보고서가 같은 금액을 다르게도 쓴다**: *"we received \$336M in liquidated equity from **seven companies**."* 구글이 압도적 비중인 건 분명하지만 보고서가 구글 단독 금액을 따로 떼어 주지는 않는다. 화면에서는 **스탠퍼드 문장을 인용하는 형식**으로 처리했다 | ● | 같은 보고서 |
| 스탠퍼드가 일찍 판 이유는 실수가 아니라 규정: *"For institutional conflict-of-interest reasons and insider trading concerns, the Stanford Management Company sells our public equities as soon as Stanford is allowed to liquidate rather than holding equity to maximize return."* | ● | 같은 보고서 |
| **이 특허로 소송이 벌어진 적이 없다.** CourtListener 판결문 전수 검색에서 '6,285,999'를 인용한 판결 0건 | ● | CourtListener API 검색 |
| 걸러낸 허구: **"구글이 특허를 소유했다" ✗** (양수인은 스탠퍼드, 구글은 실시권자) / **"페이지와 브린이 공동 출원했다" ✗** (단독) / **"특허가 만료돼서 구글이 알고리즘을 바꿨다" ✗** (독점은 2011년에 이미 끝났고 인과 근거 없음) / **"스탠퍼드가 구글 문을 닫게 할 수 있었다" ✗** (계약상 제재는 해지가 아니라 비독점 전환) / **구글이 스탠퍼드에 낸 현금 액수** ✗ (계약서 금액 전량 비공개 — 떠도는 숫자는 근거 없음) | ✗ | 위 1차 자료들 |
| 'PageRank'라는 이름의 유래에 대한 **본인들의 1차 설명은 발견되지 않음.** 1998년 논문에도 없다. 다만 프로젝트 원래 이름이 **BackRub**이었다는 건 논문 참고문헌 URL(`google.stanford.edu/~backrub/`)에 남아 있다. **대본에서 다루지 않음** | ◐ | 판단: 미사용 |
| 로빈 리의 RankDex(US5920859)를 **이 특허는 인용하지 않는다**(인용 미국특허 7건 전수 확인). 인용하는 건 2006년 연속출원 US7058628이다. **대본에서 다루지 않음** | ● | 원문 References Cited |

## 비트 대본 (한 222음절 / 영 106단어)

| # | 유형 | 나레이션 (한) | 비주얼 |
|---|---|---|---|
| 1 | 인물 | 구글을 만든 그 알고리즘, 특허 주인은 누구일까요? | FIG.1 문서 B·C→A(블루프린트) |
| 2 | 인물 | 천구백구십팔 년, 서류 한 장이 접수됩니다. | 특허 헤더 |
| 3 | 그래픽 | 제목은 '연결된 문서에 순위 매기기'였죠. | **카드 METHOD FOR NODE RANKING** |
| 4 | 그래픽 | 원리는 한 문장이면 끝납니다. | FIG.1 푸시인 |
| 5 | 그래픽 | 다른 문서가 가리키면 점수가 올라갑니다. | **초록 인용 카드** |
| 6 | 그래픽 | 점수 높은 문서가 가리키면 더 크게 올라가고요. | **FIG.2 점수 0.4/0.2 흐름** |
| 7 | 그래픽 | 그 점수로 검색 결과를 줄 세운 겁니다. | FIG.3 순서도 |
| 8 | 인물 | 이게 구글의 시작이었습니다. | 헤더 푸시인 |
| 9 | 문서 | 그런데 발명자란엔 이름이 하나뿐입니다. | **Inventor: Lawrence Page 줄** — 64% 지점 |
| 10 | 인물 | 세르게이 브린은 감사의 말에만 나옵니다. | **본문 감사의 말 크롭** |
| 11 | 인물 | 그리고 특허 주인도 구글이 아니었습니다. | 발명자+양수인 두 줄 어둡게 |
| 12 | 인물 | 스탠퍼드 대학이었어요. | **Assignee: 스탠퍼드 이사회 줄** |
| 13 | 인물 | 대학은 돈 대신 구글 주식을 받았고요. | 두 줄 밝게 |
| 14 | 인물 | 그 주식은 삼억 삼천육백만 달러가 됐습니다. | **금액 카드 \$336,000,000** |

**TTS 풀어쓰기**: 1998년→천구백구십팔 년 · 3억 3600만→삼억 삼천육백만.

## 아카이브 스틸 (확보 완료 — 전부 0크레딧)

| 파일 | 용도 | 라이선스 | 크레딧 |
|---|---|---|---|
| US6285999 PDF → 200dpi 렌더 → 크롭 → 블루프린트 반전 (FIG.1~3, 헤더, 발명자·양수인·감사의 말) | 1·2·4·6·7·8·9·10·11·12·13, 커버 | Public domain | — |
| 코드 렌더 카드 3종 (제목 / 초록 인용 / 금액) | 3·5·14 | 자체 제작 | — |

인물 사진은 쓰지 않는다. 생존 인물이고, 도면·서지 크롭만으로 이야기가 완결된다.

## 오디오

- 음악: `music_bed.mp3` — track1.mp3 150~195초.
- 나레이션: 9비트 뒤 한 박, 12비트 '스탠퍼드 대학이었어요'는 짧게 끊고, 14비트는 낮게.

## 업로드 체크

- Studio "변형·합성 콘텐츠" 라벨 ON
- 설명란: [특허 원문 US6285999B1](https://patents.google.com/patent/US6285999B1/en) · [스탠퍼드–구글 라이선스 계약서(SEC)](https://www.sec.gov/Archives/edgar/data/1288776/000119312504141762/dex1010.htm) · [Stanford OTL 2005 연차보고서](https://www-leland.stanford.edu/group/OTL/documents/otlar05.pdf)
- **설명란 필수 주석**: "3억 3600만 달러는 스탠퍼드 기술이전본부 2005년 연차보고서의 표현입니다. 같은 보고서는 이 금액을 그해 7개 회사에서 회수한 지분 총액으로도 적고 있어, 구글 단독 금액으로 확정된 수치는 아닙니다."
- **말하지 않을 것**: 구글이 특허를 소유했다 / 브린이 공동 발명자다 / 특허 만료가 알고리즘 변경을 불렀다 / 스탠퍼드가 구글을 멈출 수 있었다 / 구글이 낸 현금 액수.
- 고정 댓글 후보: "웹 역사상 가장 값비싼 특허인데, 이 특허로 벌어진 소송은 단 한 건도 없습니다. 독점 기간은 2011년에 끝났고, 특허 자체는 2018년 1월 9일 — 출원일로부터 정확히 20년 되는 날 만료됐습니다."
