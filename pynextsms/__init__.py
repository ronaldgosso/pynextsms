"""
pynextsms — Python SDK for the messaging-service.co.tz SMS API v2.

Quick-start::

    from pynextsms import SMSClient

    client = SMSClient(token="your_bearer_token", sender_id="RMNDR")
    result = client.sms.send("255763930052", "Hello from PyNextSMS!")
    print(result)
    # SMSResponse(✅ sent, http=200, ref='a3f1c2d4')
"""

from pynextsms.client import SMSClient
from pynextsms.exceptions import (
    APIError,
    AuthenticationError,
    PyNextSMSError,
    RateLimitError,
    ValidationError,
)
from pynextsms.models import (
    BulkSMSResponse,
    MessageRecipient,
    RepeatInterval,
    ScheduleOptions,
    SMSResponse,
)

__all__ = [
    "SMSClient",
    # Exceptions
    "PyNextSMSError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "RateLimitError",
    # Models
    "SMSResponse",
    "BulkSMSResponse",
    "MessageRecipient",
    "ScheduleOptions",
    "RepeatInterval",
]

__version__ = "1.0.0"
__author__ = "Ronald Gosso"
__email__ = "ronaldgosso@gmail.com"
__license__ = "MIT"
