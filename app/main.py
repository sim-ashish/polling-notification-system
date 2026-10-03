from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import notifications, users


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Real-Time Notification System",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(notifications.router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }