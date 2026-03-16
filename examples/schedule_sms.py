"""Example: Schedule a recurring daily SMS.  Run: python examples/schedule_sms.py"""
import os
from datetime import date, time
from pynextsms import SMSClient, ScheduleOptions, RepeatInterval

def main():
    with SMSClient(
        token=os.environ["PYNEXTSMS_TOKEN"],
        sender_id=os.environ.get("PYNEXTSMS_SENDER_ID", "YOURBRAND"),
    ) as client:
        opts = ScheduleOptions(
            send_date  = date(2025, 6, 1),
            send_time  = time(8, 0),
            repeat     = RepeatInterval.DAILY,
            start_date = date(2025, 6, 1),
            end_date   = date(2025, 6, 30),
        )
        resp = client.sms.schedule(
            to="255763930052",
            text="Good morning! Remember to check your dashboard.",
            options=opts,
        )
        print(f"✅ scheduled={resp.successful}  ref={resp.reference}")

if __name__ == "__main__":
    main()
