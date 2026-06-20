# ToDoList with AI

A modern, full-stack task management application powered by intelligent AI assistant. Manage your tasks efficiently through natural language conversation using advanced AI-driven tools and automated scheduling.

## Overview

**ToDoList with AI** is a sophisticated task management system that combines a responsive React frontend with a powerful FastAPI backend. The application features an intelligent AI chatbot agent that leverages **LangGraph** and **LlamaIndex** to understand your tasks through natural conversation, execute actions intelligently, and manage your workload seamlessly.

### Key Highlights
- 🤖 **AI-Powered Chatbot**: Manage tasks through natural language conversations
- ⚡ **Token-Optimized**: Calls LLM only once per interaction, reducing costs and latency
- 🔄 **Intelligent Scheduling**: Automatically schedules tool execution chains without redundant LLM calls
- 🌐 **Full-Stack Application**: Modern React frontend with FastAPI backend
- 🗄️ **MongoDB Integration**: Persistent data storage with cloud and local options
- 🔐 **Secure Authentication**: User authentication and authorization with JWT tokens

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | React 19 + Vite |
| **Backend** | FastAPI |
| **Database** | MongoDB |
| **AI/ML** | LangGraph, LlamaIndex, Hugging Face |
| **Authentication** | JWT (Python-jose) |
| **API** | RESTful API with CORS support |
| **Scheduling** | APScheduler |
| **Async Processing** | Motor (async MongoDB driver) |

---

## Features

- ✅ **User Authentication**: Secure registration and login system
- ✅ **Task Management**: Create, read, update, and delete tasks
- ✅ **AI Chat Interface**: Interact with tasks using natural language
- ✅ **Intelligent Task Scheduling**: Automatically schedule and manage task execution
- ✅ **Multi-Tool Integration**: Leverage multiple AI tools for enhanced capabilities
- ✅ **Real-time Updates**: Live task status updates
- ✅ **Responsive Design**: Works seamlessly on desktop and mobile devices

---

## Project Structure

```
ToDoList/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Main FastAPI application entry point
│   │   ├── auth.py         # Authentication and JWT logic
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # MongoDB connection management
│   │   ├── models.py       # Pydantic models and serializers
│   │   ├── mail.py         # Email utilities
│   │   ├── scheduler.py    # Task scheduling with APScheduler
│   │   └── agent/          # AI Agent implementation
│   │       ├── __init__.py
│   │       ├── graph.py    # LangGraph agent workflow
│   │       ├── prompts.py  # Agent prompts and templates
│   │       └── tools.py    # Agent tools definition
│   ├── requirements.txt     # Python dependencies
│   └── .env               # Environment configuration (not in repo)
│
├── frontend/                # React + Vite frontend application
│   ├── src/
│   │   ├── main.jsx        # React entry point
│   │   ├── App.jsx         # Main application component
│   │   ├── App.css
│   │   ├── index.css
│   │   └── assets/         # Static assets
│   ├── public/             # Public assets
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── eslint.config.js    # ESLint configuration
│   ├── index.html          # HTML entry point
│   └── README.md           # Frontend documentation
│
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

---

## Installation & Setup

### Prerequisites

- **Node.js** 16+ and npm/yarn
- **Python** 3.9+
- **MongoDB** (local or MongoDB Atlas)
- **Git**

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   Create a `.env` file in the `backend` directory:
   ```env
   # MongoDB Configuration
   MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   # or for local MongoDB:
   # MONGODB_URL=mongodb://localhost:27017

   # JWT Configuration
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Frontend URL
   FRONTEND_URL=http://localhost:5173

   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000

   # LLM Configuration (if using external LLM)
   HUGGINGFACE_API_KEY=your_hf_api_key
   ```

6. **Run the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Backend will be available at: `http://localhost:8000`

### MongoDB Setup

#### Option 1: MongoDB Atlas (Cloud - Recommended)

1. Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) and create a free account
2. Create a new cluster (M0 Free tier recommended)
3. Set up database user credentials
4. Configure network access (allow from anywhere for development)
5. Copy the connection string and add it to your `.env` file

#### Option 2: Local MongoDB Installation

1. Download from [MongoDB Community Download](https://www.mongodb.com/try/download/community)
2. Install MongoDB following the official guide
3. For Windows, MongoDB runs as a service on port `27017`
4. Default connection string: `mongodb://localhost:27017`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API endpoint (if needed):**
   Update the API URL in your React components to match your backend URL

4. **Run the development server:**
   ```bash
   npm run dev
   ```
   Frontend will be available at: `http://localhost:5173`

5. **Build for production:**
   ```bash
   npm run build
   ```

---

## Running the Application

1. **Start MongoDB** (if using local installation)
   ```bash
   # Windows: MongoDB runs as a service automatically
   # macOS/Linux:
   mongod
   ```

2. **Start Backend** (in `backend` directory):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start Frontend** (in `frontend` directory):
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs` (Swagger UI)

---

## API Endpoints

The backend provides the following main endpoints:

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive JWT token
- `POST /auth/logout` - Logout

### Tasks
- `GET /tasks` - Get all tasks for the current user
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get task details
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

### Chat
- `POST /chat/message` - Send a message to the AI assistant
- `GET /chat/history` - Get chat history

For complete API documentation, visit: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb+srv://...` |
| `SECRET_KEY` | JWT secret key | `your_secret_key` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `API_HOST` | Backend API host | `0.0.0.0` |
| `API_PORT` | Backend API port | `8000` |
| `HUGGINGFACE_API_KEY` | Hugging Face API key (optional) | Your API key |

---

## Development

### Backend Development

- API documentation available at `http://localhost:8000/docs` (Swagger UI)
- Use FastAPI's automatic validation and documentation
- All endpoints are CORS-enabled for frontend integration

### Frontend Development

- Hot module replacement enabled with Vite
- ESLint configuration for code quality
- React 19 with modern hooks and features

### Code Style

- Backend: Follow PEP 8 conventions
- Frontend: Use ESLint configuration provided

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support & Contact

For questions, issues, or suggestions, please open an issue on GitHub or contact the project maintainers.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - JavaScript library for building user interfaces
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- [LangGraph](https://python.langchain.com/docs/langgraph/) - Orchestration library
- [LlamaIndex](https://www.llamaindex.ai/) - Data framework for LLM applications 

### A. Cấu hình Backend (FastAPI)

1. Di chuyển vào thư mục `backend`:
   ```bash
   cd backend
   ```
2. Tạo môi trường ảo Python và kích hoạt:
   - **Command Prompt (cmd):**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```
   - **PowerShell:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
3. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
4. Cấu hình các biến môi trường trong file `.env`:
   - `MONGODB_URL`: Điền link MongoDB Atlas hoặc giữ nguyên localhost.
   - `HF_TOKEN`: Truy cập [Hugging Face Tokens](https://huggingface.co/settings/tokens), đăng ký tài khoản miễn phí và tạo một token có quyền `Read` rồi dán vào đây. (Nếu không cấu hình, chatbot sẽ tự động chuyển sang chế độ fallback ngoại tuyến để bạn vẫn test được chức năng).
   - **Gửi Email nhắc nhở (SMTP):** Để hệ thống gửi mail cảnh báo deadline tự động, hãy đăng nhập tài khoản Gmail của bạn, bật bảo mật 2 lớp và tạo một [Mật khẩu ứng dụng (App Password)](https://myaccount.google.com/apppasswords). Điền email vào `SMTP_EMAIL` và mật khẩu ứng dụng (16 ký tự viết liền) vào `SMTP_PASSWORD`.
   - **Xác thực Đăng nhập Google (Google Client ID):** 
     - Truy cập [Google Cloud Console](https://console.cloud.google.com/).
     - Tạo một dự án mới (Project).
     - Vào menu **APIs & Services** -> **OAuth consent screen**. Cấu hình chế độ **External**, điền thông tin mô tả ứng dụng rồi Lưu. (Nhớ thêm tài khoản Gmail thử nghiệm của bạn vào mục **Test users**).
     - Vào menu **Credentials** -> Nhấp **Create Credentials** -> Chọn **OAuth client ID**.
     - Chọn Application type là **Web application**.
     - Ở mục **Authorized JavaScript origins**, thêm địa chỉ của frontend: `http://localhost:5173`.
     - Ở mục **Authorized redirect URIs**, thêm: `http://localhost:5173`.
     - Bấm **Create** và sao chép mã **Client ID** được tạo.
     - Dán Client ID này vào biến `GOOGLE_CLIENT_ID` trong file `backend/.env`.


5. Khởi chạy FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
   API sẽ chạy tại địa chỉ: `http://localhost:8000`

---

### B. Cấu hình Frontend (React Vite)

1. Di chuyển vào thư mục `frontend`:
   ```bash
   cd ../frontend
   ```
2. Cài đặt thư viện node modules:
   ```bash
   npm install
   ```
3. Cấu hình Google Client ID:
   Mở file `frontend/.env` và điền mã Google Client ID đã tạo ở trên vào biến `VITE_GOOGLE_CLIENT_ID`:
   `VITE_GOOGLE_CLIENT_ID=your_google_client_id_here`
4. Khởi chạy máy chủ frontend:
   ```bash
   npm run dev
   ```
   Giao diện người dùng sẽ chạy tại địa chỉ: `http://localhost:5173`

---

## 3. Các Tính Năng Đang Hoạt Động

1. **Authentication (Google Sign-In):** Đăng nhập bảo mật thông qua nút **"Sign in with Google"** chính thức. Hệ thống tự động kiểm tra định dạng tài khoản Gmail và đồng bộ thông tin lưu trong cơ sở dữ liệu MongoDB.
2. **Dashboard Todo list:** Giao diện modern dark glassmorphism tuyệt đẹp, phân loại công việc theo trạng thái: Pending, In Progress, Completed, Overdue.
3. **Thao tác công việc (CRUD):** Tạo mới, chỉnh sửa thông tin, đổi trạng thái và xóa công việc trực tiếp trên UI.
4. **Trợ lý ảo AI Chatbot (LangGraph + LlamaIndex):**
   - Chatbot ghi nhớ tối đa 10 tin nhắn gần nhất.
   - Bạn có thể ra lệnh bằng tiếng Việt tự nhiên:
     - *"Tạo công việc Học React vào ngày mai"*
     - *"Đánh dấu hoàn thành công việc Mua sữa"*
     - *"Hôm nay tôi có những công việc nào trễ hạn không?"*
     - *"Xóa công việc Đi bộ"*
   - Đồ thị LangGraph gọi LLM chính xác 1 lần, sau đó định tuyến trực tiếp đến `ActionTool` (để sửa DB) hoặc `InforTool` (để trả lời) rồi kết thúc, tiết kiệm tối đa token.
   - Sau khi chatbot thực hiện hành động, UI Todo list sẽ tự động làm mới ngay lập tức mà không cần tải lại trang.
5. **Gửi Email Cảnh Báo Deadline:**
   - Hệ thống quét cơ sở dữ liệu mỗi phút 1 lần.
   - Bất kỳ công việc nào có deadline còn dưới 24 giờ mà chưa hoàn thành sẽ tự động kích hoạt tính năng gửi mail cảnh báo đến địa chỉ Gmail của người dùng.
