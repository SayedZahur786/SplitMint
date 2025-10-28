"""
SplitMint FastAPI Server
Main backend server for expense tracking and transaction management
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import os

# Import models
from models import (
    FetchTransactionsRequest,
    UpdateBudgetRequest,
    AddTransactionRequest,
    DeleteTransactionRequest,
    ApiResponse,
    BudgetResponse,
    CreateSplitRequest,
    GetSplitRequest,
    DeleteSplitRequest,
    SplitResponse
)

# Import database functions
from db import (
    connect_db,
    insert_transaction,
    get_transactions,
    update_budget,
    get_budget,
    get_all_transactions_by_month,
    delete_transaction,
    create_or_update_split,
    get_split_by_transaction,
    delete_split,
    get_all_splits
)

# Import processing pipeline
from process_transactions import process_all_transactions

# Import categorizer for validation
from categorizer import get_valid_categories

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="SplitMint",
    version="1.0",
    description="Expense tracker backend with Gmail integration and AI categorization"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email monitoring thread
email_monitor_thread = None


@app.on_event("startup")
async def startup_event():
    """Initialize database connection and start email monitoring on startup"""
    global email_monitor_thread
    
    print("\n" + "="*60)
    print("🚀 SplitMint FastAPI Server Starting...")
    print("="*60 + "\n")
    
    # Connect to database
    if connect_db():
        print("\n✅ Database connected successfully")
    else:
        print("\n❌ WARNING: Database connection failed")
    
    # Start email monitoring
    auto_monitor = os.getenv("AUTO_MONITOR_EMAILS", "true").lower() == "true"
    
    if auto_monitor:
        print("\n📧 Starting automatic email monitoring...")
        from email_monitor import start_monitoring_thread
        email_monitor_thread = start_monitoring_thread()
        print("✅ Email monitoring started (checks every 45 seconds, fetches 3 latest emails)")
    else:
        print("\n⏸️ Automatic email monitoring disabled (set AUTO_MONITOR_EMAILS=true to enable)")
    
    print("\n" + "="*60)
    print("📍 Available Endpoints:")
    print("="*60)
    print("GET    /health                      - Health check")
    print("GET    /api/transactions            - Get user transactions")
    print("GET    /api/budget                  - Get user budget")
    print("GET    /api/spending-by-category    - Get category breakdown")
    print("POST   /api/fetch-transactions      - Fetch from Gmail")
    print("POST   /api/update-budget           - Update budget")
    print("POST   /api/add-transaction         - Add manual transaction")
    print("DELETE /api/delete-transaction      - Delete a transaction")
    print("="*60 + "\n")
    
    env = os.getenv("ENVIRONMENT", "development")
    print(f"🌍 Environment: {env}")
    print(f"🔗 Server running on http://localhost:8000")
    print(f"📖 API Docs: http://localhost:8000/docs")
    print(f"📘 ReDoc: http://localhost:8000/redoc")
    print("\n" + "="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    global email_monitor_thread
    
    if email_monitor_thread:
        print("\n🛑 Stopping email monitoring...")
        from email_monitor import stop_monitoring
        stop_monitoring()
        print("✅ Email monitoring stopped")


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    global email_monitor_thread
    
    auto_monitor_enabled = os.getenv("AUTO_MONITOR_EMAILS", "true").lower() == "true"
    monitor_active = email_monitor_thread is not None and email_monitor_thread.is_alive()
    
    return {
        "status": "ok",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat(),
        "auto_monitor_enabled": auto_monitor_enabled,
        "monitor_active": monitor_active
    }


@app.post("/api/fetch-transactions", response_model=ApiResponse)
async def fetch_transactions(request: FetchTransactionsRequest):
    """
    Fetch transactions from Gmail and save to database
    
    Args:
        request: Contains user_id
    
    Returns:
        ApiResponse with success status and count of new transactions
    """
    try:
        print(f"\n📧 Fetching transactions for user: {request.user_id}")
        
        # Process all transactions
        result = process_all_transactions(request.user_id)
        
        return ApiResponse(
            success=result['success'],
            message=result['message'],
            count=result['total_new']
        )
        
    except Exception as e:
        print(f"❌ Error in fetch_transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/update-budget", response_model=ApiResponse)
async def update_budget_endpoint(request: UpdateBudgetRequest):
    """
    Update user's monthly budget
    
    Args:
        request: Contains user_id, income, budget, month
    
    Returns:
        ApiResponse with success status
    """
    try:
        # Validate month format (YYYY-MM)
        try:
            datetime.strptime(request.month, "%Y-%m")
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid month format. Use YYYY-MM (e.g., 2025-10)"
            )
        
        # Update budget in database
        success = update_budget(
            user_id=request.user_id,
            income=request.income,
            budget=request.budget,
            month=request.month
        )
        
        if success:
            return ApiResponse(
                success=True,
                message=f"Budget updated successfully for {request.month}"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update budget")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in update_budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transactions", response_model=ApiResponse)
async def get_transactions_endpoint(
    user_id: str = Query(..., description="User identifier"),
    month: str = Query(None, description="Filter by month (YYYY-MM)")
):
    """
    Get user's transactions, optionally filtered by month
    
    Args:
        user_id: User identifier
        month: Optional month filter (YYYY-MM)
    
    Returns:
        ApiResponse with transactions list and total_spent
    """
    try:
        # Fetch transactions
        if month:
            # Validate month format
            try:
                datetime.strptime(month, "%Y-%m")
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid month format. Use YYYY-MM (e.g., 2025-10)"
                )
            
            transactions = get_all_transactions_by_month(user_id, month)
        else:
            transactions = get_transactions(user_id, limit=100)
        
        # Calculate total spent
        total_spent = sum(t['amount'] for t in transactions)
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(transactions)} transactions",
            data={
                "transactions": transactions,
                "total_spent": total_spent
            },
            count=len(transactions)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/budget", response_model=ApiResponse)
async def get_budget_endpoint(
    user_id: str = Query(..., description="User identifier"),
    month: str = Query(..., description="Month in format YYYY-MM")
):
    """
    Get user's budget information for a specific month
    
    Args:
        user_id: User identifier
        month: Month in format YYYY-MM
    
    Returns:
        ApiResponse with budget details including remaining amount
    """
    try:
        # Validate month format
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid month format. Use YYYY-MM (e.g., 2025-10)"
            )
        
        # Get budget
        budget = get_budget(user_id, month)
        
        if not budget:
            raise HTTPException(
                status_code=404,
                detail=f"No budget found for user {user_id} in {month}"
            )
        
        # Get all transactions for the month
        transactions = get_all_transactions_by_month(user_id, month)
        total_spent = sum(t['amount'] for t in transactions)
        
        # Calculate remaining
        remaining = budget['budget'] - total_spent
        
        budget_response = BudgetResponse(
            income=budget['income'],
            budget=budget['budget'],
            total_spent=total_spent,
            remaining=remaining,
            month=month
        )
        
        return ApiResponse(
            success=True,
            message=f"Budget retrieved for {month}",
            data=budget_response.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/add-transaction", response_model=ApiResponse)
async def add_transaction_endpoint(request: AddTransactionRequest):
    """
    Add a manual transaction
    
    Args:
        request: Contains user_id, merchant, amount, category, date
    
    Returns:
        ApiResponse with transaction_id
    """
    try:
        # Validate category
        valid_categories = get_valid_categories()
        if request.category not in valid_categories:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        # Validate date format
        try:
            datetime.strptime(request.date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        # Insert transaction
        transaction_id = insert_transaction(
            user_id=request.user_id,
            merchant=request.merchant,
            amount=request.amount,
            category=request.category,
            date=request.date,
            email_subject=None
        )
        
        if transaction_id:
            return ApiResponse(
                success=True,
                message="Transaction added successfully",
                data={"transaction_id": transaction_id}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to add transaction")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in add_transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/spending-by-category")
async def get_spending_by_category(
    user_id: str = Query(..., description="User ID"),
    month: str = Query(..., description="Month in YYYY-MM format")
):
    """
    Get spending breakdown by category
    
    Args:
        user_id: User identifier
        month: Month in YYYY-MM format
    
    Returns:
        Dictionary with category spending data
    """
    try:
        # Validate month format
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid month format. Use YYYY-MM (e.g., 2025-01)"
            )
        
        # Get all transactions for the month
        all_transactions = get_all_transactions_by_month(user_id, month)
        
        # Calculate spending by category
        category_spending = {}
        valid_categories = get_valid_categories()
        
        # Initialize all categories with 0
        for category in valid_categories:
            category_spending[category] = 0.0
        
        # Sum up amounts by category
        for txn in all_transactions:
            category = txn.get('category', 'Unknown')
            amount = txn.get('amount', 0.0)
            
            if category in category_spending:
                category_spending[category] += amount
            else:
                category_spending['Unknown'] += amount
        
        # Calculate total spending
        total_spending = sum(category_spending.values())
        
        # Create response with percentages
        breakdown = []
        for category, amount in category_spending.items():
            if amount > 0:  # Only include categories with spending
                percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                breakdown.append({
                    "category": category,
                    "amount": round(amount, 2),
                    "percentage": round(percentage, 1)
                })
        
        # Sort by amount descending
        breakdown.sort(key=lambda x: x['amount'], reverse=True)
        
        return {
            "success": True,
            "data": {
                "breakdown": breakdown,
                "total": round(total_spending, 2),
                "month": month
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_spending_by_category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/delete-transaction", response_model=ApiResponse)
async def delete_transaction_endpoint(request: DeleteTransactionRequest):
    """
    Delete a transaction by ID
    
    Args:
        request: Contains user_id and transaction_id
    
    Returns:
        ApiResponse with success status
    """
    try:
        # Delete the transaction
        success = delete_transaction(request.transaction_id, request.user_id)
        
        if success:
            return ApiResponse(
                success=True,
                message="Transaction deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found or doesn't belong to this user"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in delete_transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    print(f"❌ Unhandled exception: {exc}")
    return {
        "success": False,
        "message": f"Internal server error: {str(exc)}",
        "data": None
    }


# ============================================================
# Split Transaction Endpoints
# ============================================================

@app.post("/api/create-split", response_model=ApiResponse)
async def create_split_endpoint(request: CreateSplitRequest):
    """
    Create or update a split for a transaction
    
    Split methods:
    - 'equal': Split equally among all participants
    - 'percentage': Split by percentage (must add up to 100%)
    - 'ratio': Split by ratio (e.g., 1:2:3)
    """
    try:
        # Validate split method
        valid_methods = ['equal', 'percentage', 'ratio']
        if request.split_method not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid split method. Must be one of: {', '.join(valid_methods)}"
            )
        
        # Convert participants to dict
        participants_dict = [p.model_dump() for p in request.participants]
        
        # Create or update split
        split_id = create_or_update_split(
            user_id=request.user_id,
            transaction_id=request.transaction_id,
            participants=participants_dict,
            split_method=request.split_method,
            notes=request.notes
        )
        
        if split_id:
            # Get the created/updated split
            split_data = get_split_by_transaction(request.user_id, request.transaction_id)
            
            return ApiResponse(
                success=True,
                message="Split created/updated successfully",
                data=split_data
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to create split")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error in create_split_endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/get-split", response_model=ApiResponse)
async def get_split_endpoint(request: GetSplitRequest):
    """
    Get split details for a transaction
    """
    try:
        split_data = get_split_by_transaction(request.user_id, request.transaction_id)
        
        if split_data:
            return ApiResponse(
                success=True,
                message="Split found",
                data=split_data
            )
        else:
            return ApiResponse(
                success=False,
                message="No split found for this transaction",
                data=None
            )
    
    except Exception as e:
        print(f"❌ Error in get_split_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/delete-split", response_model=ApiResponse)
async def delete_split_endpoint(request: DeleteSplitRequest):
    """
    Delete a split transaction
    """
    try:
        success = delete_split(request.user_id, request.transaction_id)
        
        if success:
            return ApiResponse(
                success=True,
                message="Split deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Split not found")
    
    except Exception as e:
        print(f"❌ Error in delete_split_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/splits/{user_id}")
async def get_all_splits_endpoint(user_id: str):
    """
    Get all splits for a user
    """
    try:
        splits = get_all_splits(user_id)
        
        return ApiResponse(
            success=True,
            message=f"Found {len(splits)} splits",
            data=splits,
            count=len(splits)
        )
    
    except Exception as e:
        print(f"❌ Error in get_all_splits_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
