from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv


# ============================================================
# FASTAPI PROJECT ROOT
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, BASE_DIR)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(os.path.join(BASE_DIR, ".env"))


# ============================================================
# IMPORT SQLALCHEMY BASE
# ============================================================

from app.core.database import Base


# ============================================================
# IMPORT FASTAPI MODELS
# ============================================================

from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.notification import Notification
from app.models.return_request import ReturnRequest
from app.models.refund import Refund


# ============================================================
# ALEMBIC CONFIGURATION
# ============================================================

config = context.config


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "fastapi")

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL
)


# ============================================================
# ALEMBIC LOGGING
# ============================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ============================================================
# ALEMBIC METADATA
# ============================================================

target_metadata = Base.metadata


# ============================================================
# DJANGO TABLES
#
# These tables belong to Django and MUST NOT be managed
# by FastAPI/Alembic.
# ============================================================

DJANGO_TABLES = {
    "django_migrations",
    "django_content_type",
    "django_admin_log",
    "django_session",

    "auth_user",
    "auth_group",
    "auth_permission",
    "auth_group_permissions",
    "auth_user_groups",
    "auth_user_user_permissions",

    "dashboard_product",
}


# ============================================================
# INCLUDE / EXCLUDE TABLES
# ============================================================

def include_object(
    object,
    name,
    type_,
    reflected,
    compare_to
):
    """
    Prevent Alembic from modifying Django tables.
    """

    if type_ == "table" and name in DJANGO_TABLES:
        return False

    return True


# ============================================================
# OFFLINE MIGRATIONS
# ============================================================

def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,

        literal_binds=True,

        dialect_opts={
            "paramstyle": "named"
        },

        compare_type=True,
        compare_server_default=True,

        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# ONLINE MIGRATIONS
# ============================================================

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),

        prefix="sqlalchemy.",

        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,

            compare_type=True,
            compare_server_default=True,

            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================
# RUN ALEMBIC
# ============================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()