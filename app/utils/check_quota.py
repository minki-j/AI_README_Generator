import time
from fasthtml.common import *
from app.global_vars import QUOTA_LIMIT, QUOTA_RESET_MINUTES


def check_quota(session):
    quota = session["quota"]
    quota_left = quota[0]
    quota_created_at = quota[1]
    current_time = int(time.time())

    if quota_left <= 0:
        remaining_time = round(
            (quota_created_at + QUOTA_RESET_MINUTES * 60 - time.time()) / 60, 2
        )
        if remaining_time <= 0:
            print("resetting quota")
            session["quota"] = (QUOTA_LIMIT, current_time)
            return None
        else:
            #! Not working because this doesn't return FT objects
            # add_toast(
            #     session,
            #     f"Please wait for {remaining_time} minutes to reset your quota",
            #     "info",
            # )
            print(f"Please wait for {remaining_time} minutes to reset your quota")
            return Response(
                to_xml(
                    P(
                        f"Please wait for {remaining_time} minutes to reset your quota",
                        id="quota_msg",
                    )
                ),
                status_code=429,
            )
    else:
        return None
