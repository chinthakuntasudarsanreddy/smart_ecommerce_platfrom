
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ============================================================
    # DATABASE
    # ============================================================

    database_url: str

    # ============================================================
    # OLD JWT SETTINGS
    # Keep these if other parts of the project still use them.
    # ============================================================

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ============================================================
    # AUTH0
    # ============================================================

    auth0_domain: str
    auth0_audience: str
    auth0_issuer: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()