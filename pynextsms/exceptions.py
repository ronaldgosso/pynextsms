"""
Custom exceptions for PyNextSMS SDK.

Hierarchy::

    PyNextSMSError
    ├── AuthenticationError   – 401 / bad or missing token
    ├── ValidationError       – Bad inputs caught before any HTTP call
    ├── RateLimitError        – 429 Too Many Requests
    └── APIError              – Any other non-2xx HTTP response
"""
from __future__ import annotations

from typing import Optional


class PyNextSMSError(Exception):
    """Base exception for all PyNextSMS errors."""

    def __init__(self, message: str, *, hint: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def __str__(self) -> str:
        base = self.message
        if self.hint:
            base += f"\n  Hint: {self.hint}"
        return base


class AuthenticationError(PyNextSMSError):
    """Raised when the API token is missing, expired, or rejected (HTTP 401)."""

    def __init__(
        self,
        message: str = "Invalid or missing bearer token.",
    ) -> None:
        super().__init__(
            message,
            hint=(
                "Pass your token via SMSClient(token='...') "
                "or set the PYNEXTSMS_TOKEN environment variable."
            ),
        )


class ValidationError(PyNextSMSError):
    """Raised for invalid input *before* an HTTP request is sent."""
    pass


class RateLimitError(PyNextSMSError):
    """Raised when the API returns HTTP 429 Too Many Requests."""

    def __init__(self, retry_after: Optional[int] = None) -> None:
        hint = (
            f"Retry after {retry_after} seconds."
            if retry_after
            else "Slow down your requests and try again."
        )
        super().__init__("Rate limit exceeded.", hint=hint)
        self.retry_after = retry_after


class APIError(PyNextSMSError):
    """Raised for any other non-2xx API response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"HTTP {self.status_code}")
        if self.response_body:
            parts.append(f"Response: {self.response_body}")
        return " | ".join(parts)
