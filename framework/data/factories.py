from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class SyntheticUser:
    display_name: str
    email: str
    password: str


def synthetic_user(label: str = "member", phase: str = "phase5") -> SyntheticUser:
    token = uuid4().hex[:10]
    return SyntheticUser(
        display_name=f"{phase.title()} {label.title()} {token[:4]}",
        email=f"{phase.lower()}.{label}.{token}@example.test",
        password=f"Synthetic-{token}!",
    )


def synthetic_task_title(label: str, phase: str = "phase5") -> str:
    return f"{phase.title()} {label} {uuid4().hex[:8]}"
