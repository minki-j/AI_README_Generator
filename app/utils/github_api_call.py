import os
import requests
import pendulum
from urllib.parse import urlparse, parse_qs


def github_api_request(type, url, last_fetch_at, params=None):

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Github token is not set")

    headers = {"Authorization": f"Bearer {token}"}

    if last_fetch_at:
        headers["if-modified-since"] = last_fetch_at.strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

    if type == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif type == "POST":
        response = requests.post(url, headers=headers, json=params)
    elif type == "PATCH":
        response = requests.patch(url, headers=headers, json=params)
    elif type == "PUT":
        response = requests.put(url, headers=headers, json=params)
    elif type == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported type: {type}")

    if response.status_code == 200:
        # print(f">>> 200 OK for {url}")
        pass
    elif response.status_code == 304:
        print(f">>> 304 Not Modified since the last fetch: {url}")
        pass
    elif response.status_code == 403:
        print(f"403 Forbidden Error for {url} / Message: {response.text}")
        print(
            f"remaining rate limit: {response.headers['X-RateLimit-Remaining']} reset: {pendulum.from_timestamp(int(response.headers['X-RateLimit-Reset'])).in_tz('America/Montreal')}"
        )
        pass
    elif response.status_code == 404:
        print(f"Not Found:{url}")
        pass
    else:
        print(f"{response.status_code} Error for {url} / Message: {response.text}")
        pass

    return response


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
