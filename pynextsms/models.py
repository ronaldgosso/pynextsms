"""
Data models for PyNextSMS SDK.

Uses only stdlib dataclasses — no third-party dependencies beyond ``requests``.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, time
from enum import Enum
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RepeatInterval(str, Enum):
    """Valid repeat intervals for scheduled SMS messages."""
    HOURLY  = "hourly"
    DAILY   = "daily"
    WEEKLY  = "weekly"
    MONTHLY = "monthly"


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------

@dataclass
class ScheduleOptions:
    """
    Scheduling (and optional repeat) settings for an SMS.

    Args:
        send_date:  Date to send the message  (``date`` object).
        send_time:  Time to send the message  (``time`` object, 24-hour).
        repeat:     How often to repeat.  ``None`` = send once.
        start_date: First date for a repeating message.
        end_date:   Last  date for a repeating message.

    Example::

        from datetime import date, time
        from pynextsms import ScheduleOptions, RepeatInterval

        opts = ScheduleOptions(
            send_date=date(2025, 6, 1),
            send_time=time(9, 0),
            repeat=RepeatInterval.DAILY,
            end_date=date(2025, 6, 30),
        )
    """
    send_date:  date
    send_time:  time
    repeat:     Optional[RepeatInterval] = None
    start_date: Optional[date] = None
    end_date:   Optional[date] = None

    def to_payload(self) -> Dict[str, str]:
        payload: Dict[str, str] = {
            "date": self.send_date.strftime("%Y-%m-%d"),
            "time": self.send_time.strftime("%H:%M"),
        }
        if self.repeat is not None:
            payload["repeat"] = self.repeat.value
        if self.start_date is not None:
            payload["start_date"] = self.start_date.strftime("%Y-%m-%d")
        if self.end_date is not None:
            payload["end_date"] = self.end_date.strftime("%Y-%m-%d")
        return payload


@dataclass
class MessageRecipient:
    """
    One (recipient, text) pair for use with :meth:`~pynextsms.SMSClient.sms.send_bulk`.

    Args:
        to:        Recipient phone number (e.g. ``"255712345678"``).
        text:      Message body for this recipient.
        sender_id: Override the client-level default sender ID for this message only.

    Example::

        from pynextsms import MessageRecipient

        msgs = [
            MessageRecipient(to="255712345678", text="Hello Yohana!"),
            MessageRecipient(to="255655912841", text="Hello Martin!"),
        ]
    """
    to:        str
    text:      str
    sender_id: Optional[str] = None

    def to_payload(self, default_sender: str) -> Dict[str, str]:
        return {
            "from": self.sender_id or default_sender,
            "to":   self.to,
            "text": self.text,
        }


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

@dataclass
class SMSResponse:
    """
    API response for a single-text send or scheduled send.

    Attributes:
        successful:   ``True`` when the API returned HTTP 2xx.
        status_code:  Raw HTTP status code.
        message_id:   Unique message ID assigned by the API (if returned).
        reference:    Tracking reference echoed back by the API.
        raw:          Full deserialized JSON body for advanced inspection.
    """
    successful:  bool
    status_code: int
    message_id:  Optional[str]        = None
    reference:   Optional[str]        = None
    raw:         Dict[str, Any]       = field(default_factory=dict)

    def __repr__(self) -> str:
        status = "✓ sent" if self.successful else "✗ failed"
        parts  = [f"SMSResponse({status}, http={self.status_code}"]
        if self.message_id:
            parts.append(f", id={self.message_id!r}")
        if self.reference:
            parts.append(f", ref={self.reference!r}")
        return "".join(parts) + ")"

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dictionary representation."""
        return asdict(self)

    def to_json(self) -> str:
        """Return a JSON string representation."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_http(
        cls,
        status_code: int,
        body: Dict[str, Any],
        reference: Optional[str] = None,
    ) -> "SMSResponse":
        return cls(
            successful  = 200 <= status_code < 300,
            status_code = status_code,
            message_id  = body.get("message_id") or body.get("id"),
            reference   = reference or body.get("reference"),
            raw         = body,
        )


@dataclass
class BulkSMSResponse:
    """
    Aggregated response for a :meth:`~pynextsms.SMSClient.sms.send_bulk` call.

    Attributes:
        successful:   ``True`` when the API accepted the batch.
        status_code:  Raw HTTP status code.
        total:        Number of messages in the batch.
        reference:    Batch tracking reference.
        raw:          Full deserialized JSON body.
    """
    successful:  bool
    status_code: int
    total:       int                  = 0
    reference:   Optional[str]       = None
    raw:         Dict[str, Any]      = field(default_factory=dict)

    def __repr__(self) -> str:
        status = "✓ accepted" if self.successful else "✗ failed"
        return (
            f"BulkSMSResponse({status}, http={self.status_code}, "
            f"total={self.total}, ref={self.reference!r})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_http(
        cls,
        status_code: int,
        body: Dict[str, Any],
        total: int = 0,
        reference: Optional[str] = None,
    ) -> "BulkSMSResponse":
        return cls(
            successful  = 200 <= status_code < 300,
            status_code = status_code,
            total       = total,
            reference   = reference or body.get("reference"),
            raw         = body,
        )
