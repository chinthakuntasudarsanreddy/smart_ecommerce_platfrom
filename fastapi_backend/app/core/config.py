import os
from pathlib import Path
from dotenv import load_dotenv

# fastapi_backend folder
BASE_DIR = Path(__file__).resolve().parents[2]

# Load fastapi_backend/.env
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)


class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "fastapi")

    database_url = (
        f"mysql+pymysql://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    secret_key: str = os.getenv(
        "SECRET_KEY",
        "change-this-secret-key"
    )

    algorithm: str = os.getenv(
        "ALGORITHM",
        "HS256"
    )

    access_token_expire_minutes: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "30"
        )
    )

    auth0_domain: str = os.getenv(
        "AUTH0_DOMAIN",
        ""
    )

    auth0_audience: str = os.getenv(
        "AUTH0_AUDIENCE",
        ""
    )

    auth0_issuer: str = os.getenv(
        "AUTH0_ISSUER",
        ""
    )

    internal_admin_api_key: str = os.getenv(
        "INTERNAL_ADMIN_API_KEY",
        ""
    )


settings = Settings()