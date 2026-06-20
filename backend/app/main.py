from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId
from typing import List, Optional

from .config import settings
from .database import connect_to_mongo, close_mongo_connection, get_db
from .models import (
    UserRegister, UserLogin, UserResponse, Token, TodoCreate, TodoUpdate, TodoResponse,
    ChatMessageModel, ChatHistoryResponse, serialize_doc, serialize_list
)
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
from .scheduler import start_scheduler, shutdown_scheduler
from .agent.graph import agent_graph

app = FastAPI(title="To Do List AI Assistant", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL, 
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://[::1]:5173",
        "http://[::1]:3000"
    ],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and Shutdown Lifecycle Hooks
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    shutdown_scheduler()

@app.get("/")
def read_root():
    return {"message": "Welcome to To Do List AI API"}

# ==========================================
# AUTH ENDPOINTS
# ==========================================

@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user_in: UserRegister, db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản Gmail này đã được đăng ký trước đó."
        )
        
    hashed_password = get_password_hash(user_in.password)
    new_user = {
        "email": user_in.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(new_user)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return serialize_doc(created_user)

@app.post("/api/auth/login", response_model=Token)
async def login_user(user_in: UserLogin, db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    # Check user email
    user = await db.users.find_one({"email": user_in.email})
    if not user or not verify_password(user_in.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác."
        )
        
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
    user_doc = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    has_token = bool(user_doc.get("hf_token")) if user_doc else False
    return {
        **current_user,
        "has_hf_token": has_token
    }

class HFTokenPayload(BaseModel):
    hf_token: str

@app.put("/api/users/hf-token")
async def update_hf_token(payload: HFTokenPayload, current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
    
    token_val = payload.hf_token.strip()
    if not token_val:
        raise HTTPException(status_code=400, detail="Token không được để trống")
        
    await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"hf_token": token_val}}
    )
    return {"message": "Đã cập nhật Hugging Face Token thành công"}

@app.delete("/api/users/hf-token")
async def delete_hf_token(current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
    
    await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$unset": {"hf_token": ""}}
    )
    return {"message": "Đã xóa Hugging Face Token"}

class GoogleTokenPayload(BaseModel):
    token: str

@app.post("/api/auth/google-login", response_model=Token)
async def google_login(payload: GoogleTokenPayload, db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    google_token = payload.token
    
    # 1. Verify Google token using Google API Tokeninfo
    try:
        import httpx
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={google_token}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã xác thực Google ID Token không hợp lệ hoặc đã hết hạn"
                )
            google_info = response.json()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lỗi khi xác thực mã đăng nhập Google: {str(e)}"
        )
        
    email = google_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tìm thấy email từ mã Google trả về."
        )
        
    email = email.lower().strip()
    if not email.endswith("@gmail.com"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận tài khoản Gmail (@gmail.com)."
        )
        
    # 2. Check if user already exists. If not, auto register them
    user = await db.users.find_one({"email": email})
    if not user:
        new_user = {
            "email": email,
            "hashed_password": get_password_hash("google_signed_in_oauth_account"),
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
        user = await db.users.find_one({"email": email})
        print(f"[Google Auth] Registered new user from Google Sign-In: {email}")
    else:
        print(f"[Google Auth] Logged in existing user from Google Sign-In: {email}")
        
    # 3. Create app JWT access token
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


# ==========================================
# TODO ENDPOINTS (CRUD)
# ==========================================

@app.get("/api/todos", response_model=List[TodoResponse])
async def get_todos(current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    cursor = db.todos.find({"user_id": current_user["id"]}).sort("created_at", -1)
    todos = await cursor.to_list(length=100)
    
    # Proactively check for overdue items to update status dynamically
    now = datetime.utcnow()
    updated_todos = []
    for todo in todos:
        # If pending or in_progress and deadline is passed, it is overdue
        if todo["status"] in ["pending", "in_progress"] and todo.get("deadline") and todo["deadline"] < now:
            await db.todos.update_one(
                {"_id": todo["_id"]},
                {"$set": {"status": "overdue", "updated_at": now}}
            )
            todo["status"] = "overdue"
        updated_todos.append(serialize_doc(todo))
        
    return updated_todos

@app.post("/api/todos", response_model=TodoResponse)
async def create_todo(todo_in: TodoCreate, current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    # Strip timezone info if deadline has it, MongoDB stores in UTC
    deadline_utc = todo_in.deadline
    if deadline_utc:
        deadline_utc = deadline_utc.replace(tzinfo=None)
        
    new_todo = {
        "user_id": current_user["id"],
        "title": todo_in.title.strip(),
        "description": todo_in.description.strip() if todo_in.description else "",
        "status": "pending",
        "deadline": deadline_utc,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reminded": False
    }
    
    result = await db.todos.insert_one(new_todo)
    created_todo = await db.todos.find_one({"_id": result.inserted_id})
    return serialize_doc(created_todo)

@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, todo_in: TodoUpdate, current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    try:
        obj_id = ObjectId(todo_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Mã công việc không hợp lệ")
        
    todo = await db.todos.find_one({"_id": obj_id, "user_id": current_user["id"]})
    if not todo:
        raise HTTPException(status_code=404, detail="Không tìm thấy công việc")
        
    update_data = {}
    if todo_in.title is not None:
        update_data["title"] = todo_in.title.strip()
    if todo_in.description is not None:
        update_data["description"] = todo_in.description.strip()
    if todo_in.status is not None:
        if todo_in.status not in ["pending", "in_progress", "completed", "overdue"]:
            raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")
        update_data["status"] = todo_in.status
    if todo_in.deadline is not None:
        # If set to None, we clear it, otherwise store UTC datetime
        update_data["deadline"] = todo_in.deadline.replace(tzinfo=None) if todo_in.deadline else None
        # Reset reminded flag to send warning email again if deadline was updated
        update_data["reminded"] = False
        
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.todos.update_one({"_id": obj_id}, {"$set": update_data})
        
    updated_todo = await db.todos.find_one({"_id": obj_id})
    return serialize_doc(updated_todo)

@app.delete("/api/todos/{todo_id}")
async def delete_todo(todo_id: str, current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    try:
        obj_id = ObjectId(todo_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Mã công việc không hợp lệ")
        
    result = await db.todos.delete_one({"_id": obj_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy công việc cần xóa")
        
    return {"message": "Đã xóa công việc thành công"}

# ==========================================
# CHAT / AGENT ENDPOINTS
# ==========================================

class MessagePayload(BaseModel):
    message: str

@app.get("/api/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    # Get last 10 chat messages in chronological order
    cursor = db.chat_messages.find({"user_id": current_user["id"]}).sort("timestamp", -1).limit(10)
    messages = await cursor.to_list(length=10)
    # Reverse to make it oldest to newest
    messages.reverse()
    
    return {"messages": serialize_list(messages)}

@app.post("/api/chat")
async def send_chat_message(payload: MessagePayload, current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    user_id = current_user["id"]
    user_message = payload.message.strip()
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Nội dung chat không được trống")
        
    # 1. Save User Message to database
    await db.chat_messages.insert_one({
        "user_id": user_id,
        "sender": "user",
        "content": user_message,
        "timestamp": datetime.utcnow()
    })
    
    # 2. Retrieve last 10 chat messages for Agent history context
    cursor = db.chat_messages.find({"user_id": user_id}).sort("timestamp", -1).limit(10)
    history = await cursor.to_list(length=10)
    history.reverse()
    
    # Standard format for AgentState
    formatted_history = [
        {"sender": msg["sender"], "content": msg["content"]} for msg in history
    ]
    
    # 3. Retrieve user's hf_token
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    hf_token = user_doc.get("hf_token", "") if user_doc else ""
    
    # 4. Retrieve current active todos for Context injection
    todo_cursor = db.todos.find({"user_id": user_id}).sort("created_at", -1)
    raw_todos = await todo_cursor.to_list(length=100)
    todos = serialize_list(raw_todos)
    
    # 5. Invoke Agent Graph
    initial_state = {
        "messages": formatted_history,
        "user_id": user_id,
        "todos": todos,
        "tool_calls": [],
        "final_response": "",
        "should_refresh": False,
        "hf_token": hf_token
    }
    
    try:
        final_state = await agent_graph.ainvoke(initial_state)
        ai_response = final_state.get("final_response", "Xin lỗi, tôi đã gặp sự cố khi xử lý thông tin.")
        should_refresh = final_state.get("should_refresh", False)
    except Exception as e:
        print(f"[Chat API] Graph execution error: {e}")
        ai_response = f"Đã xảy ra lỗi trong quá trình xử lý câu hỏi: {str(e)}"
        should_refresh = False

    # 5. Save Agent Response to database
    await db.chat_messages.insert_one({
        "user_id": user_id,
        "sender": "assistant",
        "content": ai_response,
        "timestamp": datetime.utcnow()
    })
    
    return {
        "response": ai_response,
        "should_refresh": should_refresh
    }

@app.delete("/api/chat/history")
async def clear_chat_history(current_user = Depends(get_current_user), db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Cơ sở dữ liệu chưa sẵn sàng")
        
    await db.chat_messages.delete_many({"user_id": current_user["id"]})
    return {"message": "Đã xóa toàn bộ lịch sử trò chuyện"}
