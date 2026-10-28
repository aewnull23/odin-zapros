# О!дин запрос

Telegram-бот и Mini App для хакатона «О! Хакатон» (трек AI-агент для путешествий). Пользователь описывает поездку одним сообщением — AI (с опциональным **поиском в интернете**) извлекает параметры, **сам выставляет фильтры** (тип: отель/тур, звёзды, цена, расстояние, теги), backend ранжирует моковые отели и туры, Mini App показывает результаты и имитацию бронирования.

## Стек

- **Backend + bot:** Python 3.11+, FastAPI, aiogram 3
- **AI:** OpenAI (`gpt-4o-mini`) + rule-based fallback
- **Mini App:** React + Vite + `@twa-dev/sdk`
- **Интернет:** DuckDuckGo (`duckduckgo-search`) — краткий контекст для AI
- **Данные:** `data/hotels.json`, `data/tours.json`

## Быстрый старт (локально)

### 1. Backend

```bash
cd "C:\Users\user\Desktop\отель_пап"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Заполните `.env`:

| Переменная | Описание |
|------------|----------|
| `BOT_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) |
| `OPENAI_API_KEY` | Ключ OpenAI (можно пустым — сработает fallback) |
| `WEBAPP_URL` | URL Mini App (локально `http://localhost:5173`) |
| `CORS_ORIGINS` | `http://localhost:5173` |
| `VALIDATE_INIT_DATA` | `false` для теста WebApp в браузере вне Telegram |
| `ENABLE_WEB_SEARCH` | `true` — AI подтягивает сnippets из интернета перед парсингом |
| `WEB_SEARCH_MAX_RESULTS` | Число результатов поиска (по умолчанию 5) |

Запуск API и бота:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Mini App

```bash
cd webapp
copy .env.example .env
npm install
npm run dev
```

Откройте [http://localhost:5173](http://localhost:5173).

### 3. Telegram + HTTPS

Telegram WebApp требует HTTPS. Для разработки:

1. Поднимите туннель (ngrok / cloudflared) на порт **5173** (фронт) и при необходимости **8000** (API).
2. В BotFather: `/setdomain` → ваш HTTPS-домен фронта.
3. Обновите `WEBAPP_URL` и `CORS_ORIGINS` на публичные URL.
4. В `webapp/.env` задайте `VITE_API_URL` на публичный URL API.

## BotFather

1. `/newbot` — создать бота, скопировать токен в `BOT_TOKEN`.
2. `/setcommands` — команда `start` (бот также регистрирует её при старте).
3. Menu Button / Web App URL — указывается автоматически при старте (`WEBAPP_URL`).
4. Для production включите `VALIDATE_INIT_DATA=true` — подпись `initData` проверяется на API.

## Деплой (рекомендация)

| Часть | Сервис |
|-------|--------|
| API + bot | [Render](https://render.com) / Railway — `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |
| Mini App | Vercel / Cloudflare Pages — build `webapp`, env `VITE_API_URL` |

После деплоя обновите `WEBAPP_URL`, `CORS_ORIGINS` и домен в BotFather.

## Демо-сценарий для защиты

1. `/start` в боте → «Начать поиск» / Menu «Поиск отелей».
2. Сообщение: `Хочу в Питер на 2 дня в эти выходные, до 10 тысяч, рядом с Невским`.
3. Бот отвечает топ-3 и кнопкой Mini App.
4. В Mini App — карточки с `ai_reason`, фильтры, детали отеля.
5. «Забронировать» → alert «Успешно забронировано!» и ссылка на ostrovok.ru (демо).

## AI + интернет + фильтры

1. `analyze_travel_query` ([`src/ai/intent.py`](src/ai/intent.py)) — web-поиск → NLP (OpenAI или fallback) → [`SearchFilters`](src/api/schemas.py).
2. Фильтры применяются в [`search/engine.py`](src/search/engine.py) и [`search/tours.py`](src/search/tours.py).
3. Mini App получает `filters` и **предзаполняет** слайдеры; блок «Кратко из интернета» — поле `web_insight`.

Отключить интернет: `ENABLE_WEB_SEARCH=false` или `"use_web": false` в `POST /api/search`.

## API

- `GET /health`
- `POST /api/search` — `{ "query": "...", "init_data": "...", "use_web": true }`
- `GET /api/sessions/{id}`
- `GET /api/hotels/{id}`
- `POST /api/book/{id}`

## Ограничения прототипа

- Отели из JSON, не API Островка.
- Сессии in-memory (сброс при перезапуске сервера).
- Бюджет трактуется как сумма за всё проживание (`price_per_night × nights`).
