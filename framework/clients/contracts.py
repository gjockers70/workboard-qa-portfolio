from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthContract(ContractModel):
    status: str


class UserContract(ContractModel):
    id: int
    email: str
    display_name: str
    role: str


class AuthContract(ContractModel):
    access_token: str
    token_type: str
    user: UserContract


class TaskContract(ContractModel):
    id: int
    title: str
    description: str
    completed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime


class AdminTaskContract(TaskContract):
    owner_email: str
    owner_name: str
