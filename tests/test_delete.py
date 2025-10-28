"""
Test delete transaction functionality
"""

import requests
import json

API_BASE = "http://localhost:8000"

print("\n" + "="*60)
print("🧪 TESTING DELETE TRANSACTION")
print("="*60 + "\n")

# First, let's get the transactions to find one to delete
user_id = "test_user_123"

print("📋 Step 1: Getting transactions...")
response = requests.get(f"{API_BASE}/api/transactions", params={
    "user_id": user_id,
    "limit": 10
})

if response.status_code == 200:
    data = response.json()
    transactions = data.get('data', {}).get('transactions', [])
    
    print(f"✅ Found {len(transactions)} transaction(s)\n")
    
    if transactions:
        # Show the first transaction
        txn = transactions[0]
        print(f"Transaction to delete:")
        print(f"  ID: {txn['_id']}")
        print(f"  Merchant: {txn['merchant']}")
        print(f"  Amount: ₹{txn['amount']}")
        print(f"  Category: {txn['category']}")
        print(f"  Date: {txn['date']}\n")
        
        # Ask for confirmation
        confirm = input("Delete this transaction? (yes/no): ")
        
        if confirm.lower() == 'yes':
            print("\n🗑️ Step 2: Deleting transaction...")
            
            delete_response = requests.delete(
                f"{API_BASE}/api/delete-transaction",
                json={
                    "user_id": user_id,
                    "transaction_id": txn['_id']
                }
            )
            
            if delete_response.status_code == 200:
                result = delete_response.json()
                print(f"✅ {result['message']}\n")
                
                # Verify deletion
                print("📋 Step 3: Verifying deletion...")
                verify_response = requests.get(f"{API_BASE}/api/transactions", params={
                    "user_id": user_id,
                    "limit": 10
                })
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    remaining = verify_data.get('data', {}).get('transactions', [])
                    print(f"✅ Remaining transactions: {len(remaining)}\n")
            else:
                print(f"❌ Delete failed: {delete_response.text}\n")
        else:
            print("\n❌ Deletion cancelled\n")
    else:
        print("❌ No transactions found to delete\n")
else:
    print(f"❌ Failed to get transactions: {response.text}\n")

print("="*60 + "\n")
