import logging
from flask import Blueprint, render_template, current_app

from .odoo_jsonrpc import OdooJsonRpcClient, OdooConfig, OdooAuthError, OdooJsonRpcError

logger = logging.getLogger(__name__)
bp = Blueprint("web", __name__)


@bp.get("/")
def index():
    settings = current_app.config["SETTINGS"]

    try:
        cfg = OdooConfig(
            url=settings.odoo_url,
            db=settings.odoo_db,
            username=settings.odoo_user,
            password=settings.odoo_password,
        )

        client = OdooJsonRpcClient(cfg)
        uid = client.odoo_login()

        # FIXME: REMOVE LIMIT, IT`S ONLY FOR DEBUG
        partners = client.search_read([["active", "=", True]], limit=25)

        return render_template(
            "index.html",
            uid=uid,
            partners=partners,
            error=None,
        )

    except OdooAuthError:
        logger.exception("Authentication error")
        return render_template("index.html", uid=None, partners=[], error="Invalid Odoo credentials (check .env).")

    except OdooJsonRpcError as e:
        logger.exception("Odoo JSON-RPC error")
        return render_template("index.html", uid=None, partners=[], error=f"Odoo JSON-RPC error: {e}")

    except Exception as e:
        logger.exception("Unexpected error")
        return render_template("index.html", uid=None, partners=[], error=f"Unexpected error: {e}")
