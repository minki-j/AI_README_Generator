import os
import time
import requests
from psycopg2 import sql
import pendulum
from datetime import datetime, timedelta
import concurrent.futures


class HTTPError(Exception):
    pass


def process_user(id_and_url):
    _, url = id_and_url
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Github token is not set")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    rate_limit = int(response.headers["X-RateLimit-Remaining"])
    reset_time = int(response.headers["X-RateLimit-Reset"])

    if response.status_code == 200:
        user_info = response.json()
        return (id_and_url, user_info, rate_limit, reset_time)
    elif response.status_code == 403:
        print(f"Forbidden Error fetching user info: {url}")
        raise HTTPError(f"HTTP 403 Error fetching user info: {url}")
    elif response.status_code == 404:
        print(f"Resource not found Error fetching user info: {url}")
        return (id_and_url, {}, rate_limit, reset_time)
    else:
        print(f"Failed to fetch user info: {response.status_code}")
        return (id_and_url, {}, rate_limit, reset_time)


def filter_users_in_parallel(account_id_and_urls) -> dict[str, list]:
    users = []
    executor = concurrent.futures.ThreadPoolExecutor()

    try:
        future_to_user = {
            executor.submit(process_user, id_and_url): id_and_url
            for id_and_url in account_id_and_urls
        }
        for future in concurrent.futures.as_completed(future_to_user):
            id_and_url, user, rate_limit, reset_time = future.result()
            if user:
                users.append(user)
            else:
                user = {
                    "id": id_and_url[0],
                    "url": id_and_url[1],
                }
                users.append(user)

            if rate_limit < 1:
                print("Rate limit exceeded.")
                raise Exception("Rate limit exceeded")
            
            if len(users) % 100 == 0:
                print(f"Processed {len(users)} users.")
            
            # if len(users) >= 10:
            #     print("DEBUG MODE: quit after 10 users are collected.")
            #     break

    except Exception as e:
        print("Error in concurrent executor: ", e)
        executor.shutdown(wait=True, cancel_futures=True)


    is_finished = len(users) == len(account_id_and_urls)

    return users, is_finished, reset_time
