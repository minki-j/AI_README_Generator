import time
from fasthtml.common import *
from app.global_vars import QUOTA_LIMIT, QUOTA_RESET_MINUTES

def check_quota(session):
    quota_left = session.get("quota", (0, 0))[0]
    current_time = int(time.time())
    quota_created_at = session.get("quota", (0, current_time))[1]

    if quota_left <= 0:
        remaining_time = quota_created_at + QUOTA_RESET_MINUTES * 60 - current_time
        if remaining_time <= 0:
            session["quota"] = (QUOTA_LIMIT, current_time)
            add_toast(
                session,
                "Your quota has been reset.",
                "info",
            )
            return None
        else:
            add_toast(
                session,
                f"Please wait for {remaining_time/60} minutes to reset your quota",
                "info",
            )

            return Response(
                to_xml(
                    P(
                        f"Please wait for {remaining_time/60} minutes to reset your quota"
                    )
                ),
                status_code=429,
            )
    else:
        return None
