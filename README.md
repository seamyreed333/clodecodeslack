# clodecodeslack

Slack 스레드 내용을 요약하여 Confluence 위키 페이지로 자동 생성하는 도구.

## 기능

- Slack 스레드 메시지를 Confluence storage format HTML로 변환
- Confluence REST API를 통한 위키 페이지 자동 생성/업데이트
- 중복 제목 페이지 자동 감지 및 업데이트
- dry-run 모드로 미리보기 지원

## 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.example` 파일을 `.env`로 복사 후 인증 정보를 입력합니다.

```bash
cp .env.example .env
# .env 파일 편집하여 인증 정보 입력
```

## 사용법

### dry-run (미리보기)

```bash
python create_wiki_summary.py \
    --space-url "https://cloud.wiki.woowa.in/wiki/spaces/~%EC%9C%A4%ED%9A%A8%EC%A0%95/" \
    --title "Slack 스레드 요약" \
    --thread-url "https://woowahan.slack.com/archives/..." \
    --messages '[{"author": "홍길동", "content": "안녕하세요"}]' \
    --summary "요약 내용" \
    --dry-run
```

### 실제 위키 생성

```bash
python create_wiki_summary.py \
    --space-url "https://cloud.wiki.woowa.in/wiki/spaces/~%EC%9C%A4%ED%9A%A8%EC%A0%95/" \
    --title "Slack 스레드 요약" \
    --thread-url "https://woowahan.slack.com/archives/..." \
    --messages messages.json \
    --summary "요약 내용"
```

### 예시 실행 스크립트

```bash
./run_create_wiki.sh
```

## 파일 구조

- `confluence_client.py` - Confluence REST API 클라이언트
- `create_wiki_summary.py` - Slack 스레드 요약 위키 생성 메인 스크립트
- `run_create_wiki.sh` - 예시 실행 스크립트
