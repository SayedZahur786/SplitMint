"""
Gmail OAuth Setup Test
This script will open your browser and ask you to authorize the app
"""

import os
from email_service import setup_gmail_service

print("=" * 60)
print("Gmail OAuth Setup")
print("=" * 60)
print()
print("This will:")
print("1. Open your browser")
print("2. Ask you to sign in to Google")
print("3. Request permission to read your Gmail")
print("4. Save the token to token.json for future use")
print()
print("=" * 60)
print()

input("Press ENTER to continue...")

print("\nStarting Gmail authentication...")
print()

service = setup_gmail_service()

if service:
    print()
    print("=" * 60)
    print("✅ SUCCESS! Gmail integration is now working!")
    print("=" * 60)
    print()
    print("Token has been saved to token.json")
    print("You can now use the 'Fetch from Gmail' feature in the app!")
    print()
    
    # Test fetching emails
    print("Testing email fetch...")
    try:
        results = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])
        
        if messages:
            print(f"✅ Successfully connected! Found {len(messages)} message(s)")
        else:
            print("✅ Connected, but no messages found (inbox might be empty)")
    except Exception as e:
        print(f"⚠️ Connected, but couldn't fetch emails: {e}")
else:
    print()
    print("=" * 60)
    print("❌ FAILED! Gmail authentication did not complete")
    print("=" * 60)
    print()
    print("Please check:")
    print("- zyura_secret.json exists in the current directory")
    print("- You granted permission in the browser")
    print("- Your internet connection is working")
