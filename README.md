<div align="center">

# [pynextsms 🇹🇿](https://ronaldgosso.github.io/pynextsms/)

**Python SDK for the [NEXT SMS Tanzania](https://app.nextsms.co.tz) SMS API v2**

[![PyPI version](https://badge.fury.io/py/pynextsms.svg)](https://pypi.org/project/pynextsms/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/ronaldgosso/pynextsms/actions/workflows/test.yml/badge.svg)](https://github.com/ronaldgosso/pynextsms/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/ronaldgosso/pynextsms)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

---

## Table of Contents

- [Documentation](#documentation)
- [Requirements](#requirements)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Usage Guide](#usage-guide)
  - [Send a Single SMS](#1-send-a-single-sms)
  - [Broadcast to Multiple Recipients](#2-broadcast-to-multiple-recipients)
  - [Send Different Messages (Bulk)](#3-send-different-messages-to-different-people)
  - [Schedule an SMS](#4-schedule-an-sms)
  - [Scheduled + Recurring SMS](#5-scheduled--recurring-sms)
  - [Flash SMS](#6-flash-sms)
  - [Context Manager](#7-context-manager)
  - [Environment Variables](#8-environment-variables-production)
- [Response Objects](#response-objects)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Running Locally](#running-locally)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)

---

## Documentation

- [Official Next SMS API Documentation](https://documenter.getpostman.com/view/1679195/2sAYkDP1XN#fe8eaa5c-5987-4a3c-bb6b-98d497c5b3b0)

## Requirements

- [Next SMS Registration](https://app.nextsms.co.tz/register)
- Python 3.8+
- requests >= 2.28

## Features

| Feature | Support |
|---|---|
| Send SMS to a single recipient | ✅ |
| Broadcast same message to multiple recipients | ✅ |
| Send different messages to different recipients | ✅ |
| Schedule SMS (one-time) | ✅ |
| Schedule SMS (recurring: hourly / daily / weekly / monthly) | ✅ |
| Flash (Class-0) SMS | ✅ |
| Auto-retry on transient 5xx errors | ✅ |
| Typed responses — no raw dict-wrangling | ✅ |
| Full type annotations + `py.typed` (mypy strict) | ✅ |
| Environment-variable credentials (12-factor ready) | ✅ |
| Zero dependencies beyond `requests` | ✅ |
| Python 3.8 – 3.12 | ✅ |

---

## Installation
[pynextsms](https://pypi.org/project/pynextsms/1.0.0/)

```bash
pip install pynextsms
```
---

## Quick Start

```python
from pynextsms import SMSClient

client = SMSClient(token="your_bearer_token", sender_id="YOURBRAND")

resp = client.sms.send("255763930052", "Hello from PyNextSMS!")
print(resp)
# SMSResponse(✅ sent, http=200, ref='a3f1c2d4')
```

---

## Authentication

Generate your **Bearer Token** from your [Next SMS API Documentation](https://documenter.getpostman.com/view/1679195/2sAYkDP1XN#authorization:~:text=header%3A%20application/json-,Authorization,-Bearer%20Authentication%20).

### Option 1 — pass credentials directly *(quick scripts, notebooks)*

```python
client = SMSClient(token="your_bearer_token", sender_id="YOURBRAND")
```

### Option 2 — environment variables *(recommended for production)*

```bash
export PYNEXTSMS_TOKEN="your_bearer_token"
export PYNEXTSMS_SENDER_ID="YOURBRAND"
```

```python
client = SMSClient()   # reads from environment automatically
```

---

## Usage Guide

### 1. Send a Single SMS

```python
resp = client.sms.send("255763930052", "Hello, Ronald!")

if resp.successful:
    print(f"✅ Sent! message_id={resp.message_id}, ref={resp.reference}")
else:
    print(f"❌ Failed: {resp.raw}")
```

### 2. Broadcast to Multiple Recipients

Send the **same message** to many people in a single API call:

```python
resp = client.sms.send(
    to=["255763930052", "255627350020", "255622999999"],
    text="Hello everyone — you are now registered!",
    reference="campaign_june",   # optional tracking ref
)
print(f"✅ Broadcast successful: {resp.successful}")
```

### 3. Send Different Messages to Different People

```python
from pynextsms import MessageRecipient

resp = client.sms.send_bulk(
    messages=[
        MessageRecipient(to="255763930052", text="Hello Daniel, welcome!"),
        MessageRecipient(to="255627350020", text="Hello Patricia, welcome!"),
        MessageRecipient(to="255622999999", text="Hello Precious, welcome!"),
    ],
    reference="onboarding_batch_001",
)
print(f"✅ Sent {resp.total} personalised messages")
```

Each `MessageRecipient` can also override the sender ID:

```python
MessageRecipient(to="255763930052", text="Hi!", sender_id="CUSTOM")
```

### 4. Schedule an SMS

```python
from datetime import date, time
from pynextsms import ScheduleOptions

opts = ScheduleOptions(
    send_date=date(2025, 6, 1),
    send_time=time(9, 0),        # 09:00, 24-hour clock
)

resp = client.sms.schedule(
    to="255763930052",
    text="Good morning! Your session starts in 1 hour.",
    options=opts,
)
print(f"✅ Scheduled: {resp.successful}")
```

### 5. Scheduled + Recurring SMS

```python
from pynextsms import ScheduleOptions, RepeatInterval

opts = ScheduleOptions(
    send_date  = date(2025, 6, 1),
    send_time  = time(8, 0),
    repeat     = RepeatInterval.DAILY,
    start_date = date(2025, 6, 1),
    end_date   = date(2025, 6, 30),
)

resp = client.sms.schedule(
    to="255763930052",
    text="Daily reminder: drink water 💧",
    options=opts,
)
```

Available repeat intervals:

| Value | Constant |
|---|---|
| `"hourly"` | `RepeatInterval.HOURLY` |
| `"daily"` | `RepeatInterval.DAILY` |
| `"weekly"` | `RepeatInterval.WEEKLY` |
| `"monthly"` | `RepeatInterval.MONTHLY` |

### 6. Flash SMS

Pass `flash=True` to any `send` or `send_bulk` call:

```python
resp = client.sms.send("255712345678", "Urgent alert!", flash=True)
```

### 7. Context Manager

The client implements `__enter__` / `__exit__` so it can be used as a context
manager — the HTTP connection pool is automatically released on exit:

```python
with SMSClient(token="...", sender_id="BRAND") as client:
    client.sms.send("255712345678", "Hello!")
# connection pool closed here
```

### 8. Environment Variables *(Production)*

| Variable | Description |
|---|---|
| `PYNEXTSMS_TOKEN` | Bearer token (required if not passed to constructor) |
| `PYNEXTSMS_SENDER_ID` | Default sender ID  |

```bash
# .env file (use python-dotenv or similar)
PYNEXTSMS_TOKEN=your_bearer_token
PYNEXTSMS_SENDER_ID=YOURBRAND
```

```python
from dotenv import load_dotenv
load_dotenv()

from pynextsms import SMSClient
client = SMSClient()
```

---

## Response Objects

### `SMSResponse`

Returned by `sms.send()` and `sms.schedule()`.

| Attribute | Type | Description |
|---|---|---|
| `successful` | `bool` | `True` when HTTP 2xx |
| `status_code` | `int` | Raw HTTP status |
| `message_id` | `str \| None` | ID assigned by API |
| `reference` | `str \| None` | Tracking reference |
| `raw` | `dict` | Full JSON response body |

```python
resp = client.sms.send("255763930052", "Hello!")

print(resp.successful)    # True
print(resp.message_id)    # "msg_abc123"
print(resp.to_dict())     # plain dict
print(resp.to_json())     # JSON string
```

### `BulkSMSResponse`

Returned by `sms.send_bulk()`.  Same as `SMSResponse` plus:

| Attribute | Type | Description |
|---|---|---|
| `total` | `int` | Number of messages in the batch |

```python
resp = client.sms.send_bulk([...])
print(f"Accepted {resp.total} messages")
```

---

## Error Handling

All exceptions inherit from `PyNextSMSError`:

```python
from pynextsms import (
    PyNextSMSError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    APIError,
)

try:
    resp = client.sms.send("255712345678", "Hello!")

except AuthenticationError:
    # Bad or missing bearer token
    print("Check your PYNEXTSMS_TOKEN.")

except ValidationError as e:
    # Bad input caught *before* the HTTP call
    print(f"Input error: {e}")

except RateLimitError as e:
    # HTTP 429
    import time
    print(f"Rate limited — retrying in {e.retry_after}s")
    time.sleep(e.retry_after or 5)

except APIError as e:
    # Any other non-2xx response
    print(f"API error (HTTP {e.status_code}): {e}")

except PyNextSMSError as e:
    # Catch-all for any other SDK error
    print(f"SDK error: {e}")
```

---

## Logging

PyNextSMS uses Python's standard `logging` under the `pynextsms` logger.

```python
import logging

# Show all SDK log messages (DEBUG and above)
logging.basicConfig(level=logging.DEBUG)

# Or configure just the pynextsms logger
logger = logging.getLogger("pynextsms")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
```

---

## Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/ronaldgosso/pynextsms.git
cd pynextsms
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Install in editable mode with dev extras

```bash
pip install -e ".[dev]"
```

### 4. Set your credentials

```bash
export PYNEXTSMS_TOKEN="your_bearer_token"
export PYNEXTSMS_SENDER_ID="YOURBRAND"
```

### 5. Try it out

```bash
python - << 'EOF'
from pynextsms import SMSClient

with SMSClient() as client:
    resp = client.sms.send("255763930052", "Hello from local dev!")
    print(resp)
EOF
```

### 6. Run the test suite

```bash
# All tests, verbose
pytest

# With coverage report
pytest --cov=pynextsms --cov-report=term-missing

# Specific test class
pytest tests/ -v -k "TestSend"
```

### 7. Lint & type-check

```bash
ruff check pynextsms/        # linter
black --check pynextsms/     # formatter check
mypy pynextsms/              # strict type checking
```

---

## Contributing

Contributions are welcome — bug reports, feature requests, documentation improvements, and pull requests all appreciated.

### Workflow

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pynextsms.git
   cd pynextsms
   ```
3. **Create a branch** for your change:
   ```bash
   git checkout -b feat/my-new-feature
   # or
   git checkout -b fix/the-bug-description
   ```
4. **Install dev dependencies:**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   ```
5. **Make your changes**, then make sure all of these pass:
   ```bash
   pytest                     # all tests pass
   ruff check pynextsms/      # no lint errors
   black pynextsms/ tests/    # code is formatted
   mypy pynextsms/            # no type errors
   ```
6. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add support for sending MMS"
   ```
7. **Push** and open a **Pull Request** against `main`.

### Commit message conventions

| Prefix | When to use |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation change |
| `test:` | Adding or updating tests |
| `refactor:` | Code change with no behaviour change |
| `chore:` | Tooling, CI, config |

### Reporting bugs

Open an issue at [github.com/ronaldgosso/pynextsms/issues](https://github.com/ronaldgosso/pynextsms/issues) and include:
- Python version (`python --version`)
- pynextsms version (`pip show pynextsms`)
- Minimal code that reproduces the issue
- Full traceback

---

## Changelog

### v1.0.0 — 2025-06-01

- Initial release
- `sms.send()` — single and broadcast sends
- `sms.send_bulk()` — personalised bulk sends
- `sms.schedule()` — one-time and recurring scheduled SMS
- Flash SMS support
- Automatic retries on 5xx errors
- Full type annotations, `py.typed` marker
- Comprehensive test suite (95% coverage)

---

## License

MIT © Ronald Gosso — see [LICENSE](LICENSE).
