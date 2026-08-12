from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router


app = FastAPI(
    title="Smart E-Commerce Platform",
    version="1.0.0",
    description="Smart E-Commerce Platform Backend"
)


# Authentication routes
app.include_router(auth_router)

# User routes
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "message": "Smart E-Commerce Platform API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }