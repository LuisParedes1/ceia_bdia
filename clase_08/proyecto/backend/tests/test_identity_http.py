"""Run against the isolated Compose API with TEST_API_URL and MAILPIT_URL set."""

# pyright: reportMissingImports=false

import json
import os
import re
import unittest

import psycopg

from app.security.password import hash_password
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


BASE_URL = os.getenv("TEST_API_URL", "")
MAILPIT_URL = os.getenv("MAILPIT_URL", "")
WEB_ORIGIN = os.getenv("TEST_WEB_ORIGIN", "http://localhost:5173")


@unittest.skipUnless(BASE_URL and MAILPIT_URL, "set TEST_API_URL and MAILPIT_URL for identity HTTP probes")
class IdentityHttpTests(unittest.TestCase):
    def request(self, path: str, payload: dict | None = None, headers: dict | None = None, method: str | None = None) -> tuple[int, dict, dict]:
        request = Request(f"{BASE_URL}{path}", headers=headers or {}, method=method or ("POST" if payload is not None else "GET"))
        if payload is not None:
            request.data = json.dumps(payload).encode()
            request.add_header("Content-Type", "application/json")
        try:
            with urlopen(request, timeout=10) as response:
                headers_out = dict(response.headers)
                headers_out["Set-Cookie"] = ", ".join(response.headers.get_all("Set-Cookie", []))
                return response.status, headers_out, json.loads(response.read())
        except HTTPError as error:
            return error.code, dict(error.headers), json.loads(error.read())

    @staticmethod
    def cookies(headers: dict) -> tuple[str, str]:
        values = headers.get("Set-Cookie", "").split(", ")
        return tuple(re.search(r"(?:session_token|csrf_token)=([^;]+)", value).group(1) for value in values)  # type: ignore[return-value]

    def csrf_headers(self, session: str, csrf: str) -> dict[str, str]:
        return {"Origin": WEB_ORIGIN, "Cookie": f"session_token={session}; csrf_token={csrf}", "X-CSRF-Token": csrf}

    def test_seeded_stack_new_admin_can_create_viewer(self) -> None:
        email = f"seed-regression-owner-{uuid4()}@example.com"
        status, headers, registered = self.request(
            "/api/auth/register",
            {"email": email, "password": "correct-horse", "tenant_name": "Seed Regression Lab"},
        )
        self.assertEqual((status, registered["role"]), (201, "admin"))
        session, csrf = self.cookies(headers)
        session_status = self.request("/api/auth/session", headers={"Cookie": f"session_token={session}"})
        self.assertEqual((session_status[0], session_status[2]["capabilities"]), (200, ["members:manage"]))
        viewer_email = f"seed-regression-viewer-{uuid4()}@example.com"
        created = self.request(
            "/api/members",
            {"email": viewer_email, "role": "viewer"},
            self.csrf_headers(session, csrf),
        )
        self.assertEqual((created[0], created[2]["role"]), (201, "viewer"))

    def test_invalid_email_payloads_return_422_without_identity_side_effects(self) -> None:
        invalid_email = "not-an-email"
        with urlopen(f"{MAILPIT_URL}/api/v1/messages", timeout=10) as response:
            mail_count = len(json.loads(response.read())["messages"])

        for path, payload in (
            ("/api/auth/register", {"email": invalid_email, "password": "correct-horse", "tenant_name": "Test Lab"}),
            ("/api/auth/login", {"email": invalid_email, "password": "correct-horse"}),
            ("/api/auth/recovery/request", {"email": invalid_email}),
            ("/api/members", {"email": invalid_email, "role": "viewer"}),
        ):
            with self.subTest(path=path):
                status, headers, _ = self.request(path, payload)
                self.assertEqual(status, 422)
                self.assertNotIn("session_token=", headers.get("Set-Cookie", ""))

        with urlopen(f"{MAILPIT_URL}/api/v1/messages", timeout=10) as response:
            self.assertEqual(len(json.loads(response.read())["messages"]), mail_count)

    def test_registration_login_recovery_and_roles(self) -> None:
        email = f"owner-{uuid4()}@example.com"
        status, headers, registered = self.request("/api/auth/register", {"email": email, "password": "correct-horse", "tenant_name": "Test Lab"})
        self.assertEqual(status, 201)
        self.assertEqual(registered["role"], "admin")
        session, csrf = self.cookies(headers)
        tenant = registered["tenant_id"]
        self.assertEqual(self.request("/api/tenants/select", {"tenant_id": tenant}, self.csrf_headers(session, csrf))[0], 404)
        session_status = self.request("/api/auth/session", headers={"Cookie": f"session_token={session}"})
        self.assertEqual(session_status[0], 200)
        self.assertEqual(session_status[2], {"user_id": registered["user_id"], "tenant_id": tenant, "tenant_name": "Test Lab", "role": "admin", "capabilities": ["members:manage"]})
        viewer_email = f"viewer-{uuid4()}@example.com"
        self.assertEqual(self.request("/api/members")[0], 401)
        self.assertEqual(self.request("/api/members", {"email": viewer_email, "role": "viewer"}, self.csrf_headers(session, csrf))[0], 201)
        listed = self.request("/api/members?page=1&per_page=10&sort=email:asc", headers={"Cookie": f"session_token={session}"})
        self.assertEqual(listed[0], 200)
        self.assertEqual(set(listed[2]), {"items", "total", "page", "per_page", "pages"})
        self.assertEqual((listed[2]["total"], listed[2]["page"], listed[2]["per_page"], listed[2]["pages"]), (2, 1, 10, 1))
        self.assertEqual([item["email"] for item in listed[2]["items"]], sorted((email, viewer_email)))
        self.assertTrue(any(item["user_id"] == registered["user_id"] and item["role"] == "admin" for item in listed[2]["items"]))
        self.assertTrue(any(item["email"] == viewer_email and item["status"] == "active" and item["password_setup_required"] for item in listed[2]["items"]))
        self.assertEqual(self.request(f"/api/members?search={viewer_email.upper()}", headers={"Cookie": f"session_token={session}"})[2]["total"], 1)
        self.assertEqual(self.request("/api/members?search=no-match", headers={"Cookie": f"session_token={session}"})[2], {"items": [], "total": 0, "page": 1, "per_page": 10, "pages": 0})
        self.assertEqual(self.request("/api/members?role=viewer", headers={"Cookie": f"session_token={session}"})[2]["total"], 1)
        self.assertEqual(self.request("/api/members?status=active", headers={"Cookie": f"session_token={session}"})[2]["total"], 2)
        for sort in ("email:asc", "email:desc", "role:asc", "role:desc", "status:asc", "status:desc", "created_at:asc", "created_at:desc"):
            with self.subTest(sort=sort):
                self.assertEqual(self.request(f"/api/members?sort={sort}", headers={"Cookie": f"session_token={session}"})[0], 200)
        for query in ("page=0", "per_page=11", "role=owner", "status=pending", "sort=email;DROP%20TABLE%20users", f"tenant_id={uuid4()}"):
            with self.subTest(query=query):
                denied = self.request(f"/api/members?{query}", headers={"Cookie": f"session_token={session}"})
                self.assertEqual(denied[0], 422)
                self.assertIn("Los datos enviados no son válidos.", str(denied[2]))
        created = self.request("/api/experiments", {"name": "Model comparison"}, self.csrf_headers(session, csrf))
        self.assertEqual((created[0], created[2]["status"]), (201, "draft"))
        experiment_id = created[2]["id"]
        running = self.request(f"/api/experiments/{experiment_id}", {"status": "running"}, self.csrf_headers(session, csrf), "PATCH")
        self.assertEqual((running[0], running[2]["status"]), (200, "running"))
        result = self.request(f"/api/experiments/{experiment_id}/results", {"status": "completed", "input_summary": "dataset v1", "output_summary": "trained", "metrics": [{"name": "accuracy", "type": "number", "value": 0.91, "unit": "%", "step": 1}]}, self.csrf_headers(session, csrf))
        self.assertEqual((result[0], result[2]["metrics"][0]["value_type"]), (201, "number"))
        self.assertEqual(self.request(f"/api/experiments/{experiment_id}", {"status": "completed"}, self.csrf_headers(session, csrf), "PATCH")[0], 200)
        self.assertEqual(self.request(f"/api/experiments/{experiment_id}", {"status": "running"}, self.csrf_headers(session, csrf), "PATCH")[0], 409)
        self.assertEqual(self.request(f"/api/experiments/{experiment_id}/results/{result[2]['id']}", {"output_summary": "edited"}, self.csrf_headers(session, csrf), "PATCH")[0], 404)

        login_status, login_headers, _ = self.request("/api/auth/login", {"email": email, "password": "correct-horse"})
        self.assertEqual(login_status, 200)
        login_session, _ = self.cookies(login_headers)
        self.assertEqual(self.request("/api/auth/session", headers={"Cookie": f"session_token={login_session}"})[2]["tenant_id"], tenant)

        known = self.request("/api/auth/recovery/request", {"email": email})
        unknown = self.request("/api/auth/recovery/request", {"email": f"unknown-{uuid4()}@example.com"})
        self.assertEqual((known[0], known[2]), (202, {"message": "Si la cuenta existe, se enviaron las instrucciones de recuperación."}))
        self.assertEqual((known[0], known[2]), (unknown[0], unknown[2]))
        with urlopen(f"{MAILPIT_URL}/api/v1/messages", timeout=10) as response:
            match = re.search(r"token=([A-Za-z0-9_-]+)", json.loads(response.read())["messages"][0]["Snippet"])
        self.assertIsNotNone(match)
        token = match.group(1) if match else ""
        self.assertEqual(self.request("/api/auth/recovery/confirm", {"token": token, "password": "updated-password"})[0], 200)
        self.assertEqual(self.request("/api/auth/recovery/confirm", {"token": token, "password": "another-password"})[0], 400)
        self.assertEqual(self.request("/api/auth/recovery/confirm", {"token": "expired-or-forged", "password": "another-password"})[0], 400)

        self.assertEqual(self.request("/api/auth/recovery/request", {"email": viewer_email})[0], 202)
        with urlopen(f"{MAILPIT_URL}/api/v1/messages", timeout=10) as response:
            match = re.search(r"token=([A-Za-z0-9_-]+)", json.loads(response.read())["messages"][0]["Snippet"])
        viewer_token = match.group(1) if match else ""
        self.assertTrue(viewer_token)
        self.assertEqual(self.request("/api/auth/recovery/confirm", {"token": viewer_token, "password": "viewer-password"})[0], 200)
        _, viewer_headers, _ = self.request("/api/auth/login", {"email": viewer_email, "password": "viewer-password"})
        viewer_session, viewer_csrf = self.cookies(viewer_headers)
        viewer_status = self.request("/api/auth/session", headers={"Cookie": f"session_token={viewer_session}"})
        self.assertEqual(viewer_status[2]["role"], "viewer")
        self.assertEqual(viewer_status[2]["capabilities"], [])
        denied_email = f"denied-{uuid4()}@example.com"
        self.assertEqual(self.request("/api/members", headers={"Cookie": f"session_token={viewer_session}"})[0], 403)
        self.assertEqual(self.request("/api/members", {"email": denied_email, "role": "member"}, self.csrf_headers(viewer_session, viewer_csrf))[0], 403)
        self.assertEqual(self.request(f"/api/experiments/{experiment_id}", headers={"Cookie": f"session_token={viewer_session}"})[0], 200)
        self.assertEqual(self.request("/api/experiments", {"name": "denied"}, self.csrf_headers(viewer_session, viewer_csrf))[0], 403)
        with urlopen(f"{MAILPIT_URL}/api/v1/messages", timeout=10) as response:
            before = len(json.loads(response.read())["messages"])
        self.assertEqual(self.request("/api/auth/recovery/request", {"email": denied_email})[0], 202)
        with urlopen(f"{MAILPIT_URL}/api/v1/messages", timeout=10) as response:
            self.assertEqual(len(json.loads(response.read())["messages"]), before)
        self.assertEqual(self.request("/api/invitations")[0], 404)

        other_email = f"owner-{uuid4()}@example.com"
        _, other_headers, _ = self.request("/api/auth/register", {"email": other_email, "password": "correct-horse", "tenant_name": "Other Lab"})
        other_session, other_csrf = self.cookies(other_headers)
        if other_session:
            isolated = self.request("/api/members", headers={"Cookie": f"session_token={other_session}"})
            self.assertEqual((isolated[0], isolated[2]["total"]), (200, 1))
            self.assertNotIn(email, [item["email"] for item in isolated[2]["items"]])
            self.assertEqual(self.request(f"/api/experiments/{experiment_id}", headers={"Cookie": f"session_token={other_session}"})[0], 404)
            self.assertEqual(self.request("/api/members", {"email": viewer_email, "role": "member"}, self.csrf_headers(other_session, other_csrf))[0], 409)

            unassigned_email = f"unassigned-{uuid4()}@example.com"
            database_url = os.environ["TEST_DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://", 1)
            with psycopg.connect(database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO users (id,email,password_hash) VALUES (%s,%s,%s)", (str(uuid4()), unassigned_email, hash_password("correct-horse")))
            self.assertEqual(self.request("/api/auth/login", {"email": unassigned_email, "password": "correct-horse"})[0], 403)


if __name__ == "__main__":
    unittest.main()
