from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .config import seeded_functional_defects_enabled
from .models import Task, User
from .schemas import (
    AdminTaskResponse,
    LoginRequest,
    ProfileUpdate,
    RegisterRequest,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TokenResponse,
    UserResponse,
)
from .security import create_access_token, decode_access_token, hash_password, verify_password


Base.metadata.create_all(bind=engine)

app = FastAPI(title="WorkBoard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DbSession = Annotated[Session, Depends(get_db)]


def current_user(
    db: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user_id = decode_access_token(authorization.removeprefix("Bearer ").strip())
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> TokenResponse:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = User(
        email=payload.email,
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id), user=UserResponse.model_validate(user))


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id), user=UserResponse.model_validate(user))


@app.get("/api/profile", response_model=UserResponse)
def profile(user: CurrentUser) -> User:
    return user


@app.patch("/api/profile", response_model=UserResponse)
def update_profile(payload: ProfileUpdate, user: CurrentUser, db: DbSession) -> User:
    if seeded_functional_defects_enabled():
        return user
    user.display_name = payload.display_name
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/tasks", response_model=list[TaskResponse])
def list_tasks(
    user: CurrentUser,
    db: DbSession,
    search: str = Query(default="", max_length=120),
    state: Literal["all", "active", "completed"] = "all",
) -> list[Task]:
    query = select(Task).where(Task.owner_id == user.id)
    if search.strip():
        pattern = f"%{search.strip()}%"
        query = query.where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
    ignore_state = seeded_functional_defects_enabled() and bool(search.strip())
    if state == "active" and not ignore_state:
        query = query.where(Task.completed.is_(False))
    elif state == "completed" and not ignore_state:
        query = query.where(Task.completed.is_(True))
    return list(db.scalars(query.order_by(Task.created_at.desc())).all())


@app.get("/api/admin/tasks", response_model=list[AdminTaskResponse])
def list_all_tasks(user: CurrentUser, db: DbSession) -> list[AdminTaskResponse]:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    tasks = db.scalars(select(Task).order_by(Task.created_at.desc())).all()
    return [
        AdminTaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            owner_id=task.owner_id,
            owner_email=task.owner.email,
            owner_name=task.owner.display_name,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, user: CurrentUser, db: DbSession) -> Task:
    task = Task(title=payload.title, description=payload.description.strip(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def owned_task(task_id: int, user: User, db: Session) -> Task:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == user.id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, user: CurrentUser, db: DbSession) -> Task:
    task = owned_task(task_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, user: CurrentUser, db: DbSession) -> None:
    task = owned_task(task_id, user, db)
    db.delete(task)
    db.commit()
