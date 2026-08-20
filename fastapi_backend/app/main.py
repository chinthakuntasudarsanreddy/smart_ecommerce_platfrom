from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.cart import router as cart_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.checkout import router as checkout_router
from app.routes.payment import router as payment_router
from app.api.stripe_webhook import router as stripe_webhook_router
app = FastAPI(
    title="Smart E-Commerce Platform",
    version="1.0.0",
    description="Smart E-Commerce Platform Backend"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(payment_router)
app.include_router(stripe_webhook_router)

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