# polling-notification-system
This Repository Contains the Notification System Using Polling

# Project Startup Commands
```bash
pip install requirements.txt
uvicorn app.main:app --reload
```
```bash
cd frontend
python -m http.server 5500
```

# Phase 1 Project Architecture
```text
                      ┌───────────────┐
                      │   Browser     │
                      │               │
                      │ 🔔 0          │
                      └───────┬───────┘
                              │
                              │ Every 5 seconds
                              │
                              │ GET /notifications/
                              │     unread-count
                              ↓
                      ┌───────────────┐
                      │    FastAPI    │
                      │               │
                      │ Notification  │
                      │ Router        │
                      └───────┬───────┘
                              │
                              ↓
                      ┌───────────────┐
                      │ Notification  │
                      │   Service     │
                      └───────┬───────┘
                              │
                              ↓
                      ┌───────────────┐
                      │  PostgreSQL   │
                      │               │
                      │ notifications │
                      └───────────────┘
```