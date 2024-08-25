import os
import time
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from .request import github_api_request


def get_page_num(url):
    query_string = urlparse(url).query
    params = parse_qs(query_string)
    return params.get("page", [None])[0]


def fetch_paginated_github_api_request(initial_url, params=None):
    next_url = "first_page"
    results = []
    is_overflowed = False

    while True:
        if next_url == "first_page":
            response = github_api_request(
                "GET",
                initial_url,
                None,
                params=params,
            )
            last_url = response.links.get("last", {}).get("url")
            last_page_num = get_page_num(last_url)

            if last_page_num == 10:
                is_overflowed = True
        elif next_url is not None:
            response = github_api_request("GET", next_url, None)
        else:
            break

        if response.status_code == 200:
            result = response.json()
            if result:
                results.extend(result)
            next_url = response.links.get("next", {}).get("url")
        else:
            print(f"Failed to fetch {next_url}: {response.status_code}")
            print(response.links.get("next", {}).get("url"))
            break

    return results, response, is_overflowed


def fetch_github_accounts_by_date_location(location: str, date: str):
    print("date: ", date)
    base_url = "https://api.github.com/search/users?"
    total_users = []
    overflowed_date = []

    params = {
        "q": f"location:{location} created:{date}",
        "page": 1,
        "per_page": 100,
        "sort": "joined",
        "order": "desc",
    }

    results, response, is_overflowed = fetch_paginated_github_api_request(
        base_url, params
    )

    results = [result["items"] for result in results]

    if is_overflowed:
        overflowed_date.append(date)

    # Add fetched_date_range key and value for each user
    for user in results:
        user["fetched_date_range"] = date
    total_users.extend(results)

    reached_rate_limit = int(response.headers.get("X-RateLimit-Remaining")) < 1
    rate_limit_reset_time = int(response.headers.get("X-RateLimit-reset"))
    print("users: ", [user["login"] for user in total_users])
    return (
        total_users,
        overflowed_date,
        reached_rate_limit,
        rate_limit_reset_time,
    )


def fetch_commits(commit_url: str, params: dict):
    results, response, is_overflowed = fetch_paginated_github_api_request(
        commit_url, params
    )

    # Add fetched_date_range key and value for each user
    remaining_rate_limit = int(response.headers.get("X-RateLimit-Remaining"))
    reached_rate_limit = remaining_rate_limit < 1
    rate_limit_reset_time = int(response.headers.get("X-RateLimit-reset"))

    return (
        results,
        is_overflowed,
        reached_rate_limit,
        remaining_rate_limit,
        rate_limit_reset_time,
    )
