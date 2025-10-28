"""
Quick script to check recent transactions in database
"""

from SplitMint.backend.db import connect_db, get_transactions
from datetime import datetime

print("\n" + "="*60)
print("📊 CHECKING DATABASE TRANSACTIONS")
print("="*60 + "\n")

# Connect to database
if connect_db():
    print("✅ Database connected\n")
    
    # Get transactions for test user
    user_id = "test_user_123"
    
    print(f"🔍 Fetching transactions for user: {user_id}\n")
    
    transactions = get_transactions(user_id, limit=50)
    
    if transactions:
        total_spent = sum(txn.get('amount', 0) for txn in transactions)
        
        print(f"✅ Found {len(transactions)} transaction(s)")
        print(f"💰 Total spent: ₹{total_spent}\n")
        
        if transactions:
            print("="*60)
            print("TRANSACTION DETAILS")
            print("="*60 + "\n")
            
            for i, txn in enumerate(transactions, 1):
                print(f"Transaction #{i}:")
                print(f"  Merchant: {txn.get('merchant')}")
                print(f"  Amount: ₹{txn.get('amount')}")
                print(f"  Category: {txn.get('category')}")
                print(f"  Date: {txn.get('date')}")
                print(f"  Created: {txn.get('created_at')}")
                print()
    else:
        print("❌ No transactions found")
else:
    print("❌ Failed to connect to database")

print("="*60 + "\n")
