"""
Testing Script for SplitMint Backend
Tests all components and API endpoints
"""

import sys
import os
from datetime import datetime

print("🧪 SplitMint Backend Test Suite")
print("="*60 + "\n")

# Test 1: MongoDB Connection
print("Test 1: MongoDB Connection")
print("-"*40)
try:
    from SplitMint.backend.db import connect_db
    result = connect_db()
    if result:
        print("✅ PASS: MongoDB connected successfully\n")
    else:
        print("❌ FAIL: MongoDB connection failed\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 2: Transaction Parsing
print("Test 2: Transaction Parsing")
print("-"*40)
try:
    from SplitMint.backend.parser import parse_transaction_from_email
    
    test_cases = [
        {
            "subject": "Payment Alert",
            "body": "Rs. 450 spent at Domino's Pizza on 15 Oct 2025",
            "expected_merchant": "Domino's Pizza",
            "expected_amount": 450
        },
        {
            "subject": "Transaction Alert",
            "body": "₹1299 debited to Amazon on 18/10/2025",
            "expected_merchant": "Amazon",
            "expected_amount": 1299
        }
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        result = parse_transaction_from_email(test['subject'], test['body'])
        if result and result['amount'] == test['expected_amount']:
            print(f"  ✅ Test {i} PASS: {result['merchant']} - ₹{result['amount']}")
            passed += 1
        else:
            print(f"  ❌ Test {i} FAIL: Expected ₹{test['expected_amount']}, got {result}")
    
    print(f"\nParsing Tests: {passed}/{len(test_cases)} passed\n")
    
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 3: Merchant Categorization
print("Test 3: Merchant Categorization")
print("-"*40)
try:
    from SplitMint.backend.categorizer import categorize_merchant
    
    test_merchants = [
        ("Domino's Pizza", ["Food & Dining"]),
        ("Amazon India", ["Shopping & E-commerce"]),
        ("Netflix", ["Entertainment"]),
        ("Uber", ["Transport"]),
        ("Apollo Pharmacy", ["Healthcare"]),
    ]
    
    passed = 0
    for merchant, expected_categories in test_merchants:
        category = categorize_merchant(merchant)
        if category in expected_categories:
            print(f"  ✅ {merchant:25} → {category}")
            passed += 1
        else:
            print(f"  ❌ {merchant:25} → {category} (expected one of {expected_categories})")
    
    print(f"\nCategorization Tests: {passed}/{len(test_merchants)} passed\n")
    
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 4: Database Operations
print("Test 4: Database Operations")
print("-"*40)
try:
    from SplitMint.backend.db import insert_transaction, get_transactions, update_budget, get_budget
    
    test_user = "test_user_" + datetime.now().strftime("%Y%m%d%H%M%S")
    test_month = "2025-10"
    
    # Test insert transaction
    transaction_id = insert_transaction(
        user_id=test_user,
        merchant="Test Merchant",
        amount=100.50,
        category="Food & Dining",
        date="2025-10-28"
    )
    
    if transaction_id:
        print(f"  ✅ Transaction inserted (ID: {transaction_id})")
    else:
        print(f"  ❌ Transaction insert failed")
    
    # Test get transactions
    transactions = get_transactions(test_user)
    if len(transactions) > 0:
        print(f"  ✅ Retrieved {len(transactions)} transaction(s)")
    else:
        print(f"  ❌ Failed to retrieve transactions")
    
    # Test update budget
    budget_updated = update_budget(test_user, 50000, 30000, test_month)
    if budget_updated:
        print(f"  ✅ Budget updated")
    else:
        print(f"  ❌ Budget update failed")
    
    # Test get budget
    budget = get_budget(test_user, test_month)
    if budget and budget['budget'] == 30000:
        print(f"  ✅ Budget retrieved correctly")
    else:
        print(f"  ❌ Budget retrieval failed")
    
    print("\n✅ Database operations test completed\n")
    
except Exception as e:
    print(f"❌ FAIL: {e}\n")

# Test 5: FastAPI Endpoints (requires server to be running)
print("Test 5: FastAPI Endpoints")
print("-"*40)
print("⚠️  To test endpoints, start the server with:")
print("    uvicorn main:app --reload")
print("\nThen test manually using:")
print("  - Browser: http://localhost:8000/docs")
print("  - Or use curl/httpx to test endpoints")

try:
    import httpx
    
    print("\n  Attempting to connect to server...")
    response = httpx.get("http://localhost:8000/health", timeout=2.0)
    
    if response.status_code == 200:
        print(f"  ✅ Server is running!")
        print(f"  ✅ Health check: {response.json()}")
        
        # Test other endpoints
        test_user = "test_user_api"
        
        # Test load demo data
        demo_response = httpx.post(
            "http://localhost:8000/api/load-demo-data",
            json={"user_id": test_user, "month": "2025-10"},
            timeout=5.0
        )
        if demo_response.status_code == 200:
            print(f"  ✅ Demo data loaded: {demo_response.json()}")
        
        # Test get transactions
        trans_response = httpx.get(
            f"http://localhost:8000/api/transactions?user_id={test_user}",
            timeout=5.0
        )
        if trans_response.status_code == 200:
            print(f"  ✅ Transactions retrieved: {trans_response.json()['count']} items")
        
    else:
        print(f"  ❌ Server returned status {response.status_code}")
        
except Exception as e:
    print(f"  ⚠️  Server not running or error: {e}")
    print(f"  💡 Start server with: uvicorn main:app --reload")

print("\n" + "="*60)
print("🏁 Test Suite Completed")
print("="*60)
