import requests
import logging

from dataclasses import dataclass
from typing import Any
logger = logging.getLogger(__name__)


class OdooJsonRpcError(Exception):
    """Class for Odoo RPC errors"""
    pass


class OdooAuthError(OdooJsonRpcError):
    """Odoo authentication error"""
    pass


@dataclass(frozen=True)
class OdooConfig:
    """Class for Odoo configuration"""
    url: str
    db: str
    username: str
    password: str


class OdooJsonRpcClient:
    """Class for Odoo JsonRpc client"""
    def __init__(self, cfg: OdooConfig, timeout: int = 15) -> None:
        self.cfg = cfg
        self.timeout = timeout
        self.uid: int | None = None
        self.session = requests.Session()
        self.endpoint = f"{cfg.url.rstrip('/')}/jsonrpc"

    def _rpc_connection(self, service: str, method: str, args: tuple[Any, ...]) -> list[list[Any]]:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,  # Method to perform ex.: login
                "args": args  # args to perform a login ex.: (DB, USER, PASS)
            }
        }

        # Service -> 'common' utility for login
        req = self.session.post(self.endpoint, json=payload, timeout=self.timeout)
        req.raise_for_status()
        data = req.json()
        if "error" in data:
            logger.error(f"Odoo returned a error: {data['error']}")
            raise OdooJsonRpcError(f"Odoo returned a error: {data['error']}")

        return data.get("result")

    def odoo_login(self) -> int:
        uid = self._rpc_connection("common", "login", (self.cfg.db, self.cfg.username, self.cfg.password))
        if not uid:
            raise OdooAuthError("Invalid credentials (login returned falsy uid).")
        self.uid = int(uid)
        return self.uid

    def search_read(self, domain_search: list[list[Any]], limit: int = 0) -> list[dict]:
        if self.uid is None:
            self.odoo_login()

        fields = [
            "name",
            "is_company",
            "x_cliente_ativo",
            "country_id",
            "state_id",
            "create_date",
        ]
        domain = domain_search or []
        kwargs = {"fields": fields}
        if limit > 0:
            kwargs["limit"] = limit

        result_search = self._rpc_connection(
            service="object",
            method="execute_kw",
            args=(
                self.cfg.db,
                self.uid,
                self.cfg.password,
                "res.partner",
                "search_read",
                [domain],
                kwargs,
            ),
        )
        return result_search or []