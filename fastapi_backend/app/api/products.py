from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# GET /products
@router.get("/", response_model=list[ProductResponse])
def get_products(
    category: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_popularity: int | None = None,
    in_stock: bool | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_popularity is not None:
        query = query.filter(
            Product.popularity >= min_popularity
        )

    if in_stock is True:
        query = query.filter(Product.stock > 0)

    if in_stock is False:
        query = query.filter(Product.stock == 0)

    return query.all()


# GET /products/{id}
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# GET /products/category/{category}
@router.get(
    "/category/{category}",
    response_model=list[ProductResponse]
)
def get_products_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    return db.query(Product).filter(
        Product.category == category
    ).all()


# POST /products
@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        category=product_data.category,
        price=product_data.price,
        stock=product_data.stock,
        popularity=product_data.popularity,
        image_url=product_data.image_url
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product