
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import (
    CartAddRequest,
    CartUpdateRequest,
    CartRemoveRequest,
    CartResponse,
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


# ============================================================
# GET OR CREATE CART
# ============================================================

def get_or_create_cart(user_id: int, db: Session):
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == user_id)
        .first()
    )

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


# ============================================================
# BUILD CART RESPONSE
# ============================================================

def build_cart_response(cart: Cart):

    items = []
    cart_total = Decimal("0.00")

    for item in cart.items:

        item_total = (
            Decimal(str(item.product.price))
            * item.quantity
        )

        cart_total += item_total

        items.append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "item_total": item_total,
        })

    tax = cart_total * Decimal("0.18")
    grand_total = cart_total + tax

    return {
        "items": items,
        "cart_total": cart_total,
        "tax": tax,
        "grand_total": grand_total,
    }


# ============================================================
# GET CART
# GET /cart/
# ============================================================

@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    cart = get_or_create_cart(
        current_user.id,
        db,
    )

    return build_cart_response(cart)


# ============================================================
# ADD TO CART
# POST /cart/add
# ============================================================

@router.post("/add", response_model=CartResponse)
def add_to_cart(
    request: CartAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0",
        )

    product = (
        db.query(Product)
        .filter(Product.id == request.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if product.stock < request.quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock",
        )

    cart = get_or_create_cart(
        current_user.id,
        db,
    )

    item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == request.product_id,
        )
        .first()
    )

    if item:

        new_quantity = item.quantity + request.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock",
            )

        item.quantity = new_quantity

    else:

        item = CartItem(
            cart_id=cart.id,
            product_id=request.product_id,
            quantity=request.quantity,
        )

        db.add(item)

    db.commit()
    db.refresh(cart)

    return build_cart_response(cart)


# ============================================================
# UPDATE CART
# PUT /cart/update
# ============================================================

@router.put("/update", response_model=CartResponse)
def update_cart(
    request: CartUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0",
        )

    cart = get_or_create_cart(
        current_user.id,
        db,
    )

    item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == request.product_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product is not in cart",
        )

    if request.quantity > item.product.stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock",
        )

    item.quantity = request.quantity

    db.commit()
    db.refresh(cart)

    return build_cart_response(cart)


# ============================================================
# REMOVE FROM CART
# DELETE /cart/remove
# ============================================================

@router.delete("/remove", response_model=CartResponse)
def remove_from_cart(
    request: CartRemoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    cart = get_or_create_cart(
        current_user.id,
        db,
    )

    item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == request.product_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product is not in cart",
        )

    db.delete(item)
    db.commit()
    db.refresh(cart)

    return build_cart_response(cart)