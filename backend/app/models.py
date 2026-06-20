from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

# Helper to serialize MongoDB object IDs
def serialize_doc(doc) -> dict:
    if not doc:
        return {}
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

def serialize_list(docs) -> list:
    return [serialize_doc(doc) for doc in docs]

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_gmail(cls, v: str) -> str:
        v = v.lower().strip()
        if not v.endswith("@gmail.com"):
            raise ValueError("Chỉ chấp nhận đăng ký tài khoản bằng định dạng Gmail (@gmail.com)")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
    has_hf_token: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Todo Schemas
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Tiêu đề công việc")
    description: Optional[str] = ""
    deadline: Optional[datetime] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # pending, in_progress, completed
    deadline: Optional[datetime] = None

class TodoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    status: str  # pending, in_progress, completed, overdue
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    reminded: bool

# Chat Schemas
class ChatMessageModel(BaseModel):
    sender: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageModel]
