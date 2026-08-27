# 시리즈 공용 음원

## track1.mp3

- 곡: **"Cinematic Dramatic Emotional Piano"** — Music_For_Creators, Pixabay #131839
- 출처: https://pixabay.com/music/main-title-cinematic-dramatic-emotional-piano-131839/
- 라이선스: **Pixabay Content License** — 귀속 표기 불필요, 상업적·유튜브 사용 허용
- 길이 3:08

편별 `music_bed.mp3` 는 이 파일에서 구간을 잘라 페이드를 입힌 것이다.
스크래치 디렉터리는 컨테이너 재시작 때 사라지므로 **원본을 저장소에 둔다** —
이게 없으면 새 편의 음악 베드를 만들 수 없다.

편별 사용 구간:

| 편 | 구간 | 비고 |
|---|---|---|
| P01 | 48–105s | 도입 잔잔 → 중반 상승 → 페이오프 정점 |
| P06 | 4–46s | |
| P09 | 40–92s | |
| P10 | 96–144s | |
| P11 | 150–195s | |

새 편 베드 만들기:
```bash
FF=<imageio-ffmpeg 바이너리>
$FF -y -ss <시작> -t <길이> -i docs/shorts/_audio/track1.mp3 \
   -af "afade=in:st=0:d=2,afade=out:st=<길이-4>:d=4" \
   docs/shorts/ep-pNN_output/music_bed.mp3
```
