# Восстановление nginx и n8n (если слетело после деплоя PEcj11)

Причина: конфиг `pefcj11` перехватил порт 80 и/или была удалена ссылка `default`, где жил n8n.

## 1. Быстро вернуть n8n (отключить PEcj11 в nginx)

```bash
rm -f /etc/nginx/sites-enabled/pefcj11
ls /etc/nginx/sites-available/
```

Посмотрите список — найдите конфиг n8n (`n8n`, `default`, домен и т.п.).

```bash
ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
# или, если n8n был в отдельном файле:
# ln -sf /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/n8n

nginx -t
systemctl reload nginx
```

Проверьте n8n в браузере.

## 2. Проверить, что n8n-сервис жив

```bash
systemctl status n8n
docker ps
```

Если n8n в Docker остановлен:

```bash
docker ps -a | grep n8n
docker start ИМЯ_КОНТЕЙНЕРА
```

## 3. PEcj11 оставить на отдельном порту (не ломая n8n)

Сайт и API можно открыть **напрямую по портам** (временно или постоянно):

- Сайт: `http://IP:5000`
- API: `http://IP:8000/health`

В `.env`:

```env
CHAT_API_URL=http://IP:8000
```

Откройте в Timeweb firewall порты 5000 и 8000 (если закрыты).

## 4. Правильный вариант — разные домены в nginx

Пример (два server-блока):

- `n8n.ваш-домен.ru` → n8n (как было)
- `site.ваш-домен.ru` → PEcj11 (Flask + /api/)

Не удаляйте `sites-enabled/default` и не перезаписывайте единственный конфиг на IP.
