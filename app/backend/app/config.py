import os


def seeded_functional_defects_enabled() -> bool:
    return os.environ.get("WORKBOARD_SEEDED_FUNCTIONAL_DEFECTS", "false").lower() == "true"

