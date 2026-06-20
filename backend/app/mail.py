import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from .config import settings

def send_deadline_email(to_email: str, todo_title: str, deadline: datetime) -> bool:
    # Check if SMTP is configured
    is_configured = (
        settings.SMTP_EMAIL and 
        settings.SMTP_EMAIL != "your_email@gmail.com" and 
        settings.SMTP_PASSWORD and 
        settings.SMTP_PASSWORD != "your_gmail_app_password"
    )
    
    subject = f"[Nhắc nhở Deadline] Công việc: {todo_title} sắp đến hạn!"
    # Format deadline for presentation (Vietnamese time is local, so we just format it directly)
    deadline_str = deadline.strftime("%H:%M %d/%m/%Y")
    
    body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff;">
            <h2 style="color: #e53935; border-bottom: 2px solid #e53935; padding-bottom: 10px; margin-top: 0;">⏰ Cảnh Báo Sắp Hết Hạn Công Việc!</h2>
            <p>Xin chào,</p>
            <p>Đây là thông báo tự động từ hệ thống quản lý công việc <strong>To Do List AI</strong>.</p>
            <p>Công việc sau đây của bạn sắp đến thời hạn deadline:</p>
            <div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #e53935; margin: 15px 0; border-radius: 4px;">
                <strong style="font-size: 16px; color: #b71c1c;">Tiêu đề:</strong> {todo_title}<br/>
                <strong style="font-size: 16px; color: #b71c1c;">Hạn chót:</strong> <span style="color: #e53935; font-weight: bold;">{deadline_str}</span>
            </div>
            <p>Vui lòng truy cập website để hoàn thành công việc kịp thời.</p>
            <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 20px 0;" />
            <p style="font-size: 12px; color: #9e9e9e; text-align: center;">Email này được gửi tự động từ hệ thống To Do List AI. Vui lòng không trả lời email này.</p>
        </div>
    </body>
    </html>
    """
    
    if not is_configured:
        print(f"\n--- [MOCK EMAIL TRIGGERED] ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body (Text version): Công việc '{todo_title}' sắp đến hạn chót vào lúc {deadline_str}!")
        print(f"-------------------------------\n")
        return True
        
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        
        # Connect to SMTP Server
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL, to_email, msg.as_string())
        server.close()
        print(f"Successfully sent deadline reminder email to {to_email} for todo '{todo_title}'")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email} for todo '{todo_title}': {e}")
        return False
