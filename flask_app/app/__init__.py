import os
import logging
import sys
from flask import Flask, render_template

from .odoo_jsonrpc import OdooJsonRpcClient, OdooConfig, OdooJsonRpcError, OdooAuthError
from .config import load_settings, ConfigError
from .routes import bp

logger = logging.getLogger(__name__)


def setup_logging(level: str):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        stream=sys.stdout,  # Stream to work on docker with gunicorn
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,  # is necessary for use logging of python on gunicorn
    )


def create_app():
    try:
        settings = load_settings()
        setup_logging(settings.log_level)
    except ConfigError as e:
        setup_logging("INFO")
        raise

    app = Flask(__name__)
    app.config["SETTINGS"] = settings
    app.register_blueprint(bp)

    logging.getLogger(__name__).info(f"Flask app started (ODOO_URL={settings.odoo_url}, ODOO_DB={settings.odoo_db})")

    return app
