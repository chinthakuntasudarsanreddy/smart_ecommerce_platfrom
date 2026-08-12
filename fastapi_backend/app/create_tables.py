from app.core.database import Base
from app.core.database import engine

from app.models import User
from app.models import Product
from app.models import Cart


print("Creating database tables...")


Base.metadata.create_all(
    bind=engine
)


print("Database tables created successfully!")