"""
Email Service Module - Enhanced Gmail Fetching
Handles all Gmail API interactions for fetching transaction emails
"""

import os
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CLIENT_SECRETS_FILE = 'zyura_secret.json'


def setup_gmail_service():
    """
    Load Gmail credentials and setup service
    
    Returns:
        Gmail service object or None if failed
    """
    creds = None
    
    try:
        # Step 1: Load existing token if available
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print("✅ Loaded existing credentials from token.json")
        
        # Step 2: If no valid creds, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("♻️ Refreshing expired token...")
                creds.refresh(Request())
            else:
                print("🌐 No valid token found, running OAuth flow...")
                
                if not os.path.exists(CLIENT_SECRETS_FILE):
                    print(f"❌ ERROR: {CLIENT_SECRETS_FILE} not found!")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE,
                    SCOPES
                )
                
                # Run local server for OAuth
                port = 8080
                print(f"🚀 Starting local OAuth server on http://localhost:{port}/ ...")
                creds = flow.run_local_server(port=port)
                print(f"🛑 Local OAuth server on port {port} stopped successfully.")
                print("✅ Authentication successful, credentials obtained.")
                
                # Save credentials for future runs
                with open('token.json', 'w') as f:
                    f.write(creds.to_json())
                print("💾 Credentials saved to token.json")
        
        # Step 3: Connect to Gmail API
        print("🔗 Connecting to Gmail API...")
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API connection established!")
        
        return service
        
    except Exception as e:
        print(f"❌ Error setting up Gmail service: {e}")
        return None


def get_email_body(service, message_id: str) -> str:
    """
    Extract plain text body from an email message
    
    Args:
        service: Gmail service object
        message_id: Gmail message ID
    
    Returns:
        Email body text (limited to 1000 chars)
    """
    try:
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        payload = msg.get('payload', {})
        body_text = ""
        
        # Handle simple text email
        if 'body' in payload and payload['body'].get('data'):
            body_text = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')
        
        # Handle multipart email
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
        
        # Limit to 1000 characters
        return body_text[:1000] if body_text else ""
        
    except Exception as e:
        print(f"⚠️ Error extracting email body: {e}")
        return ""


def fetch_transaction_emails(num_emails: int = 3, days_back: int = 30) -> List[Dict]:
    """
    Query Gmail API for transaction-related emails
    
    Args:
        num_emails: Maximum number of emails to fetch
        days_back: Number of days to look back
    
    Returns:
        List of email dictionaries with keys: message_id, subject, body, sender, date
    """
    try:
        service = setup_gmail_service()
        if not service:
            print("❌ Failed to setup Gmail service")
            return []
        
        # Calculate timestamp for days_back
        after_date = datetime.now() - timedelta(days=days_back)
        after_timestamp = after_date.strftime('%Y/%m/%d')
        
        # Gmail query: filter for transaction keywords
        query = f'subject:(transaction OR payment OR spent OR debited OR credited OR "bank alert") after:{after_timestamp}'
        
        print(f"📬 Fetching transaction emails (last {days_back} days, max {num_emails})...")
        print(f"🔍 Query: {query}")
        
        # Fetch message list
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=num_emails
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("📭 No transaction emails found")
            return []
        
        print(f"📨 Found {len(messages)} emails, extracting details...")
        
        email_list = []
        
        for msg in messages:
            try:
                msg_detail = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = msg_detail['payload']['headers']
                
                # Extract headers
                subject = next(
                    (h['value'] for h in headers if h['name'].lower() == 'subject'),
                    "(No Subject)"
                )
                sender = next(
                    (h['value'] for h in headers if h['name'].lower() == 'from'),
                    "(No Sender)"
                )
                date = next(
                    (h['value'] for h in headers if h['name'].lower() == 'date'),
                    ""
                )
                
                # Extract body
                body = get_email_body(service, msg['id'])
                
                email_list.append({
                    "message_id": msg['id'],
                    "subject": subject,
                    "body": body,
                    "sender": sender,
                    "date": date
                })
                
            except Exception as e:
                print(f"⚠️ Error processing email {msg['id']}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(email_list)} emails")
        return email_list
        
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []
