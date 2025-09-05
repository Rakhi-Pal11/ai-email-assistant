from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def fetch_emails(creds: Credentials, max_results=10):
    """
    Fetch emails from Gmail using the provided credentials.
    Returns a list of dictionaries with id, from, subject, snippet.
    """
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == "Subject"), "No subject")
        sender = next((h['value'] for h in headers if h['name'] == "From"), "Unknown sender")
        snippet = msg_detail.get('snippet', "")

        emails.append({
            "id": msg['id'],
            "from": sender,
            "subject": subject,
            "snippet": snippet
        })
    return emails
