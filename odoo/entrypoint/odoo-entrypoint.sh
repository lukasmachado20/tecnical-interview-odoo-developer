#!/usr/bin/env bash
# Entrypoint to start Odoo 14 with pt_BR lang and contact module installed.
# Author: Lukas S. Machado

set -euo pipefail

echo "[entrypoint] Starting Odoo entrypoint"

# Fix permissions for odoo local bind mounted
echo "[entrypoint] Fixing permissions for /var/lib/odoo ..."
mkdir -p /var/lib/odoo/.local/share/Odoo
chown -R odoo:odoo /var/lib/odoo || true

echo "[entrypoint] Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT} ..."

gosu odoo python3 -u <<'EOF'
import os, time
import psycopg2

host = os.environ["DB_HOST"]
port = int(os.environ["DB_PORT"])
user = os.environ["DB_USER"]
pwd  = os.environ["DB_PASSWORD"]

for attempt in range(60):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname="postgres").close()
        print("[entrypoint] PostgreSQL is available.")
        break
    except Exception:
        if attempt == 59:
            raise
        time.sleep(1)
EOF

echo "[entrypoint] Determining whether bootstrap is needed for DB=${DB_NAME} ..."

set +e
gosu odoo python3 -u <<'EOF'
import os
import psycopg2
import sys

DB_NAME = os.environ["DB_NAME"]

def pg_connect(dbname):
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dbname=dbname,
    )

# 1) Does DB exist?
conn = pg_connect("postgres")
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_NAME,))
db_exists = cur.fetchone() is not None
cur.close()
conn.close()

if not db_exists:
    print("[entrypoint] Database does not exist -> bootstrap required.")
    sys.exit(42)

# 2) If DB exists, verify contacts + pt_BR
try:
    conn = pg_connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT state FROM ir_module_module WHERE name='contacts'")
    row = cur.fetchone()
    contacts_state = row[0] if row else None

    cur.execute("SELECT active FROM res_lang WHERE code='pt_BR'")
    row = cur.fetchone()
    ptbr_active = bool(row[0]) if row else False

    cur.close()
    conn.close()

    print(f"[entrypoint] Found DB. contacts_state={contacts_state}, pt_BR_active={ptbr_active}")

    if contacts_state != "installed" or not ptbr_active:
        print("[entrypoint] Bootstrap incomplete -> bootstrap required.")
        sys.exit(42)

    print("[entrypoint] Bootstrap already applied -> skipping.")
    sys.exit(0)

except psycopg2.Error as e:
    # Covers "relation does not exist" etc (schema not initialized yet)
    print(f"[entrypoint] DB exists but schema/bootstrap markers unavailable -> bootstrap required. ({e})")
    sys.exit(42)
EOF
NEED_BOOTSTRAP=$?
set -e

if [ "$NEED_BOOTSTRAP" -eq 42 ]; then
  echo "[entrypoint] Running bootstrap (install contacts, load pt_BR)..."
  gosu odoo odoo \
    --db_host="${DB_HOST}" \
    --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" \
    --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" \
    -i contacts,paycon_res_partner_custom \
    --without-demo=all \
    --load-language=pt_BR \
    --stop-after-init
  echo "[entrypoint] Bootstrap finished."
else
  echo "[entrypoint] Bootstrap not needed."
fi

echo "[entrypoint] Starting Odoo server..."
exec gosu odoo odoo \
  --db_host="${DB_HOST}" \
  --db_port="${DB_PORT}" \
  --db_user="${DB_USER}" \
  --db_password="${DB_PASSWORD}" \
  --database="${DB_NAME}" \
  --db-filter="${DB_FILTER}"
