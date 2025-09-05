import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from gmail_service import fetch_emails
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local dev setup
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
REDIRECT_URI = "http://localhost:8000/callback"

flow = Flow.from_client_secrets_file(
    CLIENT_SECRET_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

TOKEN_FILE = "token.json"
creds: Credentials = None

@app.get("/login")
def login():
    """Redirect to Google OAuth consent page"""
    auth_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)

@app.get("/callback")
def callback(request: Request):
    """Handle OAuth callback and save credentials"""
    global creds
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials
    # Save credentials to file
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    return RedirectResponse("http://localhost:5500/inbox.html")

@app.get("/fetch-emails")
def get_emails():
    """Fetch emails from Gmail using stored credentials"""
    global creds
    # Load credentials from file if missing
    if not creds:
        try:
            with open(TOKEN_FILE, "r") as f:
                creds = Credentials.from_authorized_user_info(json.loads(f.read()))
        except Exception:
            return JSONResponse(content={"error": "Not authenticated"}, status_code=401)
    
    try:
        emails = fetch_emails(creds, max_results=10)
        return {"emails": emails}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
