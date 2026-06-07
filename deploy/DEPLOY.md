# Деплой PEcj11 в продакшен (VPS Timeweb / Ubuntu)

Проект состоит из **двух сервисов** на одном сервере:

| Сервис | Технология | Порт (внутри) | Назначение |
|--------|------------|---------------|------------|
| Сайт | Flask + gunicorn | 5000 | Кейсы, контакты, админка |
| API чата | FastAPI + uvicorn | 8000 | RAG / FAQ-ассистент |

Снаружи всё доступно через **nginx** на порту 80 (или 443 с SSL):

- `https://ВАШ_ДОМЕН/` — сайт
- `https://ВАШ_ДОМЕН/api/chat` — API чата (виджет на кейсе #3)

---

## Шаг 0. Подготовка на компьютере

1. Закоммитьте и запушьте проект в **свой** GitHub-репозиторий (не обязательно pcef9).
2. Убедитесь, что в репозитории есть:
   - `data/faiss_index.bin` и `data/faqs_metadata.npy` (индекс уже собран)
   - папки `backend/`, `templates/`, `static/`, `deploy/`

---

## Шаг 1. VPS Timeweb (тот же сервер, что и Telegram-бот)

1. Зайдите в [Timeweb Cloud](https://cloud.timeweb.com) → ваш VPS.
2. Скопируйте **IP-адрес** и пароль root (или используйте SSH-ключ).
3. Подключитесь с компьютера:

```bash
ssh root@IP_ВАШЕГО_VPS
```

4. Проверьте, что порты свободны (бот их обычно не занимает):

```bash
ss -tlnp | grep -E ':5000|:8000|:80'
```

Если `:5000` или `:8000` заняты — напишите, подберём другие порты.

5. (Если есть домен) В Timeweb: **Домены → DNS → A-запись** `@` и `www` → IP вашего VPS.

---

## Шаг 2. Автоматическая установка

```bash
cd /tmp
git clone https://github.com/Nvtrap/PEcj11.git
cd PEcj11
sudo bash deploy/setup-server.sh https://github.com/Nvtrap/PEcj11.git
```

Скрипт установит Python, nginx, venv, зависимости и systemd-службы.

---

## Шаг 3. Настройка .env на сервере

```bash
sudo nano /var/www/pefcj11/.env
```

Минимум:

```env
SECRET_KEY=длинная-случайная-строка
ADMIN_USERNAME=admin
ADMIN_PASSWORD=надёжный-пароль
OPENAI_API_KEY=sk-...
CHAT_API_URL=https://ВАШ_ДОМЕН/api
```

Перезапуск после правок:

```bash
sudo systemctl restart pefcj11-web pefcj11-chat
```

---

## Шаг 4. Nginx

```bash
sudo cp /var/www/pefcj11/deploy/nginx-pefcj11.conf /etc/nginx/sites-available/pefcj11
sudo nano /etc/nginx/sites-available/pefcj11   # замените ВАШ_ДОМЕН
sudo ln -sf /etc/nginx/sites-available/pefcj11 /etc/nginx/sites-enabled/
# НЕ удаляйте default и другие сайты (n8n)! Добавьте pefcj11 отдельным server_name или портом.
sudo nginx -t
sudo systemctl reload nginx
```

---

## Шаг 5. SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d ВАШ_ДОМЕН
```

После SSL обновите в `.env`:

```env
CHAT_API_URL=https://ВАШ_ДОМЕН/api
```

---

## Шаг 6. Проверка

```bash
curl -s http://127.0.0.1:5000/cases | head
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Расскажи о компании","top_k":3}'
```

В браузере:

- `https://ВАШ_ДОМЕН/cases/faq-assistant` — кейс #3 с кнопкой 💬

---

## Полезные команды

```bash
sudo systemctl status pefcj11-web pefcj11-chat
sudo journalctl -u pefcj11-chat -f
sudo journalctl -u pefcj11-web -f
```

Обновление после git push:

```bash
cd /var/www/pefcj11
sudo -u www-data git pull
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo systemctl restart pefcj11-web pefcj11-chat
```

---

## Схема

```
Браузер
   │
   ▼
nginx :80 / :443
   ├── /      → gunicorn :5000 → Flask (сайт)
   └── /api/  → uvicorn  :8000 → FastAPI (чат)
```

Виджет чата берёт URL из `CHAT_API_URL` (шаблон → `data-api-base` → `chat.js`).
