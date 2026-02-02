FROM odoo:14.0

USER root

# Fix Debian buster EOL repositories + install gosu for use on odoo-entrypoint.sh
RUN set -eux; \
    sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list; \
    sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list; \
    sed -i '/buster-updates/d' /etc/apt/sources.list; \
    printf 'Acquire::Check-Valid-Until "false";\nAcquire::AllowInsecureRepositories "true";\nAcquire::AllowDowngradeToInsecureRepositories "true";\n' > /etc/apt/apt.conf.d/99no-check-valid; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get install -y --no-install-recommends gosu; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-build-isolation --no-cache-dir -r /tmp/requirements.txt
