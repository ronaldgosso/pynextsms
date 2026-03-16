"""
Full test suite for PyNextSMS SDK.

Run:  pytest tests/ -v
Cov:  pytest tests/ --cov=pynextsms --cov-report=term-missing
"""

from __future__ import annotations

from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest
import requests

from pynextsms import (
    SMSClient,
    SMSResponse,
    BulkSMSResponse,
    MessageRecipient,
    ScheduleOptions,
    RepeatInterval,
    AuthenticationError,
    ValidationError,
    APIError,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_client(**kw) -> SMSClient:
    return SMSClient(**{"token": "test_tok", "sender_id": "BRAND", **kw})


def mock_resp(status: int = 200, body: dict | None = None) -> MagicMock:
    r = MagicMock(spec=requests.Response)
    r.status_code = status
    r.json.return_value = body or {}
    r.text = str(body or {})
    r.headers = {}
    return r


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestClientInit:
    def test_raises_with_no_token(self, monkeypatch):
        monkeypatch.delenv("PYNEXTSMS_TOKEN", raising=False)
        with pytest.raises(AuthenticationError):
            SMSClient()

    def test_reads_token_from_env(self, monkeypatch):
        monkeypatch.setenv("PYNEXTSMS_TOKEN", "env_tok")
        monkeypatch.setenv("PYNEXTSMS_SENDER_ID", "ENVBRAND")
        c = SMSClient()
        assert c._token == "env_tok"
        c.close()

    def test_context_manager_closes(self):
        with make_client() as c:
            assert c._token == "test_tok"

    def test_repr_contains_sender(self):
        c = make_client()
        assert "BRAND" in repr(c)
        c.close()


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


class TestValidators:
    def test_valid_phone_returns_cleaned(self):
        from pynextsms._validators import validate_phone

        assert validate_phone("255712345678") == "255712345678"

    def test_phone_bad_prefix_raises(self):
        from pynextsms._validators import validate_phone

        with pytest.raises(ValidationError, match="Invalid phone number"):
            validate_phone("0712345678")

    def test_phone_too_short_raises(self):
        from pynextsms._validators import validate_phone

        with pytest.raises(ValidationError):
            validate_phone("25571234")

    def test_sender_too_long_raises(self):
        from pynextsms._validators import validate_sender_id

        with pytest.raises(ValidationError, match="too long"):
            validate_sender_id("AVERYLONGBRANDNAME")

    def test_empty_text_raises(self):
        from pynextsms._validators import validate_text

        with pytest.raises(ValidationError):
            validate_text("   ")

    def test_reference_too_long_raises(self):
        from pynextsms._validators import make_reference

        with pytest.raises(ValidationError):
            make_reference("x" * 51)

    def test_reference_auto_generated_is_8_chars(self):
        from pynextsms._validators import make_reference

        assert len(make_reference(None)) == 8

    def test_too_many_recipients_raises(self):
        from pynextsms._validators import validate_phone_list

        with pytest.raises(ValidationError, match="Too many"):
            validate_phone_list([f"255712{str(i).zfill(6)}" for i in range(1001)])

    def test_single_string_accepted_as_list(self):
        from pynextsms._validators import validate_phone_list

        result = validate_phone_list("255712345678")
        assert result == ["255712345678"]


# ---------------------------------------------------------------------------
# sms.send
# ---------------------------------------------------------------------------


class TestSend:
    @patch("pynextsms._session.requests.Session.post")
    def test_single_recipient_success(self, mock_post):
        mock_post.return_value = mock_resp(200, {"message_id": "m1"})
        c = make_client()
        resp = c.sms.send("255712345678", "Hello!")
        assert resp.successful
        assert resp.status_code == 200
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_custom_reference_echoed(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        resp = c.sms.send("255712345678", "Hi", reference="myref")
        assert resp.reference == "myref"
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_multi_recipient_sends_list(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        c.sms.send(["255712345678", "255686123903"], "Broadcast")
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args.args[1]
        assert isinstance(payload["to"], list)
        assert len(payload["to"]) == 2
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_flash_sets_flag(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        c.sms.send("255712345678", "Flash!", flash=True)
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args.args[1]
        assert payload["flash"] == 1
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_sender_id_override(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        c.sms.send("255712345678", "Hi", sender_id="CUSTOM")
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args.args[1]
        assert payload["from"] == "CUSTOM"
        c.close()

    def test_invalid_phone_raises_before_request(self):
        c = make_client()
        with pytest.raises(ValidationError):
            c.sms.send("0712345678", "Hi")
        c.close()

    def test_empty_text_raises_before_request(self):
        c = make_client()
        with pytest.raises(ValidationError):
            c.sms.send("255712345678", "")
        c.close()


# ---------------------------------------------------------------------------
# sms.send_bulk
# ---------------------------------------------------------------------------


class TestSendBulk:
    @patch("pynextsms._session.requests.Session.post")
    def test_bulk_success(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        resp = c.sms.send_bulk(
            [
                MessageRecipient("255712345678", "Hello Yohana!"),
                MessageRecipient("255655912841", "Hello Martin!"),
            ]
        )
        assert resp.successful
        assert resp.total == 2
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_bulk_per_message_sender_override(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        c.sms.send_bulk([MessageRecipient("255712345678", "Hi!", sender_id="CUSTOM")])
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args.args[1]
        assert payload["messages"][0]["from"] == "CUSTOM"
        c.close()

    def test_empty_messages_raises(self):
        c = make_client()
        with pytest.raises(ValidationError):
            c.sms.send_bulk([])
        c.close()


# ---------------------------------------------------------------------------
# sms.schedule
# ---------------------------------------------------------------------------


class TestSchedule:
    @patch("pynextsms._session.requests.Session.post")
    def test_schedule_one_time(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        opts = ScheduleOptions(send_date=date(2025, 6, 1), send_time=time(9, 0))
        resp = c.sms.schedule("255712345678", "Reminder!", opts)
        assert resp.successful
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_schedule_repeat_payload(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        opts = ScheduleOptions(
            send_date=date(2025, 6, 1),
            send_time=time(9, 0),
            repeat=RepeatInterval.DAILY,
            end_date=date(2025, 6, 30),
        )
        c.sms.schedule("255712345678", "Daily!", opts)
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args.args[1]
        assert payload["repeat"] == "daily"
        assert payload["end_date"] == "2025-06-30"
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_schedule_no_repeat_has_no_repeat_key(self, mock_post):
        mock_post.return_value = mock_resp(200, {})
        c = make_client()
        opts = ScheduleOptions(send_date=date(2025, 6, 1), send_time=time(9, 0))
        c.sms.schedule("255712345678", "Once!", opts)
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args.args[1]
        assert "repeat" not in payload
        c.close()


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    @patch("pynextsms._session.requests.Session.post")
    def test_401_raises_auth_error(self, mock_post):
        mock_post.return_value = mock_resp(401, {"message": "Unauthorized"})
        c = make_client()
        with pytest.raises(AuthenticationError):
            c.sms.send("255712345678", "Hi")
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_429_raises_rate_limit_with_retry_after(self, mock_post):
        r = mock_resp(429, {})
        r.headers = {"Retry-After": "30"}
        mock_post.return_value = r
        c = make_client()
        with pytest.raises(RateLimitError) as exc_info:
            c.sms.send("255712345678", "Hi")
        assert exc_info.value.retry_after == 30
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_500_raises_api_error(self, mock_post):
        mock_post.return_value = mock_resp(500, {"message": "Server Error"})
        c = make_client()
        with pytest.raises(APIError) as exc_info:
            c.sms.send("255712345678", "Hi")
        assert exc_info.value.status_code == 500
        c.close()

    @patch("pynextsms._session.requests.Session.post")
    def test_non_json_body_does_not_crash(self, mock_post):
        r = mock_resp(400)
        r.json.side_effect = ValueError("no json")
        r.text = "Bad Request"
        mock_post.return_value = r
        c = make_client()
        with pytest.raises(APIError):
            c.sms.send("255712345678", "Hi")
        c.close()


# ---------------------------------------------------------------------------
# Model helpers
# ---------------------------------------------------------------------------


class TestModels:
    def test_sms_response_to_dict(self):
        resp = SMSResponse(successful=True, status_code=200, reference="abc")
        d = resp.to_dict()
        assert d["successful"] is True
        assert d["reference"] == "abc"

    def test_sms_response_to_json(self):
        import json

        resp = SMSResponse(successful=True, status_code=200)
        parsed = json.loads(resp.to_json())
        assert parsed["successful"] is True

    def test_bulk_response_total(self):
        resp = BulkSMSResponse(successful=True, status_code=200, total=5)
        assert resp.total == 5

    def test_schedule_options_time_format(self):
        opts = ScheduleOptions(send_date=date(2025, 1, 5), send_time=time(8, 5))
        p = opts.to_payload()
        assert p["date"] == "2025-01-05"
        assert p["time"] == "08:05"

    def test_message_recipient_uses_default_sender(self):
        mr = MessageRecipient("255712345678", "Hi")
        p = mr.to_payload("DEFAULTBRAND")
        assert p["from"] == "DEFAULTBRAND"

    def test_message_recipient_overrides_sender(self):
        mr = MessageRecipient("255712345678", "Hi", sender_id="CUSTOM")
        p = mr.to_payload("DEFAULTBRAND")
        assert p["from"] == "CUSTOM"

    def test_repeat_interval_values(self):
        assert RepeatInterval.HOURLY.value == "hourly"
        assert RepeatInterval.DAILY.value == "daily"
        assert RepeatInterval.WEEKLY.value == "weekly"
        assert RepeatInterval.MONTHLY.value == "monthly"

#------------------------------------------------------
# Next update instructions after git commit
# git tag v1.1.0 ensures that PyPI version is updated too
# git push origin v1.1.0 ensures that GitHub version is updated too
#------------------------------------------------------
