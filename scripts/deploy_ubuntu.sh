#!/usr/bin/env bash
set -euo pipefail

# TripMate one-click deployment for Ubuntu 22.04/24.04
# Usage:
#   chmod +x scripts/deploy_ubuntu.sh
#   sudo bash scripts/deploy_ubuntu.sh

#######################################
# Editable variables
#######################################
APP_USER="${APP_USER:-ubuntu}"
APP_DIR="${APP_DIR:-/opt/trip_mate}"
REPO_URL="${REPO_URL:-https://github.com/yourname/trip_mate.git}"
BRANCH="${BRANCH:-main}"
DOMAIN="${DOMAIN:-_}" # use "_" for default nginx server

MYSQL_DB="${MYSQL_DB:-trip_mate}"
MYSQL_USER="${MYSQL_USER:-tripmate}"
MYSQL_PASS="${MYSQL_PASS:-ChangeMe_123456}"
MYSQL_ROOT_AUTH="${MYSQL_ROOT_AUTH:-socket}" # socket or password
MYSQL_ROOT_PASS="${MYSQL_ROOT_PASS:-}"

REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
JWT_SECRET="${JWT_SECRET:-please_change_to_long_random_string}"

APP_ENV="${APP_ENV:-prod}"
APP_PORT="${APP_PORT:-8000}"
WORKERS="${WORKERS:-2}"

#######################################
# Helpers
#######################################
run_mysql() {
  local sql="$1"
  if [[ "${MYSQL_ROOT_AUTH}" == "password" ]]; then
    mysql -uroot -p"${MYSQL_ROOT_PASS}" -e "${sql}"
  else
    sudo mysql -e "${sql}"
  fi
}

ensure_user_exists() {
  if ! id -u "${APP_USER}" >/dev/null 2>&1; then
    echo "User ${APP_USER} not found. Please create it first."
    exit 1
  fi
}

#######################################
# 1) System packages
#######################################
echo "==> Installing system dependencies"
apt update
apt install -y git curl wget vim ufw build-essential python3 python3-venv python3-pip nginx mysql-server redis-server
pip3 install poetry

#######################################
# 2) Basic security
#######################################
echo "==> Configuring firewall"
ufw allow 22 || true
ufw allow 80 || true
ufw allow 443 || true
ufw --force enable || true

#######################################
# 3) MySQL setup
#######################################
echo "==> Configuring MySQL database/user"
run_mysql "CREATE DATABASE IF NOT EXISTS ${MYSQL_DB} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
run_mysql "CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASS}';"
run_mysql "GRANT ALL PRIVILEGES ON ${MYSQL_DB}.* TO '${MYSQL_USER}'@'127.0.0.1';"
run_mysql "FLUSH PRIVILEGES;"
systemctl enable --now mysql

#######################################
# 4) Redis setup
#######################################
echo "==> Configuring Redis"
if ! rg -q "^bind 127\\.0\\.0\\.1" /etc/redis/redis.conf; then
  sed -i "s/^bind .*/bind 127.0.0.1 ::1/" /etc/redis/redis.conf
fi
if ! rg -q "^protected-mode yes" /etc/redis/redis.conf; then
  sed -i "s/^protected-mode .*/protected-mode yes/" /etc/redis/redis.conf
fi
systemctl enable --now redis-server
systemctl restart redis-server

#######################################
# 5) App code deploy
#######################################
echo "==> Deploying application code"
ensure_user_exists
mkdir -p "${APP_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

if [[ ! -d "${APP_DIR}/.git" ]]; then
  sudo -u "${APP_USER}" git clone -b "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
else
  sudo -u "${APP_USER}" bash -lc "cd '${APP_DIR}' && git fetch --all && git checkout '${BRANCH}' && git pull --ff-only origin '${BRANCH}'"
fi

sudo -u "${APP_USER}" bash -lc "
  cd '${APP_DIR}' && \
  poetry config virtualenvs.in-project true && \
  poetry install
"

#######################################
# 6) Environment file
#######################################
echo "==> Writing .env"
cat > "${APP_DIR}/.env" <<EOF
APP_NAME=TripMate Backend
APP_ENV=${APP_ENV}
MYSQL_DSN=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASS}@127.0.0.1:3306/${MYSQL_DB}
REDIS_URL=${REDIS_URL}
JWT_SECRET=${JWT_SECRET}
EOF
chown "${APP_USER}:${APP_USER}" "${APP_DIR}/.env"
chmod 600 "${APP_DIR}/.env"

#######################################
# 7) DB migrations
#######################################
echo "==> Running Alembic migrations"
sudo -u "${APP_USER}" bash -lc "cd '${APP_DIR}' && poetry run alembic upgrade head"

#######################################
# 8) Systemd service
#######################################
echo "==> Configuring systemd service"
cat > /etc/systemd/system/tripmate-api.service <<EOF
[Unit]
Description=TripMate FastAPI API
After=network.target

[Service]
User=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/.venv/bin
ExecStart=${APP_DIR}/.venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w ${WORKERS} -b 127.0.0.1:${APP_PORT}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now tripmate-api

#######################################
# 9) Nginx reverse proxy
#######################################
echo "==> Configuring nginx"
cat > /etc/nginx/sites-available/tripmate.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/tripmate.conf /etc/nginx/sites-enabled/tripmate.conf
nginx -t
systemctl reload nginx

#######################################
# 10) Final checks
#######################################
echo "==> Final checks"
systemctl status tripmate-api --no-pager || true
systemctl status nginx --no-pager || true
systemctl status mysql --no-pager || true
systemctl status redis-server --no-pager || true
curl -sS "http://127.0.0.1/api/v1/health" || true

echo ""
echo "Deployment completed."
echo "Swagger: http://<your_server_ip>/docs"
echo "Health:  http://<your_server_ip>/api/v1/health"
