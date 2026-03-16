"""
Input validation helpers.

Every public function raises :class:`~pynextsms.ValidationError` on bad input,
so callers never need boilerplate guards.
"""
from __future__ import annotations

import re
import uuid
from typing import List, Union

from pynextsms.exceptions import ValidationError

# Tanzania MSISDNs: 255 + network digit (6 or 7) + 8 digits = 12 total
_TZ_PHONE_RE = re.compile(r"^255[67]\d{8}$")


def validate_phone(number: str, *, field: str = "to") -> str:
    """Validate a single Tanzanian phone number. Returns cleaned string."""
    cleaned = str(number).strip()
    if not _TZ_PHONE_RE.match(cleaned):
        raise ValidationError(
            f"Invalid phone number in field '{field}': {cleaned!r}",
            hint="Numbers must start with 255 followed by 9 digits, e.g. '255712345678'.",
        )
    return cleaned


def validate_phone_list(numbers: Union[str, List[str]]) -> List[str]:
    """Validate one or many phone numbers. Always returns a list."""
    if isinstance(numbers, str):
        numbers = [numbers]
    if not numbers:
        raise ValidationError("Recipient list must not be empty.")
    if len(numbers) > 1000:
        raise ValidationError(
            f"Too many recipients: {len(numbers)}. Maximum per call is 1 000.",
            hint="Split large batches into chunks of ≤ 1 000.",
        )
    return [validate_phone(n) for n in numbers]


def validate_sender_id(sender_id: str) -> str:
    cleaned = str(sender_id).strip()
    if not cleaned:
        raise ValidationError("sender_id must not be empty.")
    if len(cleaned) > 11:
        raise ValidationError(
            f"sender_id '{cleaned}' is too long ({len(cleaned)} chars). Maximum is 11.",
        )
    return cleaned


def validate_text(text: str) -> str:
    cleaned = str(text).strip()
    if not cleaned:
        raise ValidationError("Message text must not be empty.")
    return cleaned


def make_reference(reference: Union[str, None]) -> str:
    """Return the provided reference or auto-generate an 8-char hex string."""
    if reference:
        cleaned = str(reference).strip()
        if len(cleaned) > 50:
            raise ValidationError("reference must be ≤ 50 characters.")
        return cleaned
    return uuid.uuid4().hex[:8]
