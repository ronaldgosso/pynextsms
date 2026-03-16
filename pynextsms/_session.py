"""
Low-level HTTP session used by all resource classes.

Responsibilities
----------------
* Attach ``Authorization: Bearer <token>`` and JSON headers to every request.
* Deserialise JSON responses.
* Map HTTP error codes → typed SDK exceptions.
* Automatic retry with exponential back-off on transient 5xx / connection errors.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pynextsms.exceptions import APIError, AuthenticationError, RateLimitError

logger = logging.getLogger("pynextsms")


class _Session:
    _DEFAULT_TIMEOUT = 30  # seconds

    def __init__(
        self,
        token: str,
        base_url: str,
        *,
        timeout: int = _DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        retry = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        logger.debug("POST %s payload=%s", url, payload)
        resp = self._session.post(url, json=payload, timeout=self._timeout)
        return self._handle(resp)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        logger.debug("GET  %s params=%s", url, params)
        resp = self._session.get(url, params=params, timeout=self._timeout)
        return self._handle(resp)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _handle(self, response: requests.Response) -> Dict[str, Any]:
        status = response.status_code
        try:
            body: Dict[str, Any] = response.json()
        except ValueError:
            body = {"_raw_text": response.text}

        if 200 <= status < 300:
            logger.debug("Response %s OK", status)
            return body

        if status == 401:
            raise AuthenticationError()

        if status == 429:
            retry_after = _safe_int(response.headers.get("Retry-After"))
            raise RateLimitError(retry_after=retry_after)

        api_message = (
            body.get("message")
            or body.get("error")
            or body.get("detail")
            or f"HTTP {status}"
        )
        raise APIError(
            str(api_message), status_code=status, response_body=response.text[:500]
        )

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "_Session":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


def _safe_int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None
