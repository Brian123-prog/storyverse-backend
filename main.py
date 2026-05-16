from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="StoryVerse Global Engine")

# 🌍 GLOBALLY OPTIMIZED CORS CONFIGURATION
# This allows mobile devices and laptops from anywhere in the world to connect securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows global production traffic
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 🛠️ LIVE SMTP EMAIL DISPATCH CONFIGURATION
# =====================================================================
SMTP_SENDER_EMAIL = "brianomotoso@gmail.com"  
SMTP_APP_PASSWORD = "nclbvlodeamsjhvq"        
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  

def send_live_verification_email(recipient_email: str, pin_code: str):
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "🔐 StoryVerse | Confirm Your Creator Account PIN"
        message["From"] = f"StoryVerse Studio <{SMTP_SENDER_EMAIL}>"
        message["To"] = recipient_email  

        html_content = f"""
        <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0a0b10; color: #f3f4f6; padding: 40px; margin: 0;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #131520; padding: 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                    <h1 style="color: #6366f1; margin-bottom: 5px;">StoryVerse</h1>
                    <p style="color: #9ca3af; font-size: 0.95rem; margin-top: 0;">Multi-Vendor Marketplace Verification</p>
                    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.06); margin: 20px 0;">
                    <p style="font-size: 1rem; color: #f3f4f6; line-height: 1.5;">Welcome to the portal! Use the secret 6-digit verification code below to authorize your registration profile:</p>
                    <div style="background-color: #1b1e2e; color: #34d399; font-size: 2rem; font-weight: bold; letter-spacing: 6px; padding: 15px; border-radius: 12px; margin: 25px 0; border: 1px solid rgba(52, 211, 153, 0.2); text-shadow: 0 0 10px rgba(52, 211, 153, 0.2);">
                        {pin_code}
                    </div>
                    <p style="font-size: 0.8rem; color: #9ca3af; margin-top: 30px;">If you did not request this profile setup sequence, you can safely ignore this automated message transmission.</p>
                </div>
            </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_SENDER_EMAIL, SMTP_APP_PASSWORD)
        server.sendmail(SMTP_SENDER_EMAIL, recipient_email, message.as_string())
        server.quit()
        print(f"🚀 [SMTP SUCCESS]: Verification email sent out cleanly to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ [SMTP CRITICAL ERROR]: Handshake dropped. Reason: {e}")
        return False

# --- DATA STORAGE MOCKS ---
database_users = []       
database_stories = []     
story_id_counter = 1

# --- OBJECT VALIDATION DATA MODELS ---
class RegisterModel(BaseModel):
    email: str  
    password: str
    role: str   

class VerifyModel(BaseModel):
    email: str
    code: str

class LoginModel(BaseModel):
    email: str
    password: str

class StoryUploadModel(BaseModel):
    title: str
    price: float
    content: str
    author: str 

# --- API SERVICES ---

@app.get("/")
def health_check():
    return {"status": "online", "system": "StoryVerse Global Cloud Gateway Active"}

@app.post("/api/register")
def register_user(user: RegisterModel):
    for existing_user in database_users:
        if existing_user["email"].lower() == user.email.lower():
            raise HTTPException(status_code=400, detail="An account with this email address already exists!")
    
    verification_pin = str(random.randint(100000, 999999))
    email_success = send_live_verification_email(user.email.lower(), verification_pin)
    
    if not email_success:
        raise HTTPException(status_code=500, detail="Global mail server routing path failure.")
    
    new_user = {
        "email": user.email.lower(),
        "password": user.password,
        "role": user.role,
        "is_verified": False,
        "verification_code": verification_pin
    }
    database_users.append(new_user)
    return {"status": "success", "message": "Verification code dispatched!"}

@app.post("/api/verify-code")
def verify_code(data: VerifyModel):
    for user in database_users:
        if user["email"] == data.email.lower():
            if user["verification_code"] == data.code:
                user["is_verified"] = True
                user["verification_code"] = None 
                return {"status": "success", "message": "Email verified successfully!"}
            else:
                raise HTTPException(status_code=400, detail="Invalid verification code mismatch.")
    raise HTTPException(status_code=404, detail="Profile record missing.")

@app.post("/api/login")
def login_user(user: LoginModel):
    for existing_user in database_users:
        if existing_user["email"] == user.email.lower() and existing_user["password"] == user.password:
            if not existing_user["is_verified"]:
                raise HTTPException(status_code=403, detail="Please verify your email registration code first!")
            return {"status": "success", "email": existing_user["email"], "role": existing_user["role"]}
    raise HTTPException(status_code=401, detail="Invalid credentials.")

@app.post("/api/upload-story")
def upload_story(story: StoryUploadModel):
    global story_id_counter
    database_stories.append({
        "id": story_id_counter, "title": story["title"], "price": story["price"],
        "content": story["content"], "author": story["author"], "is_locked": False
    })
    story_id_counter += 1
    return {"status": "success"}

@app.get("/api/get-stories")
def get_stories():
    processed_stories = []
    for story in database_stories:
        processed_stories.append({
            "id": story["id"], "title": story["title"], "price": story["price"],
            "author": story["author"], "content": story["content"], "is_locked": False
        })
    return processed_stories

@app.delete("/api/delete-story/{story_id}")
def delete_story(story_id: int):
    global database_stories
    for i, story in enumerate(database_stories):
        if story["id"] == story_id:
            database_stories.pop(i)
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Story not found")