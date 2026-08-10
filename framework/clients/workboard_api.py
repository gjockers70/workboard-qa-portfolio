from collections.abc import Mapping
from typing import Any

import httpx


class ApiResponseError(RuntimeError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"WorkBoard API returned {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class WorkBoardApi:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        *,
        timeout_seconds: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "WorkBoardApi":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    @staticmethod
    def authorization(token: str | None) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"} if token else {}

    @staticmethod
    def require_success(response: httpx.Response) -> httpx.Response:
        if response.is_success:
            return response
        try:
            body = response.json()
            detail_value = body.get("detail", "Request failed") if isinstance(body, dict) else "Request failed"
            detail = detail_value if isinstance(detail_value, str) else "Request validation failed"
        except ValueError:
            detail = response.text or "Request failed"
        raise ApiResponseError(response.status_code, detail)

    def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        return self._client.request(
            method,
            path,
            headers=self.authorization(token),
            json=json,
            params=params,
        )

    def health(self) -> httpx.Response:
        return self.request("GET", "/health")

    def register(self, email: str, display_name: str, password: str) -> httpx.Response:
        return self.request(
            "POST",
            "/api/auth/register",
            json={"email": email, "display_name": display_name, "password": password},
        )

    def login(self, email: str, password: str) -> httpx.Response:
        return self.request("POST", "/api/auth/login", json={"email": email, "password": password})

    def profile(self, token: str | None) -> httpx.Response:
        return self.request("GET", "/api/profile", token=token)

    def update_profile(self, token: str, display_name: Any) -> httpx.Response:
        return self.request("PATCH", "/api/profile", token=token, json={"display_name": display_name})

    def tasks(
        self,
        token: str | None,
        *,
        search: Any = "",
        state: Any = "all",
    ) -> httpx.Response:
        return self.request(
            "GET",
            "/api/tasks",
            token=token,
            params={"search": search, "state": state},
        )

    def all_tasks(self, token: str | None) -> httpx.Response:
        return self.request("GET", "/api/admin/tasks", token=token)

    def create_task(self, token: str | None, title: Any = None, description: Any = "") -> httpx.Response:
        payload: dict[str, Any] = {"description": description}
        if title is not None:
            payload["title"] = title
        return self.request("POST", "/api/tasks", token=token, json=payload)

    def update_task(self, token: str | None, task_id: int, **changes: Any) -> httpx.Response:
        return self.request("PATCH", f"/api/tasks/{task_id}", token=token, json=changes)

    def delete_task(self, token: str | None, task_id: int) -> httpx.Response:
        return self.request("DELETE", f"/api/tasks/{task_id}", token=token)
