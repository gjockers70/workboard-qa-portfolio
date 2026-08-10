"""Load and cross-check the CSV registers used by the project."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


def split_ids(value: str) -> set[str]:
    """Return trimmed semicolon-delimited identifiers, excluding blanks."""

    return {part.strip() for part in value.split(";") if part.strip()}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(frozen=True)
class RegisterSet:
    """In-memory view of the case, cycle, execution, and traceability files."""

    cases: list[dict[str, str]]
    cycles: list[dict[str, str]]
    executions: list[dict[str, str]]
    traceability: list[dict[str, str]]

    @classmethod
    def load(cls, root: Path) -> "RegisterSet":
        register_dir = root / "test-management"
        return cls(
            cases=_read_csv(register_dir / "TEST_CASES.csv"),
            cycles=_read_csv(register_dir / "TEST_CYCLES.csv"),
            executions=_read_csv(register_dir / "TEST_EXECUTIONS.csv"),
            traceability=_read_csv(register_dir / "REQUIREMENTS_TRACEABILITY.csv"),
        )

    @staticmethod
    def unique_values(rows: list[dict[str, str]], column: str) -> set[str]:
        values = [row[column] for row in rows]
        if len(values) != len(set(values)):
            duplicates = sorted({value for value in values if values.count(value) > 1})
            raise AssertionError(f"Duplicate {column}: {duplicates}")
        return set(values)
