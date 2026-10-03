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

# Phase 2 Features and Phase 1 Limitations
### Phase 1 Limitation
- In the short polling the Browser is requesting after every 5 seconds
- This can lead the load on server during high traffic
- There is another Problem with this i.e the 4 second delay when notification arrives immediately after a pill
### What we'll change in Phase 2
- Instead of :
```text
Browser → "Anything new?"
Server  → "No."

5 seconds later

Browser → "Anything new?"
Server  → "No."

5 seconds later

Browser → "Anything new?"
Server  → "YES!"
```
- We'll do:
```text
Browser → "Anything new?"
Server  → "No."

5 seconds later

Browser → "Anything new?"
Server  → "No."

5 seconds later

Browser → "Anything new?"
Server  → "YES!"
```
- The server holds the HTTP request open until either 
- 1. A notification arrives, or 
- 2. A timeout occurs

# Phase 2 Architecture:
```text
                         ┌──────────────┐
                         │   Browser    │
                         └──────┬───────┘
                                │
                         Long Poll Request
                                │
                                ↓
                         ┌──────────────┐
                         │   FastAPI    │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    ↓                       ↓
             PostgreSQL             Long Poll Manager
                    │                       │
                    │                       │
                    └───────────┬───────────┘
                                │
                         Notification
                                │
                                ↓
                             Browser
                                │
                           🔔 +1 + Shake
```
