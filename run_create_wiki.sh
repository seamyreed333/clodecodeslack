#!/bin/bash
# Slack 스레드 요약 -> Confluence 위키 페이지 생성 실행 스크립트
#
# 사전 준비:
#   1. .env 파일에 인증 정보 설정 (.env.example 참고)
#   2. pip install -r requirements.txt
#
# 사용법:
#   ./run_create_wiki.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --dry-run 옵션: 실제 API 호출 없이 미리보기만 수행
# 실제 위키에 생성하려면 --dry-run 을 제거하고 .env 에 인증 정보를 설정하세요.
python3 "${SCRIPT_DIR}/create_wiki_summary.py" \
    --space-url "https://cloud.wiki.woowa.in/wiki/spaces/~%EC%9C%A4%ED%9A%A8%EC%A0%95/" \
    --title "Slack 스레드 요약 - 모바일플랫폼팀 잡담 (2026-02-19)" \
    --thread-url "https://woowahan.slack.com/archives/C0A8NUCAYLU/p1771484241310949?thread_ts=1771472724.667169&cid=C0A8NUCAYLU" \
    --summary "권장휴가 일에 오프라인 출근하여 업무 중인 상황. 혼자 출근하여 심심함을 표현한 가벼운 잡담 스레드." \
    --messages '[
        {"author": "윤효정(HYOJEONG)/ON/모바일플랫폼팀", "content": "오늘이 권장휴가 일이지만 열일중이시군요 (혼자 오프 출근해서 심심)"},
        {"author": "윤효정(HYOJEONG)/ON/모바일플랫폼팀", "content": "아무말"},
        {"author": "윤효정(HYOJEONG)/ON/모바일플랫폼팀", "content": "테스트"}
    ]' \
    --dry-run
