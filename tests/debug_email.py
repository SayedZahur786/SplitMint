"""
Debug script to check email content and test parsing
"""

from SplitMint.backend.email_service import fetch_transaction_emails
from SplitMint.backend.parser import parse_transaction_from_email
import json

print("\n" + "="*60)
print("🔍 EMAIL DEBUG SCRIPT")
print("="*60 + "\n")

# Fetch emails
print("📧 Fetching transaction emails...\n")
emails = fetch_transaction_emails()

if not emails:
    print("❌ No emails found!")
else:
    print(f"✅ Found {len(emails)} email(s)\n")
    
    for i, email in enumerate(emails, 1):
        print("="*60)
        print(f"EMAIL #{i}")
        print("="*60)
        
        # Show email details
        print(f"\n📌 SUBJECT:")
        print(f"   {email.get('subject', 'N/A')}")
        
        print(f"\n📄 BODY (first 500 chars):")
        body = email.get('body', 'N/A')
        print(f"   {body[:500]}")
        
        if len(body) > 500:
            print(f"   ... ({len(body)} total characters)")
        
        print(f"\n📅 DATE:")
        print(f"   {email.get('date', 'N/A')}")
        
        # Try to parse
        print(f"\n🔄 PARSING ATTEMPT:")
        result = parse_transaction_from_email(
            email.get('subject', ''),
            email.get('body', '')
        )
        
        if result:
            print(f"   ✅ SUCCESS!")
            print(f"   Merchant: {result['merchant']}")
            print(f"   Amount: ₹{result['amount']}")
            print(f"   Date: {result['date']}")
        else:
            print(f"   ❌ FAILED - No transaction pattern matched")
            
            # Show what we're searching for
            print(f"\n   Debugging hints:")
            print(f"   - Looking for currency symbols: Rs, Rs., ₹")
            print(f"   - Looking for keywords: spent, debited, payment, transaction")
            print(f"   - Checking full text: {email.get('subject', '')} {email.get('body', '')[:200]}")
        
        print("\n")

print("="*60)
print("✅ Debug complete!")
print("="*60 + "\n")
