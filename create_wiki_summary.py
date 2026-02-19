#!/usr/bin/env python3
"""Slack 스레드 요약을 Confluence 위키 페이지로 생성하는 스크립트.

사용법:
    python create_wiki_summary.py \\
        --space-url "https://cloud.wiki.woowa.in/wiki/spaces/~%EC%9C%A4%ED%9A%A8%EC%A0%95/" \\
        --title "Slack 스레드 요약 - 2026-02-19" \\
        --thread-url "https://woowahan.slack.com/archives/..." \\
        --messages messages.json

환경변수:
    CONFLUENCE_BASE_URL: Confluence 서버 URL
    CONFLUENCE_USERNAME: 사용자 이메일
    CONFLUENCE_API_TOKEN: API 토큰
"""

import argparse
import json
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from confluence_client import ConfluenceClient

load_dotenv()


def build_wiki_body(thread_url, messages, summary=None):
    """Slack 스레드 메시지들을 Confluence storage format HTML로 변환한다.

    Args:
        thread_url: Slack 스레드 URL
        messages: 메시지 목록 [{"author": "...", "content": "..."}, ...]
        summary: 요약 텍스트 (선택)

    Returns:
        Confluence storage format HTML 문자열
    """
    html_parts = []

    # 요약 섹션
    if summary:
        html_parts.append(f"<h2>요약</h2>")
        html_parts.append(f"<p>{_escape_html(summary)}</p>")

    # Slack 스레드 링크
    html_parts.append(f"<h2>원본 Slack 스레드</h2>")
    html_parts.append(
        f'<p><a href="{_escape_html(thread_url)}">'
        f"Slack 스레드 바로가기</a></p>"
    )

    # 메시지 목록
    html_parts.append(f"<h2>스레드 내용</h2>")
    html_parts.append("<table><tbody>")
    html_parts.append(
        "<tr><th>작성자</th><th>내용</th></tr>"
    )
    for msg in messages:
        author = _escape_html(msg.get("author", "Unknown"))
        content = _escape_html(msg.get("content", ""))
        html_parts.append(f"<tr><td>{author}</td><td>{content}</td></tr>")
    html_parts.append("</tbody></table>")

    # 메타 정보
    html_parts.append(f"<h2>메타 정보</h2>")
    html_parts.append("<ul>")
    html_parts.append(
        f"<li>위키 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}</li>"
    )
    html_parts.append(f"<li>메시지 수: {len(messages)}건</li>")
    html_parts.append("</ul>")

    return "\n".join(html_parts)


def _escape_html(text):
    """HTML 특수문자를 이스케이프한다."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def create_wiki_page_from_thread(
    space_url, title, thread_url, messages, summary=None
):
    """Slack 스레드 내용으로 Confluence 위키 페이지를 생성한다.

    Args:
        space_url: Confluence 스페이스 URL
        title: 위키 페이지 제목
        thread_url: Slack 스레드 URL
        messages: 메시지 목록
        summary: 요약 텍스트 (선택)

    Returns:
        생성된 페이지 정보 dict
    """
    client = ConfluenceClient()
    space_key = ConfluenceClient.parse_space_key_from_url(space_url)

    body_html = build_wiki_body(thread_url, messages, summary=summary)

    # 동일 제목의 페이지가 있으면 업데이트, 없으면 생성
    existing = client.find_page_by_title(space_key, title)
    if existing:
        page_id = existing["id"]
        version = existing["version"]["number"] + 1
        print(f"기존 페이지 업데이트: {title} (version {version})")
        result = client.update_page(page_id, title, body_html, version)
    else:
        parent_id = client.get_space_homepage(space_key)
        print(f"새 페이지 생성: {title} (스페이스: {space_key})")
        result = client.create_page(
            space_key, title, body_html, parent_id=parent_id
        )

    page_url = f"{client.base_url}/wiki{result.get('_links', {}).get('webui', '')}"
    print(f"페이지 URL: {page_url}")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Slack 스레드 요약을 Confluence 위키 페이지로 생성"
    )
    parser.add_argument(
        "--space-url",
        required=True,
        help="Confluence 스페이스 URL",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="위키 페이지 제목",
    )
    parser.add_argument(
        "--thread-url",
        required=True,
        help="Slack 스레드 URL",
    )
    parser.add_argument(
        "--messages",
        required=True,
        help="메시지 JSON 파일 경로 또는 JSON 문자열",
    )
    parser.add_argument(
        "--summary",
        default=None,
        help="스레드 요약 텍스트",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 API 호출 없이 생성될 위키 페이지 미리보기",
    )

    args = parser.parse_args()

    # 메시지 파싱
    try:
        with open(args.messages, encoding="utf-8") as f:
            messages = json.load(f)
    except (FileNotFoundError, IsADirectoryError):
        messages = json.loads(args.messages)

    if args.dry_run:
        space_key = ConfluenceClient.parse_space_key_from_url(args.space_url)
        body_html = build_wiki_body(args.thread_url, messages, summary=args.summary)
        print("=" * 60)
        print(f"[DRY RUN] 위키 페이지 미리보기")
        print(f"  스페이스: {space_key}")
        print(f"  제목: {args.title}")
        print(f"  메시지 수: {len(messages)}건")
        print("=" * 60)
        print(body_html)
        print("=" * 60)
        print(
            "\n실제 생성하려면 --dry-run 옵션을 제거하고 "
            ".env 파일에 인증 정보를 설정하세요."
        )
        return

    result = create_wiki_page_from_thread(
        space_url=args.space_url,
        title=args.title,
        thread_url=args.thread_url,
        messages=messages,
        summary=args.summary,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
