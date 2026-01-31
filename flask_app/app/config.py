import os
from dataclasses import dataclass


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    odoo_url: str
    odoo_db: str
    odoo_user: str
    odoo_password: str
    log_level: str = "INFO"


def load_settings() -> Settings:
    odoo_url = os.getenv("ODOO_URL", "").rstrip("/")
    odoo_db = os.getenv("ODOO_DB", "")
    odoo_user = os.getenv("ODOO_USER", "")
    odoo_password = os.getenv("ODOO_PASSWORD", "")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    missing = []
    if not odoo_url: missing.append("ODOO_URL")
    if not odoo_db: missing.append("ODOO_DB")
    if not odoo_user: missing.append("ODOO_USER")
    if not odoo_password: missing.append("ODOO_PASSWORD")

    if missing:
        raise ConfigError(f"Missing environment variables: {', '.join(missing)}")

    return Settings(
        odoo_url=odoo_url,
        odoo_db=odoo_db,
        odoo_user=odoo_user,
        odoo_password=odoo_password,
        log_level=log_level,
    )
