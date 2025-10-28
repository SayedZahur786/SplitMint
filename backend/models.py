"""
Pydantic Data Models for Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FetchTransactionsRequest(BaseModel):
    """Request body for /api/fetch-transactions"""
    user_id: str = Field(..., description="User identifier")


class UpdateBudgetRequest(BaseModel):
    """Request body for /api/update-budget"""
    user_id: str = Field(..., description="User identifier")
    income: float = Field(..., gt=0, description="Monthly income (must be > 0)")
    budget: float = Field(..., gt=0, description="Monthly budget limit (must be > 0)")
    month: str = Field(..., description="Month in format YYYY-MM (e.g., 2025-10)")


class TransactionResponse(BaseModel):
    """Response model for a single transaction"""
    _id: str
    user_id: str
    merchant: str
    amount: float
    category: str
    date: str
    email_subject: Optional[str] = None
    created_at: str


class BudgetResponse(BaseModel):
    """Response model for budget information"""
    income: float
    budget: float
    total_spent: float
    remaining: float
    month: str


class AddTransactionRequest(BaseModel):
    """Request body for /api/add-transaction"""
    user_id: str = Field(..., description="User identifier")
    merchant: str = Field(..., description="Merchant/store name")
    amount: float = Field(..., gt=0, description="Transaction amount (must be > 0)")
    category: str = Field(..., description="Transaction category")
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")


class DeleteTransactionRequest(BaseModel):
    """Request body for /api/delete-transaction"""
    user_id: str = Field(..., description="User identifier")
    transaction_id: str = Field(..., description="Transaction ID to delete")


class DemoDataRequest(BaseModel):
    """Request body for /api/load-demo-data"""
    user_id: str = Field(..., description="User identifier")
    month: str = Field(..., description="Month in format YYYY-MM (e.g., 2025-10)")


class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    count: Optional[int] = None


# ============================================================
# Split Transaction Models
# ============================================================

class SplitParticipant(BaseModel):
    """Model for a participant in a split transaction"""
    name: str = Field(..., description="Participant name")
    phone_number: Optional[str] = Field(None, description="Phone number for payment reminders")
    share_percentage: Optional[float] = Field(None, ge=0, le=100, description="Share as percentage (0-100)")
    share_ratio: Optional[int] = Field(None, ge=1, description="Share as ratio (e.g., 1, 2, 3)")
    amount_paid: float = Field(default=0.0, ge=0, description="Amount this person paid")
    amount_owed: float = Field(default=0.0, description="Amount this person owes (calculated)")


class CreateSplitRequest(BaseModel):
    """Request body for creating/updating a split transaction"""
    user_id: str = Field(..., description="User identifier")
    transaction_id: str = Field(..., description="Original transaction ID")
    participants: List[SplitParticipant] = Field(..., min_items=2, description="List of participants (min 2)")
    split_method: str = Field(..., description="Split method: 'equal', 'percentage', or 'ratio'")
    notes: Optional[str] = Field(None, description="Optional notes about the split")


class GetSplitRequest(BaseModel):
    """Request body for getting split details"""
    user_id: str = Field(..., description="User identifier")
    transaction_id: str = Field(..., description="Transaction ID")


class DeleteSplitRequest(BaseModel):
    """Request body for deleting a split"""
    user_id: str = Field(..., description="User identifier")
    transaction_id: str = Field(..., description="Transaction ID")


class SplitResponse(BaseModel):
    """Response model for split transaction"""
    transaction_id: str
    merchant: str
    total_amount: float
    category: str
    date: str
    split_method: str
    participants: List[Dict[str, Any]]
    notes: Optional[str] = None
    created_at: str
    updated_at: str
