from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bson import ObjectId

from .database import get_db
from .mail import send_deadline_email

scheduler = AsyncIOScheduler()

async def check_deadlines_job():
    db = get_db()
    if db is None:
        print("[Scheduler] DB connection is not initialized yet. Skipping check.")
        return
        
    now = datetime.utcnow()
    # Check for deadlines within the next 24 hours
    deadline_threshold = now + timedelta(hours=24)
    
    # Find todos that are not completed, due between now and 24 hours, and haven't sent reminders yet
    query = {
        "status": {"$in": ["pending", "in_progress"]},
        "deadline": {
            "$gt": now,
            "$lte": deadline_threshold
        },
        "reminded": {"$ne": True}
    }
    
    try:
        cursor = db.todos.find(query)
        todos_to_remind = await cursor.to_list(length=100)
        
        if not todos_to_remind:
            return
            
        print(f"[Scheduler] Found {len(todos_to_remind)} upcoming todo(s) within 24 hours.")
        
        for todo in todos_to_remind:
            user_id = todo.get("user_id")
            # Fetch user email
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                continue
                
            user_email = user.get("email")
            todo_title = todo.get("title")
            todo_deadline = todo.get("deadline")
            
            # Send email
            sent = send_deadline_email(user_email, todo_title, todo_deadline)
            if sent:
                # Update todo reminded status to True to avoid duplicate emails
                await db.todos.update_one(
                    {"_id": todo["_id"]},
                    {"$set": {"reminded": True, "updated_at": datetime.utcnow()}}
                )
                print(f"[Scheduler] Marked todo '{todo_title}' as reminded.")
    except Exception as e:
        print(f"[Scheduler] Error running deadline check job: {e}")

def start_scheduler():
    if not scheduler.running:
        # Run every 60 seconds (1 minute) for quick testing and feedback during local run
        scheduler.add_job(check_deadlines_job, "interval", minutes=1, id="check_deadlines_job_id")
        scheduler.start()
        print("[Scheduler] Scheduler started. Checking deadlines every 1 minute.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[Scheduler] Scheduler stopped.")
