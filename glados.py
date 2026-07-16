import json
import os
import sys
from urllib.parse import urlencode

import requests


CHECKIN_URL = "https://glados.rocks/api/user/checkin"
STATUS_URL = "https://glados.rocks/api/user/status"
REFERER = "https://glados.rocks/console/checkin"
ORIGIN = "https://glados.rocks"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
PAYLOAD = {"token": "glados.one"}


def split_cookies(raw_cookie):
    if not raw_cookie:
        return []
    return [cookie.strip() for cookie in raw_cookie.split("&") if cookie.strip()]


def build_headers(cookie):
    return {
        "cookie": cookie,
        "referer": REFERER,
        "origin": ORIGIN,
        "user-agent": USER_AGENT,
        "content-type": "application/json;charset=UTF-8",
    }


def checkin_account(cookie, session=requests, timeout=20):
    headers = build_headers(cookie)
    checkin = session.post(
        CHECKIN_URL,
        headers=headers,
        data=json.dumps(PAYLOAD),
        timeout=timeout,
    )
    checkin.raise_for_status()

    status = session.get(STATUS_URL, headers=headers, timeout=timeout)
    status.raise_for_status()

    checkin_data = checkin.json()
    status_data = status.json()
    account = status_data.get("data", {})

    email = account.get("email", "unknown account")
    left_days = str(account.get("leftDays", "unknown")).split(".")[0]
    message = checkin_data.get("message") or checkin_data.get("data") or checkin.text

    return f"{email} ---- {message} ---- remaining({left_days}) days"


def notify_pushplus(token, title, content, session=requests, timeout=20):
    if not token:
        return

    query = urlencode({"token": token, "title": title, "content": content})
    response = session.get(f"https://www.pushplus.plus/send?{query}", timeout=timeout)
    response.raise_for_status()


def run_checkins(raw_cookie, pushplus_token="", session=requests):
    cookies = split_cookies(raw_cookie)
    if not cookies:
        raise RuntimeError("GLADOS_COOKIE is missing. Add it as a GitHub Actions secret.")

    summaries = []
    failures = []
    for index, cookie in enumerate(cookies, start=1):
        try:
            summary = checkin_account(cookie, session=session)
            summaries.append(summary)
            print(summary)
        except Exception as exc:
            failures.append(f"account #{index}: {exc}")
            print(f"account #{index} failed: {exc}")

    if summaries:
        notify_pushplus(
            pushplus_token,
            "GLaDOS check-in result",
            "\n".join(summaries),
            session=session,
        )

    if failures:
        raise RuntimeError("; ".join(failures))

    return summaries


def main():
    try:
        run_checkins(
            os.environ.get("GLADOS_COOKIE", ""),
            os.environ.get("PUSHPLUS_TOKEN", ""),
        )
    except Exception as exc:
        print(f"Check-in failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
