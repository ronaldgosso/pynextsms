"""
SMSClient — the single entry point for the PyNextSMS SDK.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from pynextsms._session import _Session
from pynextsms._validators import validate_sender_id
from pynextsms.exceptions import AuthenticationError
from pynextsms.resources import SMSResource

logger = logging.getLogger("pynextsms")

_DEFAULT_BASE_URL = "https://messaging-service.co.tz"


class SMSClient:
    """
    Top-level client for the messaging-service.co.tz SMS API v2.

    Args:
        token:       Bearer token for authentication.
                     Falls back to the ``PYNEXTSMS_TOKEN`` environment variable.
        sender_id:   Default sender ID (≤ 11 chars) used for every message
                     unless overridden per-call.
                     Falls back to ``PYNEXTSMS_SENDER_ID`` env var.
        base_url:    API base URL.  Override for staging / test environments.
        timeout:     HTTP request timeout in seconds.  Default ``30``.
        max_retries: Automatic retries on transient 5xx errors.  Default ``3``.

    Raises:
        :class:`~pynextsms.AuthenticationError`:
            If no token is provided and ``PYNEXTSMS_TOKEN`` is not set.
        :class:`~pynextsms.ValidationError`:
            If *sender_id* exceeds 11 characters.

    Examples::

        # Explicit credentials
        client = SMSClient(token="abc123", sender_id="MYBRAND")

        # Environment-variable credentials (recommended for production)
        # export PYNEXTSMS_TOKEN=abc123
        # export PYNEXTSMS_SENDER_ID=MYBRAND
        client = SMSClient()

        # Context manager — auto-closes the connection pool
        with SMSClient(token="abc123", sender_id="BRAND") as client:
            client.sms.send("255712345678", "Hello!")
    """

    def __init__(
        self,
        token:       Optional[str] = None,
        *,
        sender_id:   Optional[str] = None,
        base_url:    str           = _DEFAULT_BASE_URL,
        timeout:     int           = 30,
        max_retries: int           = 3,
    ) -> None:
        resolved_token = token or os.environ.get("PYNEXTSMS_TOKEN")
        if not resolved_token:
            raise AuthenticationError(
                "No API token provided. "
                "Pass token='...' or set the PYNEXTSMS_TOKEN environment variable."
            )

        resolved_sender = sender_id or os.environ.get("PYNEXTSMS_SENDER_ID", "")
        validated_sender = validate_sender_id(resolved_sender) if resolved_sender else ""

        self._token     = resolved_token
        self._sender_id = validated_sender
        self._base_url  = base_url

        self._session = _Session(
            token       = resolved_token,
            base_url    = base_url,
            timeout     = timeout,
            max_retries = max_retries,
        )

        # ── Resource namespaces ──────────────────────────────────────────
        self.sms = SMSResource(self._session, self._sender_id)

        logger.debug(
            "SMSClient ready | base_url=%s sender_id=%s",
            base_url,
            self._sender_id or "(not set)",
        )

    # Context-manager support ------------------------------------------------

    def __enter__(self) -> "SMSClient":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying connection pool."""
        self._session.close()

    def __repr__(self) -> str:
        return f"SMSClient(sender_id={self._sender_id!r}, base_url={self._base_url!r})"
