import os
import requests
import pendulum

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
        # print(f"==> 200 OK for {url}")
        pass
    elif response.status_code == 304:
        print(f"==> 304 Not Modified since the last fetch: {url}")
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
        print(
            f"{response.status_code} Error for {url} / Message: {response.text}"
        )
        pass

    return response
