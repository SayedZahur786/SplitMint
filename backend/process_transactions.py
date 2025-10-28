"""
Process Transactions Module - Main Pipeline
Orchestrates fetching, parsing, categorizing, and saving transactions
"""

from typing import Dict
from email_service import setup_gmail_service, fetch_transaction_emails
from parser import parse_transaction_from_email
from categorizer import categorize_merchant
from db import check_duplicate_transaction, insert_transaction, connect_db


def process_single_transaction(user_id: str, subject: str, body: str) -> Dict:
    """
    Process a single email transaction
    
    Args:
        user_id: User identifier
        subject: Email subject
        body: Email body
    
    Returns:
        Transaction dictionary or None
    """
    try:
        # Parse transaction details
        parsed = parse_transaction_from_email(subject, body)
        
        if not parsed:
            return None
        
        # Check for duplicates
        if check_duplicate_transaction(
            user_id,
            parsed['merchant'],
            parsed['amount'],
            parsed['date']
        ):
            return None
        
        # Categorize merchant
        category = categorize_merchant(parsed['merchant'])
        
        # Insert into database
        transaction_id = insert_transaction(
            user_id=user_id,
            merchant=parsed['merchant'],
            amount=parsed['amount'],
            category=category,
            date=parsed['date'],
            email_subject=subject
        )
        
        if transaction_id:
            return {
                'transaction_id': transaction_id,
                'merchant': parsed['merchant'],
                'amount': parsed['amount'],
                'category': category,
                'date': parsed['date']
            }
        
        return None
        
    except Exception as e:
        print(f"❌ Error processing single transaction: {e}")
        return None


def process_all_transactions(user_id: str) -> Dict:
    """
    Main orchestration function - fetch, parse, categorize, and save transactions
    
    Args:
        user_id: User identifier
    
    Returns:
        Dictionary with processing summary: {success, total_new, total_failed, message}
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting transaction processing for user: {user_id}")
    print(f"{'='*60}\n")
    
    # Track statistics
    total_processed = 0
    total_parsed = 0
    total_duplicates = 0
    total_inserted = 0
    total_failed = 0
    
    try:
        # Step 0: Connect to database
        print("🔗 Step 0: Connecting to database...")
        if not connect_db():
            return {
                'success': False,
                'total_new': 0,
                'total_failed': 0,
                'message': 'Failed to connect to database'
            }
        print("✅ Database connected\n")
        
        # Step 1: Setup Gmail service
        print("📧 Step 1: Setting up Gmail service...")
        service = setup_gmail_service()
        if not service:
            return {
                'success': False,
                'total_new': 0,
                'total_failed': 0,
                'message': 'Failed to setup Gmail service'
            }
        
        # Step 2: Fetch transaction emails (latest 3 emails)
        print("\n📬 Step 2: Fetching transaction emails...")
        emails = fetch_transaction_emails(num_emails=3, days_back=30)
        
        if not emails:
            return {
                'success': True,
                'total_new': 0,
                'total_failed': 0,
                'message': 'No transaction emails found'
            }
        
        total_processed = len(emails)
        print(f"✅ Retrieved {total_processed} emails\n")
        
        # Step 3: Process each email
        print("🔄 Step 3: Processing emails...\n")
        
        for i, email in enumerate(emails, 1):
            try:
                print(f"Processing email {i}/{total_processed}...")
                print(f"  Subject: {email['subject'][:60]}...")
                
                # Parse transaction
                parsed = parse_transaction_from_email(email['subject'], email['body'])
                
                if not parsed:
                    print(f"  ⚠️ No transaction found, skipping")
                    total_failed += 1
                    continue
                
                total_parsed += 1
                print(f"  ✓ Parsed: {parsed['merchant']} - ₹{parsed['amount']}")
                
                # Check for duplicates
                if check_duplicate_transaction(
                    user_id,
                    parsed['merchant'],
                    parsed['amount'],
                    parsed['date']
                ):
                    print(f"  ⚠️ Duplicate transaction, skipping")
                    total_duplicates += 1
                    continue
                
                # Categorize merchant
                category = categorize_merchant(parsed['merchant'])
                print(f"  ✓ Category: {category}")
                
                # Insert into database
                transaction_id = insert_transaction(
                    user_id=user_id,
                    merchant=parsed['merchant'],
                    amount=parsed['amount'],
                    category=category,
                    date=parsed['date'],
                    email_subject=email['subject']
                )
                
                if transaction_id:
                    print(f"  ✅ Saved to database (ID: {transaction_id})")
                    total_inserted += 1
                else:
                    print(f"  ❌ Failed to save to database")
                    total_failed += 1
                
                print()  # Blank line between emails
                
            except Exception as e:
                print(f"  ❌ Error processing email: {e}\n")
                total_failed += 1
                continue
        
        # Step 4: Summary
        print(f"\n{'='*60}")
        print("📊 PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total emails processed:     {total_processed}")
        print(f"Successfully parsed:        {total_parsed}")
        print(f"Duplicates skipped:         {total_duplicates}")
        print(f"New transactions inserted:  {total_inserted}")
        print(f"Failed/skipped:             {total_failed}")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'total_new': total_inserted,
            'total_failed': total_failed,
            'message': f'Successfully processed {total_inserted} new transactions'
        }
        
    except Exception as e:
        print(f"\n❌ Fatal error in process_all_transactions: {e}")
        return {
            'success': False,
            'total_new': total_inserted,
            'total_failed': total_failed + 1,
            'message': f'Error: {str(e)}'
        }


# Example usage
if __name__ == "__main__":
    # Test the pipeline
    result = process_all_transactions(user_id="test_user_123")
    print(f"\nFinal result: {result}")
