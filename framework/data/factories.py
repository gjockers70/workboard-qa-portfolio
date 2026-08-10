from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class SyntheticUser:
    display_name: str
    email: str
    password: str


def synthetic_user(label: str = "member") -> SyntheticUser:
    token = uuid4().hex[:10]
    return SyntheticUser(
        display_name=f"Phase 5 {label.title()} {token[:4]}",
        email=f"phase5.{label}.{token}@example.test",
        password=f"Synthetic-{token}!",
    )


def synthetic_task_title(label: str) -> str:
    return f"Phase 5 {label} {uuid4().hex[:8]}"
