"""Confluence Wiki API Client.

Confluence REST API를 사용하여 위키 페이지를 생성/조회/업데이트하는 클라이언트.
"""

import os
import json
from urllib.parse import unquote

import requests
from requests.auth import HTTPBasicAuth


class ConfluenceClient:
    """Confluence REST API 클라이언트."""

    def __init__(self, base_url=None, username=None, api_token=None):
        self.base_url = (base_url or os.environ.get("CONFLUENCE_BASE_URL", "")).rstrip("/")
        self.username = username or os.environ.get("CONFLUENCE_USERNAME", "")
        self.api_token = api_token or os.environ.get("CONFLUENCE_API_TOKEN", "")
        self.auth = HTTPBasicAuth(self.username, self.api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _api_url(self, path):
        return f"{self.base_url}/wiki/rest/api{path}"

    def get_space(self, space_key):
        """스페이스 정보를 조회한다."""
        resp = self.session.get(self._api_url(f"/space/{space_key}"))
        resp.raise_for_status()
        return resp.json()

    def get_space_homepage(self, space_key):
        """스페이스의 홈페이지(루트 페이지) ID를 반환한다."""
        resp = self.session.get(
            self._api_url(f"/space/{space_key}"),
            params={"expand": "homepage"},
        )
        resp.raise_for_status()
        data = resp.json()
        homepage = data.get("homepage")
        if homepage:
            return homepage["id"]
        return None

    def find_page_by_title(self, space_key, title):
        """스페이스 내에서 제목으로 페이지를 검색한다."""
        resp = self.session.get(
            self._api_url("/content"),
            params={
                "spaceKey": space_key,
                "title": title,
                "type": "page",
                "expand": "version",
            },
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return results[0] if results else None

    def create_page(self, space_key, title, body_html, parent_id=None):
        """새 위키 페이지를 생성한다.

        Args:
            space_key: Confluence 스페이스 키 (예: '~윤효정')
            title: 페이지 제목
            body_html: 페이지 본문 (Confluence storage format HTML)
            parent_id: 부모 페이지 ID (None이면 스페이스 루트에 생성)

        Returns:
            생성된 페이지 정보 dict
        """
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": body_html,
                    "representation": "storage",
                }
            },
        }
        if parent_id:
            payload["ancestors"] = [{"id": str(parent_id)}]

        resp = self.session.post(self._api_url("/content"), json=payload)
        resp.raise_for_status()
        return resp.json()

    def update_page(self, page_id, title, body_html, version_number):
        """기존 위키 페이지를 업데이트한다."""
        payload = {
            "type": "page",
            "title": title,
            "version": {"number": version_number},
            "body": {
                "storage": {
                    "value": body_html,
                    "representation": "storage",
                }
            },
        }
        resp = self.session.put(self._api_url(f"/content/{page_id}"), json=payload)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def parse_space_key_from_url(space_url):
        """위키 스페이스 URL에서 스페이스 키를 추출한다.

        예: 'https://cloud.wiki.woowa.in/wiki/spaces/~%EC%9C%A4%ED%9A%A8%EC%A0%95/'
            -> '~윤효정'
        """
        # URL에서 /spaces/ 이후의 경로를 추출
        parts = space_url.rstrip("/").split("/spaces/")
        if len(parts) < 2:
            raise ValueError(f"Invalid space URL: {space_url}")
        space_key = parts[1].split("/")[0]
        return unquote(space_key)
