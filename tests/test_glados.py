import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import glados


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.posts = []
        self.gets = []

    def post(self, url, headers=None, data=None, timeout=None):
        self.posts.append(
            {"url": url, "headers": headers, "data": data, "timeout": timeout}
        )
        return FakeResponse({"message": "Checkin successful"})

    def get(self, url, headers=None, timeout=None):
        self.gets.append({"url": url, "headers": headers, "timeout": timeout})
        return FakeResponse(
            {"data": {"leftDays": "123.45", "email": "user@example.com"}}
        )


class GladosCheckinTests(unittest.TestCase):
    def test_split_cookies_removes_empty_chunks(self):
        self.assertEqual(glados.split_cookies("cookie-a&& cookie-b &"), ["cookie-a", "cookie-b"])

    def test_checkin_account_posts_payload_and_returns_summary(self):
        session = FakeSession()

        summary = glados.checkin_account("cookie=value", session=session)

        self.assertEqual(
            session.posts[0]["url"], "https://glados.rocks/api/user/checkin"
        )
        self.assertEqual(json.loads(session.posts[0]["data"]), {"token": "glados.one"})
        self.assertEqual(session.posts[0]["headers"]["cookie"], "cookie=value")
        self.assertIn("user@example.com", summary)
        self.assertIn("Checkin successful", summary)
        self.assertIn("123", summary)

    def test_workflow_uses_secret_instead_of_literal_cookie(self):
        workflow = Path(".github/workflows/runGladosAction.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("${{ secrets.GLADOS_COOKIE }}", workflow)
        self.assertNotIn("koa:sess=", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("schedule:", workflow)


if __name__ == "__main__":
    unittest.main()
