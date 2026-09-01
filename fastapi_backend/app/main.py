
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# API ROUTES
# ============================================================

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.cart import router as cart_router
from app.api.checkout import router as checkout_router
from app.api.stripe_webhook import router as stripe_webhook_router
from app.api.orders import router as orders_router
from app.api.returns import router as returns_router

# ============================================================
# OTHER ROUTES
# ============================================================

from app.routes.payment import router as payment_router
from app.routes.notifications import router as notification_router
from app.routes.websocket import router as websocket_router
from app.routes.return_request import router as return_request_router
from app.routes.user import router as user_router

# ============================================================
# WEBSOCKET MANAGER
# ============================================================

from app.websocket.manager import manager


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Smart E-Commerce Platform",
    version="1.0.0",
    description="Smart E-Commerce Platform Backend"
)


# ============================================================
# CORS
# ============================================================

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


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(checkout_router)

app.include_router(payment_router)
app.include_router(stripe_webhook_router)

app.include_router(notification_router)
app.include_router(websocket_router)

app.include_router(user_router)

# Orders - only ONE orders router
app.include_router(orders_router)

# Return API
app.include_router(returns_router)

# Existing return-request routes
app.include_router(return_request_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Smart E-Commerce Platform API",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# NOTIFICATION WEBSOCKET
# ============================================================

@app.websocket("/ws/notifications/{user_id}")
async def notification_websocket(
    websocket: WebSocket,
    user_id: int
):

    await manager.connect(
        user_id,
        websocket
    )

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            user_id,
            websocket
        )
