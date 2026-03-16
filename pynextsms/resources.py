"""
SMS resource — maps every SMS endpoint to a clean Python method.

Access via ``client.sms``, never instantiate directly.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from pynextsms._session import _Session
from pynextsms._validators import (
    make_reference,
    validate_phone,
    validate_phone_list,
    validate_sender_id,
    validate_text,
)
from pynextsms.models import (
    BulkSMSResponse,
    MessageRecipient,
    ScheduleOptions,
    SMSResponse,
)

logger = logging.getLogger("pynextsms")


class SMSResource:
    """
    All SMS operations. Access via ``client.sms``.
    """

    def __init__(self, session: _Session, default_sender: str) -> None:
        self._session = session
        self._default_sender = default_sender

    # ------------------------------------------------------------------
    # 1. Send one message to one or many recipients
    # ------------------------------------------------------------------

    def send(
        self,
        to: Union[str, List[str]],
        text: str,
        *,
        sender_id: Optional[str] = None,
        flash: bool = False,
        reference: Optional[str] = None,
    ) -> SMSResponse:
        """
        Send **one message** to one or more recipients.

        When *to* is a list the same *text* is broadcast to all numbers in a
        single API call.

        Args:
            to:        Phone number or list of numbers (``"255XXXXXXXXX"``).
            text:      Message body.
            sender_id: Override the client-level default sender ID for this call.
            flash:     Send as a Class-0 (flash) SMS.  Default ``False``.
            reference: Your own tracking reference.  Auto-generated if omitted.

        Returns:
            :class:`~pynextsms.SMSResponse`

        Raises:
            :class:`~pynextsms.ValidationError`: bad input before the request.
            :class:`~pynextsms.AuthenticationError`: invalid / missing token.
            :class:`~pynextsms.RateLimitError`: API rate limit hit.
            :class:`~pynextsms.APIError`: any other non-2xx response.

        Examples::

            # Single recipient
            resp = client.sms.send("255712345678", "Hello!")

            # Broadcast
            resp = client.sms.send(
                ["255712345678", "255686123903"],
                "Hello everyone!",
            )
        """
        sender = validate_sender_id(sender_id or self._default_sender)
        text = validate_text(text)
        ref = make_reference(reference)
        recipients = validate_phone_list(to)

        destination: Union[str, List[str]] = (
            recipients[0] if len(recipients) == 1 else recipients
        )

        payload: Dict[str, Any] = {
            "from": sender,
            "to": destination,
            "text": text,
            "flash": int(flash),
            "reference": ref,
        }

        logger.info(
            "send | from=%s to=%s ref=%s",
            sender,
            (
                destination
                if isinstance(destination, str)
                else f"{len(destination)} recipients"
            ),
            ref,
        )
        body = self._session.post("api/sms/v2/text/single", payload)
        return SMSResponse.from_http(200, body, reference=ref)

    # ------------------------------------------------------------------
    # 2. Send different messages to different recipients
    # ------------------------------------------------------------------

    def send_bulk(
        self,
        messages: List[MessageRecipient],
        *,
        flash: bool = False,
        reference: Optional[str] = None,
    ) -> BulkSMSResponse:
        """
        Send **different messages** to different recipients in one API call.

        Args:
            messages:  List of :class:`~pynextsms.MessageRecipient`.
            flash:     Send all as flash SMS.
            reference: Batch tracking reference.

        Returns:
            :class:`~pynextsms.BulkSMSResponse`

        Example::

            from pynextsms import MessageRecipient

            resp = client.sms.send_bulk([
                MessageRecipient("255712345678", "Hello Yohana!"),
                MessageRecipient("255655912841", "Hello Martin!"),
            ])
            print(f"Sent {resp.total} messages")
        """
        if not messages:
            from pynextsms.exceptions import ValidationError

            raise ValidationError("messages list must not be empty.")

        ref = make_reference(reference)
        msg_payloads = [m.to_payload(self._default_sender) for m in messages]

        for mp in msg_payloads:
            validate_phone(mp["to"])
            validate_text(mp["text"])
            validate_sender_id(mp["from"])

        payload = {
            "messages": msg_payloads,
            "flash": int(flash),
            "reference": ref,
        }

        logger.info("send_bulk | %d messages ref=%s", len(messages), ref)
        body = self._session.post("api/sms/v2/text/multi", payload)
        return BulkSMSResponse.from_http(200, body, total=len(messages), reference=ref)

    # ------------------------------------------------------------------
    # 3. Schedule an SMS
    # ------------------------------------------------------------------

    def schedule(
        self,
        to: str,
        text: str,
        options: ScheduleOptions,
        *,
        sender_id: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> SMSResponse:
        """
        Schedule an SMS for a future date/time, with optional recurrence.

        Args:
            to:        Recipient phone number.
            text:      Message body.
            options:   :class:`~pynextsms.ScheduleOptions` controlling when
                       (and how often) to send.
            sender_id: Override the default sender ID.
            reference: Tracking reference.

        Returns:
            :class:`~pynextsms.SMSResponse`

        Example::

            from datetime import date, time
            from pynextsms import ScheduleOptions, RepeatInterval

            opts = ScheduleOptions(
                send_date=date(2025, 6, 1),
                send_time=time(9, 0),
                repeat=RepeatInterval.DAILY,
                end_date=date(2025, 6, 30),
            )
            resp = client.sms.schedule("255712345678", "Daily tip!", opts)
        """
        sender = validate_sender_id(sender_id or self._default_sender)
        to = validate_phone(to)
        text = validate_text(text)
        ref = make_reference(reference)

        payload: Dict[str, Any] = {
            "from": sender,
            "to": to,
            "text": text,
            "reference": ref,
            **options.to_payload(),
        }

        logger.info(
            "schedule | from=%s to=%s date=%s time=%s ref=%s",
            sender,
            to,
            options.send_date,
            options.send_time,
            ref,
        )
        body = self._session.post("api/sms/v2/text/single", payload)
        return SMSResponse.from_http(200, body, reference=ref)
