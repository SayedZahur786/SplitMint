# SplitMint - Startup Scripts

## 🚀 Quick Start

Run these scripts from the **`SplitMint/scripts/`** directory or the **`SplitMint/`** root directory.

### Windows (Batch Files)

```bash
# Start Backend (FastAPI on port 8000)
.\scripts\start-backend.bat

# Start Frontend (Next.js on port 3000)
.\scripts\start-frontend.bat

# Start Email Monitor (Standalone)
.\scripts\start-monitor.bat
```

### Important Notes

1. **Working Directory**: Run from `C:\Users\itsre\OneDrive\Pictures\ML\SplitMint\SplitMint\`
2. **Backend**: Automatically changes to `backend/` folder
3. **Frontend**: Automatically changes to `splitmint/` folder
4. **Monitor**: Automatically changes to `backend/` folder

### Typical Development Workflow

**Terminal 1** - Backend:

```bash
cd C:\Users\itsre\OneDrive\Pictures\ML\SplitMint\SplitMint
.\scripts\start-backend.bat
```

**Terminal 2** - Frontend:

```bash
cd C:\Users\itsre\OneDrive\Pictures\ML\SplitMint\SplitMint
.\scripts\start-frontend.bat
```

**Terminal 3** - Email Monitor (Optional):

```bash
cd C:\Users\itsre\OneDrive\Pictures\ML\SplitMint\SplitMint
.\scripts\start-monitor.bat
```

### URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Troubleshooting

**Backend fails to start:**

- Check if port 8000 is available
- Ensure `.env` file exists in `backend/` folder
- Check `backend/requirements.txt` dependencies are installed

**Frontend fails to start:**

- Check if port 3000 is available
- Run `pnpm install` in `splitmint/` folder
- Ensure Node.js and pnpm are installed

**Monitor fails to start:**

- Check if `token.json` exists in `backend/` folder
- Verify Gmail OAuth is set up correctly
- Check `.env` has `AUTO_MONITOR_EMAILS=true`

---

## 📁 Script Details

### start-backend.bat

- Changes to `backend/` directory
- Runs `uvicorn main:app --reload`
- Auto-reloads on code changes
- Starts email monitor automatically (if enabled in .env)

### start-frontend.bat

- Changes to `splitmint/` directory
- Installs dependencies if `node_modules/` missing
- Runs `pnpm dev`
- Auto-reloads on code changes

### start-monitor.bat

- Changes to `backend/` directory
- Runs `email_monitor.py` standalone
- Checks emails every 45 seconds
- Use if you don't want to run full backend

---

Happy Coding! 🎉
