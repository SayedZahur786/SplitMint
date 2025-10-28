# SplitMint Backend - FastAPI Expense Tracker

A complete expense tracking backend built with FastAPI, integrating Gmail API for automatic transaction detection and Gemini AI for intelligent categorization.

## 🚀 Features

- **Gmail Integration**: Automatically fetch and parse transaction emails
- **AI Categorization**: Use Google Gemini AI to categorize merchants
- **MongoDB Database**: Store transactions and budgets
- **RESTful API**: Complete FastAPI backend with automatic documentation
- **Transaction Management**: Add, view, and manage expenses
- **Budget Tracking**: Set monthly budgets and track spending
- **Demo Data**: Load sample transactions for testing

## 📋 Prerequisites

- Python 3.8+
- MongoDB (local or MongoDB Atlas)
- Google Gmail API credentials (`zyura_secret.json`)
- Google Gemini API key

## 🛠️ Installation

### 1. Clone and Setup

```powershell
# Navigate to project directory
cd C:\Users\itsre\OneDrive\Pictures\ML\SplitMint

# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/splitmint

# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Environment
ENVIRONMENT=development
```

**Note**: Replace the values with your actual credentials.

### 4. Setup Gmail API

- Ensure `zyura_secret.json` is in the project root
- First run will open browser for OAuth authentication
- Token will be saved to `token.json` for future use

## 🏃 Running the Application

### Start the FastAPI Server

```powershell
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Health Check

```
GET /health
```

Returns server status and environment info.

### Fetch Transactions from Gmail

```
POST /api/fetch-transactions
Body: {"user_id": "your_user_id"}
```

Fetches transaction emails from Gmail, parses them, categorizes, and saves to database.

### Get Transactions

```
GET /api/transactions?user_id=your_user_id&month=2025-10
```

Retrieves user transactions, optionally filtered by month.

### Update Budget

```
POST /api/update-budget
Body: {
  "user_id": "your_user_id",
  "income": 50000,
  "budget": 30000,
  "month": "2025-10"
}
```

Sets monthly income and budget limit.

### Get Budget

```
GET /api/budget?user_id=your_user_id&month=2025-10
```

Returns budget info including total spent and remaining amount.

### Add Manual Transaction

```
POST /api/add-transaction
Body: {
  "user_id": "your_user_id",
  "merchant": "Starbucks",
  "amount": 250,
  "category": "Food & Dining",
  "date": "2025-10-28"
}
```

Manually add a transaction.

### Load Demo Data

```
POST /api/load-demo-data
Body: {
  "user_id": "your_user_id",
  "month": "2025-10"
}
```

Loads 10 sample transactions for testing.

## 🧪 Testing

Run the test suite:

```powershell
python test.py
```

This tests:

- MongoDB connection
- Transaction parsing
- Merchant categorization
- Database operations
- API endpoints (if server is running)

## 📂 Project Structure

```
SplitMint/
├── main.py                    # FastAPI server and endpoints
├── db.py                      # MongoDB database operations
├── models.py                  # Pydantic data models
├── email_service.py           # Gmail API integration
├── parser.py                  # Transaction parsing from emails
├── categorizer.py             # AI categorization with Gemini
├── process_transactions.py    # Main processing pipeline
├── test.py                    # Test suite
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── zyura_secret.json          # Gmail OAuth credentials
└── token.json                 # Gmail OAuth token (auto-generated)
```

## 📊 Transaction Categories

- Food & Dining
- Shopping & E-commerce
- Entertainment
- Bills & Utilities
- Transport
- Healthcare
- Education
- Others

## 🔐 Security Notes

- **Never commit** `.env` or `token.json` to version control
- Keep `zyura_secret.json` secure
- Use environment variables for all secrets
- In production, restrict CORS origins

## 🐛 Troubleshooting

### MongoDB Connection Issues

- Verify `MONGODB_URI` in `.env`
- Check network connectivity
- Ensure IP is whitelisted in MongoDB Atlas

### Gmail API Issues

- Ensure `zyura_secret.json` exists
- Check OAuth consent screen configuration
- Verify redirect URIs match

### Import Errors

```powershell
# Make sure packages are installed
pip install -r requirements.txt

# Verify Python interpreter
python --version
```

## 💡 Quick Start Example

```powershell
# 1. Start server
uvicorn main:app --reload

# 2. In another terminal, test with demo data
curl -X POST http://localhost:8000/api/load-demo-data \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "month": "2025-10"}'

# 3. View transactions
curl http://localhost:8000/api/transactions?user_id=demo_user

# 4. Set budget
curl -X POST http://localhost:8000/api/update-budget \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "income": 50000, "budget": 30000, "month": "2025-10"}'

# 5. Check budget
curl http://localhost:8000/api/budget?user_id=demo_user&month=2025-10
```

## 🚀 Next Steps

1. Connect frontend (Next.js app in `splitmint/` folder)
2. Add user authentication
3. Implement data visualization
4. Add expense analytics and insights
5. Deploy to production (Vercel, Railway, etc.)

## 📝 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

Built with ❤️ using FastAPI, MongoDB, Gmail API, and Gemini AI
