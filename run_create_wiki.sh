#!/bin/bash
# Slack 스레드 요약 -> Confluence 위키 페이지 생성 실행 스크립트
#
# 사전 준비:
#   1. .env 파일에 인증 정보 설정 (.env.example 참고)
#   2. pip install -r requirements.txt
#
# 사용법:
#   # 스페이스 목록 조회
#   ./run_create_wiki.sh --list-spaces
#
#   # 위키 페이지 생성 (스페이스 키 지정 필요)
#   ./run_create_wiki.sh --space-key "~윤효정"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 스페이스 목록 조회 모드
if [[ "${1:-}" == "--list-spaces" ]]; then
    python3 "${SCRIPT_DIR}/create_wiki_summary.py" --list-spaces
    exit 0
fi

# 스페이스 키가 지정되었는지 확인
SPACE_KEY="${1:-}"
if [[ -z "$SPACE_KEY" ]] || [[ "$SPACE_KEY" != --space-key ]]; then
    echo "사용법:"
    echo "  스페이스 목록 조회: $0 --list-spaces"
    echo "  위키 페이지 생성:   $0 --space-key \"~스페이스키\""
    exit 1
fi

SPACE_KEY_VALUE="${2:-}"
if [[ -z "$SPACE_KEY_VALUE" ]]; then
    echo "스페이스 키를 지정해주세요. 예: $0 --space-key \"~윤효정\""
    echo "스페이스 목록을 보려면: $0 --list-spaces"
    exit 1
fi

# 예시 위키 페이지 생성 (실제 사용 시 아래 값들을 수정하세요)
python3 "${SCRIPT_DIR}/create_wiki_summary.py" \
    --space-key "$SPACE_KEY_VALUE" \
    --title "Slack 스레드 요약 - 모바일플랫폼팀 잡담 (2026-02-19)" \
    --thread-url "https://woowahan.slack.com/archives/C0A8NUCAYLU/p1771484241310949?thread_ts=1771472724.667169&cid=C0A8NUCAYLU" \
    --summary "권장휴가 일에 오프라인 출근하여 업무 중인 상황. 혼자 출근하여 심심함을 표현한 가벼운 잡담 스레드." \
    --messages '[
        {"author": "윤효정(HYOJEONG)/ON/모바일플랫폼팀", "content": "오늘이 권장휴가 일이지만 열일중이시군요 (혼자 오프 출근해서 심심)"},
        {"author": "윤효정(HYOJEONG)/ON/모바일플랫폼팀", "content": "아무말"},
        {"author": "윤효정(HYOJEONG)/ON/모바일플랫폼팀", "content": "테스트"}
    ]'
