#!/bin/bash
# Запуск на VPS (Ubuntu/Debian) от root или через sudo
set -euo pipefail

PROJECT_DIR="/var/www/pefcj11"
REPO_URL="${1:-}"

if [ -z "$REPO_URL" ]; then
  echo "Использование: sudo bash setup-server.sh https://github.com/USER/PEcj11.git"
  exit 1
fi

apt-get update
apt-get install -y python3 python3-venv python3-pip nginx git

mkdir -p "$PROJECT_DIR"
if [ ! -d "$PROJECT_DIR/.git" ]; then
  git clone "$REPO_URL" "$PROJECT_DIR"
else
  git -C "$PROJECT_DIR" pull
fi

cd "$PROJECT_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  cp deploy/env.example .env
  echo "Создан .env из шаблона — отредактируйте: nano $PROJECT_DIR/.env"
fi

if [ ! -f data/faiss_index.bin ]; then
  ./venv/bin/python -m backend.build_index
fi

mkdir -p database logs
chown -R www-data:www-data "$PROJECT_DIR"

cp deploy/pefcj11-web.service /etc/systemd/system/
cp deploy/pefcj11-chat.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pefcj11-web pefcj11-chat
systemctl restart pefcj11-web pefcj11-chat

echo "Готово. Настройте nginx (deploy/nginx-pefcj11.conf) и .env"
