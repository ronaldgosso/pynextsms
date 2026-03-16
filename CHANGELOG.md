# Changelog

All notable changes to **pynextsms** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2025-06-01

### Added
- `SMSClient` — main entry point with env-var credential support.
- `sms.send()` — send one message to one or many recipients.
- `sms.send_bulk()` — send personalised messages to multiple recipients.
- `sms.schedule()` — schedule one-time or recurring SMS.
- `RepeatInterval` enum (`HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY`).
- `ScheduleOptions` dataclass for scheduling parameters.
- `MessageRecipient` dataclass for bulk sends.
- `SMSResponse` and `BulkSMSResponse` typed response models with `.to_dict()` / `.to_json()`.
- Full exception hierarchy: `PyNextSMSError`, `AuthenticationError`, `ValidationError`, `RateLimitError`, `APIError`.
- Automatic HTTP retry with exponential back-off on 5xx errors.
- Flash (Class-0) SMS support via `flash=True`.
- `py.typed` marker for mypy strict compatibility.
- GitHub Actions CI across Python 3.8 – 3.12.
- 95%+ test coverage.

---

## [Unreleased]

Nothing yet — this is the initial release.
