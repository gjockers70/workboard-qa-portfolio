from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse


DEFAULT_BASE_URL = "http://127.0.0.1:8010"
DEFAULT_USERS = 10
DEFAULT_SPAWN_RATE = 2
DEFAULT_RUN_TIME = "30s"
READ_REQUEST_NAMES = (
    "GET /api/profile",
    "GET /api/tasks",
    "GET /api/tasks?search&state",
)


@dataclass(frozen=True)
class PerformanceThresholds:
    p95_ms: float = 500.0
    error_rate_percent: float = 1.0
    concurrent_users: int = 10


THRESHOLDS = PerformanceThresholds()


class LocustEnvironment(Protocol):
    host: str
    process_exit_code: int | None


def validate_local_base_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "http":
        raise ValueError("The performance target must use local HTTP.")
    if parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("The performance target must be a loopback host.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("The performance target must not include credentials, a query, or a fragment.")
    if parsed.path not in {"", "/"}:
        raise ValueError("The performance target must not include an application path.")
    if parsed.port is None:
        raise ValueError("The performance target must include an explicit port.")
    return f"http://{parsed.hostname}:{parsed.port}"


def terminate_if_target_is_not_local(environment: LocustEnvironment) -> None:
    try:
        validate_local_base_url(environment.host)
    except ValueError as error:
        environment.process_exit_code = 2
        raise SystemExit(str(error)) from error
