"""
MongoDB Database Helper Module
Handles all database interactions for SplitMint
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global database connection
db = None
client = None


def connect_db():
    """Initialize MongoDB connection"""
    global db, client
    
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            print("❌ ERROR: MONGODB_URI not found in .env file")
            return False
        
        print("🔗 Connecting to MongoDB...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        # Create database and collections
        db = client["splitmint"]
        
        # Create collections if they don't exist
        if "transactions" not in db.list_collection_names():
            db.create_collection("transactions")
            print("✅ Created 'transactions' collection")
        
        if "budgets" not in db.list_collection_names():
            db.create_collection("budgets")
            print("✅ Created 'budgets' collection")
        
        # Create indexes for faster queries
        db.transactions.create_index([("user_id", ASCENDING)])
        db.transactions.create_index([("date", ASCENDING)])
        db.budgets.create_index([("user_id", ASCENDING), ("month", ASCENDING)], unique=True)
        
        print("✅ MongoDB connection established successfully!")
        print(f"📦 Database: splitmint")
        print(f"📊 Collections: transactions, budgets")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def insert_transaction(
    user_id: str,
    merchant: str,
    amount: float,
    category: str,
    date: str,
    email_subject: str = None
) -> Optional[str]:
    """
    Insert a new transaction document
    
    Args:
        user_id: User identifier
        merchant: Merchant/store name
        amount: Transaction amount
        category: Transaction category
        date: Transaction date (YYYY-MM-DD format)
        email_subject: Original email subject (optional)
    
    Returns:
        Inserted document ID as string, or None if failed
    """
    try:
        transaction = {
            "user_id": user_id,
            "merchant": merchant,
            "amount": float(amount),
            "category": category,
            "date": date,
            "email_subject": email_subject,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db.transactions.insert_one(transaction)
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"❌ Error inserting transaction: {e}")
        return None


def get_transactions(user_id: str, limit: int = 100) -> List[Dict]:
    """
    Get all transactions for a user, sorted by date (newest first)
    
    Args:
        user_id: User identifier
        limit: Maximum number of transactions to return
    
    Returns:
        List of transaction dictionaries
    """
    try:
        transactions = db.transactions.find(
            {"user_id": user_id}
        ).sort("date", -1).limit(limit)
        
        # Convert ObjectId to string and return as list
        result = []
        for t in transactions:
            t["_id"] = str(t["_id"])
            result.append(t)
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching transactions: {e}")
        return []


def check_duplicate_transaction(
    user_id: str,
    merchant: str,
    amount: float,
    date_str: str
) -> bool:
    """
    Check if a transaction already exists
    
    Args:
        user_id: User identifier
        merchant: Merchant name
        amount: Transaction amount
        date_str: Transaction date
    
    Returns:
        True if duplicate exists, False otherwise
    """
    try:
        existing = db.transactions.find_one({
            "user_id": user_id,
            "merchant": merchant,
            "amount": amount,
            "date": date_str
        })
        
        return existing is not None
        
    except Exception as e:
        print(f"❌ Error checking duplicate: {e}")
        return False


def delete_transaction(transaction_id: str, user_id: str) -> bool:
    """
    Delete a transaction by ID
    
    Args:
        transaction_id: Transaction ID (MongoDB ObjectId as string)
        user_id: User identifier (for security verification)
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        from bson.objectid import ObjectId
        
        # Verify the transaction belongs to this user before deleting
        result = db.transactions.delete_one({
            "_id": ObjectId(transaction_id),
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            print(f"✅ Deleted transaction: {transaction_id}")
            return True
        else:
            print(f"⚠️ Transaction not found or doesn't belong to user: {transaction_id}")
            return False
        
    except Exception as e:
        print(f"❌ Error deleting transaction: {e}")
        return False


def update_budget(user_id: str, income: float, budget: float, month: str) -> bool:
    """
    Insert or update budget document
    
    Args:
        user_id: User identifier
        income: Monthly income
        budget: Monthly budget limit
        month: Month in format "YYYY-MM"
    
    Returns:
        True if successful, False otherwise
    """
    try:
        budget_doc = {
            "user_id": user_id,
            "month": month,
            "income": float(income),
            "budget": float(budget),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Upsert: update if exists, insert if not
        result = db.budgets.update_one(
            {"user_id": user_id, "month": month},
            {
                "$set": budget_doc,
                "$setOnInsert": {"created_at": datetime.utcnow().isoformat()}
            },
            upsert=True
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating budget: {e}")
        return False


def get_budget(user_id: str, month: str) -> Optional[Dict]:
    """
    Get budget document for user and month
    
    Args:
        user_id: User identifier
        month: Month in format "YYYY-MM"
    
    Returns:
        Budget dictionary or None if not found
    """
    try:
        budget = db.budgets.find_one({
            "user_id": user_id,
            "month": month
        })
        
        if budget:
            budget["_id"] = str(budget["_id"])
            return budget
        
        return None
        
    except Exception as e:
        print(f"❌ Error fetching budget: {e}")
        return None


def get_all_transactions_by_month(user_id: str, month: str) -> List[Dict]:
    """
    Get all transactions for a user in a specific month
    
    Args:
        user_id: User identifier
        month: Month in format "YYYY-MM"
    
    Returns:
        List of transaction dictionaries
    """
    try:
        # Query for dates starting with the month prefix (e.g., "2025-10")
        transactions = db.transactions.find({
            "user_id": user_id,
            "date": {"$regex": f"^{month}"}
        }).sort("date", -1)
        
        result = []
        for t in transactions:
            t["_id"] = str(t["_id"])
            result.append(t)
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching monthly transactions: {e}")
        return []


def insert_demo_transactions(user_id: str, month: str) -> int:
    """
    Insert 10 sample transactions for testing
    
    Args:
        user_id: User identifier
        month: Month in format "YYYY-MM"
    
    Returns:
        Number of transactions inserted
    """
    demo_data = [
        {"merchant": "Domino's Pizza", "amount": 450, "category": "Food & Dining", "day": "05"},
        {"merchant": "Amazon", "amount": 1299, "category": "Shopping & E-commerce", "day": "08"},
        {"merchant": "Swiggy", "amount": 320, "category": "Food & Dining", "day": "10"},
        {"merchant": "Uber", "amount": 180, "category": "Transport", "day": "12"},
        {"merchant": "Netflix", "amount": 649, "category": "Entertainment", "day": "15"},
        {"merchant": "Big Bazaar", "amount": 2500, "category": "Shopping & E-commerce", "day": "18"},
        {"merchant": "Zomato", "amount": 280, "category": "Food & Dining", "day": "20"},
        {"merchant": "Apollo Pharmacy", "amount": 650, "category": "Healthcare", "day": "22"},
        {"merchant": "Flipkart", "amount": 899, "category": "Shopping & E-commerce", "day": "25"},
        {"merchant": "Starbucks", "amount": 220, "category": "Food & Dining", "day": "28"},
    ]
    
    inserted_count = 0
    
    try:
        for item in demo_data:
            date_str = f"{month}-{item['day']}"
            
            # Check if already exists
            if not check_duplicate_transaction(user_id, item["merchant"], item["amount"], date_str):
                transaction_id = insert_transaction(
                    user_id=user_id,
                    merchant=item["merchant"],
                    amount=item["amount"],
                    category=item["category"],
                    date=date_str,
                    email_subject=f"Payment to {item['merchant']}"
                )
                
                if transaction_id:
                    inserted_count += 1
        
        print(f"✅ Inserted {inserted_count} demo transactions")
        return inserted_count
        
    except Exception as e:
        print(f"❌ Error inserting demo data: {e}")
        return inserted_count


# ============================================================
# Split Transaction Functions
# ============================================================

def create_split_collection():
    """Create splits collection if it doesn't exist"""
    global db
    
    if db is None:
        print("❌ Database not connected")
        return False
    
    try:
        if "splits" not in db.list_collection_names():
            db.create_collection("splits")
            print("✅ Created 'splits' collection")
        
        # Create index for faster queries
        db.splits.create_index([("transaction_id", ASCENDING)])
        db.splits.create_index([("user_id", ASCENDING)])
        
        return True
    except Exception as e:
        print(f"❌ Error creating splits collection: {e}")
        return False


def calculate_split_amounts(total_amount: float, participants: List[Dict], split_method: str) -> List[Dict]:
    """
    Calculate split amounts for each participant
    
    Args:
        total_amount: Total transaction amount
        participants: List of participant dictionaries
        split_method: 'equal', 'percentage', or 'ratio'
    
    Returns:
        Updated participants list with calculated amounts
    """
    num_participants = len(participants)
    
    if split_method == 'equal':
        # Split equally
        share_amount = total_amount / num_participants
        for participant in participants:
            participant['share_amount'] = round(share_amount, 2)
            participant['share_percentage'] = round(100 / num_participants, 2)
            participant['share_ratio'] = 1
    
    elif split_method == 'percentage':
        # Split by percentage
        total_percentage = sum(p.get('share_percentage', 0) for p in participants)
        
        if abs(total_percentage - 100) > 0.01:  # Allow small rounding errors
            raise ValueError(f"Percentages must add up to 100, got {total_percentage}")
        
        for participant in participants:
            percentage = participant.get('share_percentage', 0)
            participant['share_amount'] = round((percentage / 100) * total_amount, 2)
    
    elif split_method == 'ratio':
        # Split by ratio
        total_ratio = sum(p.get('share_ratio', 1) for p in participants)
        
        for participant in participants:
            ratio = participant.get('share_ratio', 1)
            participant['share_percentage'] = round((ratio / total_ratio) * 100, 2)
            participant['share_amount'] = round((ratio / total_ratio) * total_amount, 2)
    
    # Calculate who owes what
    total_paid = sum(p.get('amount_paid', 0) for p in participants)
    
    if abs(total_paid - total_amount) > 0.01:
        raise ValueError(f"Total paid ({total_paid}) must equal transaction amount ({total_amount})")
    
    for participant in participants:
        amount_paid = participant.get('amount_paid', 0)
        share_amount = participant.get('share_amount', 0)
        participant['amount_owed'] = round(share_amount - amount_paid, 2)
    
    return participants


def create_or_update_split(user_id: str, transaction_id: str, participants: List[Dict], 
                           split_method: str, notes: Optional[str] = None) -> Optional[str]:
    """
    Create or update a split transaction
    
    Args:
        user_id: User identifier
        transaction_id: Original transaction ID
        participants: List of participant dictionaries
        split_method: 'equal', 'percentage', or 'ratio'
        notes: Optional notes
    
    Returns:
        Split ID if successful, None otherwise
    """
    global db
    
    if db is None:
        print("❌ Database not connected")
        return None
    
    try:
        from bson import ObjectId
        
        # Ensure splits collection exists
        create_split_collection()
        
        # Get the original transaction
        transaction = db.transactions.find_one({"_id": ObjectId(transaction_id), "user_id": user_id})
        
        if not transaction:
            print(f"❌ Transaction {transaction_id} not found")
            return None
        
        # Calculate split amounts
        calculated_participants = calculate_split_amounts(
            transaction['amount'], 
            participants, 
            split_method
        )
        
        # Create split document
        split_doc = {
            "user_id": user_id,
            "transaction_id": transaction_id,
            "merchant": transaction['merchant'],
            "total_amount": transaction['amount'],
            "category": transaction['category'],
            "date": transaction['date'],
            "split_method": split_method,
            "participants": calculated_participants,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Check if split already exists for this transaction
        existing_split = db.splits.find_one({"transaction_id": transaction_id, "user_id": user_id})
        
        if existing_split:
            # Update existing split
            split_doc["updated_at"] = datetime.now().isoformat()
            db.splits.update_one(
                {"_id": existing_split["_id"]},
                {"$set": split_doc}
            )
            print(f"✅ Updated split for transaction {transaction_id}")
            return str(existing_split["_id"])
        else:
            # Create new split
            result = db.splits.insert_one(split_doc)
            print(f"✅ Created split for transaction {transaction_id}")
            return str(result.inserted_id)
    
    except ValueError as e:
        print(f"❌ Validation error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error creating split: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_split_by_transaction(user_id: str, transaction_id: str) -> Optional[Dict]:
    """
    Get split details for a transaction
    
    Args:
        user_id: User identifier
        transaction_id: Transaction ID
    
    Returns:
        Split document if found, None otherwise
    """
    global db
    
    if db is None:
        print("❌ Database not connected")
        return None
    
    try:
        split = db.splits.find_one({"transaction_id": transaction_id, "user_id": user_id})
        
        if split:
            split["_id"] = str(split["_id"])
            return split
        
        return None
    
    except Exception as e:
        print(f"❌ Error getting split: {e}")
        return None


def delete_split(user_id: str, transaction_id: str) -> bool:
    """
    Delete a split transaction
    
    Args:
        user_id: User identifier
        transaction_id: Transaction ID
    
    Returns:
        True if deleted, False otherwise
    """
    global db
    
    if db is None:
        print("❌ Database not connected")
        return False
    
    try:
        result = db.splits.delete_one({"transaction_id": transaction_id, "user_id": user_id})
        
        if result.deleted_count > 0:
            print(f"✅ Deleted split for transaction {transaction_id}")
            return True
        else:
            print(f"⚠️ No split found for transaction {transaction_id}")
            return False
    
    except Exception as e:
        print(f"❌ Error deleting split: {e}")
        return False


def get_all_splits(user_id: str) -> List[Dict]:
    """
    Get all splits for a user
    
    Args:
        user_id: User identifier
    
    Returns:
        List of split documents
    """
    global db
    
    if db is None:
        print("❌ Database not connected")
        return []
    
    try:
        splits = list(db.splits.find({"user_id": user_id}).sort("date", -1))
        
        # Convert ObjectId to string
        for split in splits:
            split["_id"] = str(split["_id"])
        
        return splits
    
    except Exception as e:
        print(f"❌ Error getting splits: {e}")
        return []
