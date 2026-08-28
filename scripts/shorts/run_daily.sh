#!/usr/bin/env bash
# 쿼터가 열리는 날 이 한 줄만 실행하면 됩니다.
#
#   bash scripts/shorts/run_daily.sh
#
# 두 프로세스를 띄웁니다.
#   patient_tts      쿼터가 열릴 때마다 나레이션을 조금씩 채운다 (429가 나면 길게 쉬고 모델을 바꾼다)
#   finish_episodes  한 편이 다 차는 순간을 감지해 무음압축→조립까지 끝낸다
#
# 자막 폰트는 assets/fonts/Pretendard-Bold.ttf 를 자동으로 씁니다(지정 불필요).
# 중간에 끊겨도 진행분은 파일로 남으므로, 다음 날 같은 명령을 다시 실행하면
# 남은 것부터 이어서 채웁니다.
#
# 로그: logs/tts.log · logs/finish.log
# 중단: bash scripts/shorts/run_daily.sh stop

set -u
cd "$(dirname "$0")/../.." || exit 1

LOGDIR=logs
mkdir -p "$LOGDIR"

if [ "${1:-}" = "stop" ]; then
    pkill -f patient_tts.py && echo "· patient_tts 중단"
    pkill -f finish_episodes.py && echo "· finish_episodes 중단"
    exit 0
fi

if [ -z "${GEMINI_API_KEY:-}" ]; then
    echo "✗ GEMINI_API_KEY 가 없습니다. 환경 변수를 설정한 뒤 다시 실행하세요."
    exit 1
fi

if pgrep -f patient_tts.py > /dev/null; then
    echo "· 이미 돌고 있습니다. 로그: $LOGDIR/tts.log"
    exit 0
fi

# 아직 나레이션이 덜 찬 편만 넘긴다. p01:en:1,2 는 대본이 바뀌어 낡아버린
# 영어 청크라 자리표시 탐지로는 안 잡히므로 직접 지정한다.
MINUTES="${MINUTES:-720}"
TARGETS="p01:en:1,2 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11 p12"

nohup python3 -u scripts/shorts/patient_tts.py $TARGETS \
    --lang ko --minutes "$MINUTES" > "$LOGDIR/tts.log" 2>&1 &
nohup python3 -u scripts/shorts/finish_episodes.py \
    --lang ko --minutes "$MINUTES" > "$LOGDIR/finish.log" 2>&1 &

sleep 2
echo "✓ 시작했습니다 (최대 ${MINUTES}분)"
echo "  나레이션 진행:  tail -f $LOGDIR/tts.log"
echo "  완성본 생성:    tail -f $LOGDIR/finish.log"
echo "  현재 상태:      python3 scripts/shorts/status.py"
echo "  중단:           bash scripts/shorts/run_daily.sh stop"
