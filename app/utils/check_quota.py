import os
import time
from fasthtml.common import *

from app.utils.error_responses import error_modal
def check_quota(session):
    quota = session["quota"]
    quota_left = quota[0]
    quota_created_at = quota[1]
    current_time = int(time.time())

    if int(quota_left) <= 0:
        remaining_time = round(
            (quota_created_at + int(os.getenv("QUOTA_RESET_MINUTES")) * 60 - time.time()) / 60, 2
        )
        if remaining_time <= 0:
            print("resetting quota")
            session["quota"] = (int(os.getenv("QUOTA_LIMIT")), current_time)
            return None
        else:
            print(f"Please wait for {remaining_time} minutes to reset your quota")
            return error_modal(f"Please wait for {remaining_time} minutes to reset your quota", 429)
    else:
        return None
