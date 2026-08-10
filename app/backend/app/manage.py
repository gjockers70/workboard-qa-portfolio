import argparse
import os
import sys

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import User
from .security import hash_password


def create_admin(email: str, display_name: str) -> int:
    password = os.environ.get("WORKBOARD_ADMIN_PASSWORD", "")
    if len(password) < 12:
        print("Set WORKBOARD_ADMIN_PASSWORD to at least 12 characters.", file=sys.stderr)
        return 2

    normalized_email = email.strip().lower()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == normalized_email))
        if user is None:
            user = User(
                email=normalized_email,
                display_name=display_name.strip(),
                password_hash=hash_password(password),
                role="admin",
            )
            db.add(user)
            action = "created"
        else:
            user.display_name = display_name.strip()
            user.password_hash = hash_password(password)
            user.role = "admin"
            action = "updated"
        db.commit()
    print(f"Administrator {action}: {normalized_email}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage local WorkBoard accounts")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser("create-admin")
    create_parser.add_argument("--email", required=True)
    create_parser.add_argument("--display-name", required=True)
    args = parser.parse_args()
    if args.command == "create-admin":
        return create_admin(args.email, args.display_name)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

