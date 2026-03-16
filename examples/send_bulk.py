"""Example: Personalised bulk send.  Run: python examples/send_bulk.py"""
import os
from pynextsms import SMSClient, MessageRecipient

def main():
    with SMSClient(
        token=os.environ["PYNEXTSMS_TOKEN"],
        sender_id=os.environ.get("PYNEXTSMS_SENDER_ID", "YOURBRAND"),
    ) as client:
        resp = client.sms.send_bulk([
            MessageRecipient("255763930052", "Hello Daniel, welcome!"),
            MessageRecipient("255627350020", "Hello Patricia, welcome!"),
            MessageRecipient("255622999999", "Hello Precious, welcome!"),
        ], reference="onboarding_batch")
        print(f"✅ successful={resp.successful}  total={resp.total}  ref={resp.reference}")

if __name__ == "__main__":
    main()
