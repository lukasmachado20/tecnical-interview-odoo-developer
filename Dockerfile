FROM odoo:14.0

USER root
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-build-isolation --no-cache-dir -r /tmp/requirements.txt
USER odoo
