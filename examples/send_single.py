"""Example: Send a single SMS.  Run: python examples/send_single.py"""
import os
from pynextsms import SMSClient, ValidationError, AuthenticationError, APIError

def main():
    client = SMSClient(
        token     = os.environ["PYNEXTSMS_TOKEN"],
        sender_id = os.environ.get("PYNEXTSMS_SENDER_ID", "YOURBRAND"),
    )
    try:
        resp = client.sms.send(
            to="255763930052",
            text="Hello from PyNextSMS!",
            reference="example_single",
        )
        print(f"✅ sent={resp.successful}  ref={resp.reference}  id={resp.message_id}")
    except ValidationError as e:
        print(f"❌ Bad input: {e}")
    except AuthenticationError:
        print("❌ Invalid token — check PYNEXTSMS_TOKEN.")
    except APIError as e:
        print(f"❌ API error (HTTP {e.status_code}): {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
