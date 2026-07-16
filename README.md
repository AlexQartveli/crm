# KINETIKS — CRM + Склад

Готовый к запуску проект CRM и складского учёта для локальной работы и деплоя.

## Быстрый запуск (Windows)

1. Откройте папку `crm` на рабочем столе
2. Дважды кликните **`start.bat`**
3. Откроется:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Swagger: http://localhost:8000/docs

Нужно: **Node.js 20+** и **Python 3.12**.

### Альтернатива через Docker

```bat
start-docker.bat
```

или:

```bash
docker compose up --build
```

## Структура проекта

```
crm/
├── backend/      — FastAPI + SQLite
├── frontend/     — React + TypeScript + Vite
├── desktop/      — Windows-приложение (Electron)
├── scripts/      — сборка и локальный запуск
├── start.bat     — запуск всего проекта
└── start-docker.bat
```

## Сайт компании

https://kinetiks.online/

## Онлайн-пробник

https://alexqartveli.github.io/crm/

## Возможности

### CRM
- **Лиды** — входящие заявки с управлением статусами
- **Сделки** — воронка продаж (канбан-доска) с 6 стадиями
- **Контакты** — база контактных лиц с привязкой к компаниям
- **Компании** — карточки организаций с реквизитами
- **Дашборд** — сводная аналитика по CRM и складу

### Роли и доступы
- **admin** — полный доступ + управление пользователями
- **director** — всё, кроме пользователей и настроек RS.ge
- **sales** — CRM, сообщения, просмотр ботов
- **operator** — сообщения, лиды и контакты
- **warehouse** — товары, склад, движения
- **accountant** — бухгалтерия, RS.ge, просмотр контактов/компаний

Демо-логины: код компании **`demo`**, затем `admin` / `admin123`, `sales` / `sales123`, и т.д.

### Мультитенантность (несколько компаний)
- Каждая организация регистрируется отдельно и получает **изолированный кабинет**
- Данные CRM, склад, сообщения, боты и бухгалтерия **не пересекаются** между компаниями
- Вход: **код компании** + логин + пароль
- Регистрация: `/register` — создаёт компанию и администратора
- Личный кабинет: профиль, смена пароля, данные компании

### Роли и доступы
- **Товары** — каталог с артикулами, ценами и единицами измерения
- **Склады** — несколько складов с остатками
- **Остатки** — количество, резерв, доступно
- **Движения** — приход, расход, перемещение, корректировка

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Backend   | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend  | React, TypeScript, Tailwind CSS, Vite |
| API       | REST, OpenAPI (Swagger) |

## Деплой в интернет (с телефона)

### Шаг 1. Включите GitHub Pages (один раз)

1. Откройте **Settings → Pages** в репозитории
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / **/ (root)**
4. Save

### Шаг 2. Запустите деплой

После push в `main` GitHub Actions собирает и публикует фронтенд на ветку `gh-pages`.

Или вручную: **Actions → Deploy to GitHub Pages → Run workflow**

### Шаг 3. Подключите backend на Render (один раз)

1. Зайдите на [render.com](https://render.com) → войдите через GitHub
2. **New → Blueprint** → выберите репозиторий `AlexQartveli/crm`
3. Render подхватит `render.yaml` и задеплоит API

### Готово — открывайте с телефона

| Что | Адрес |
|-----|-------|
| **Kinetix (интерфейс)** | https://alexqartveli.github.io/crm/ |
| **API** | https://crm-ced4.onrender.com |
| **Swagger** | https://crm-ced4.onrender.com/docs |

> На бесплатном Render сервер «засыпает» после 15 мин бездействия. Первый запрос может занять ~30 сек.

## Быстрый старт (локально)

### Docker Compose

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### Локальный запуск

**Backend:**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Windows-приложение

Настольное приложение с встроенным backend (SQLite в `%APPDATA%\\Kinetix`).

### Сборка установщика (.exe)

```bat
build-windows.bat
```

Или в PowerShell:

```powershell
.\scripts\build-windows.ps1
```

Готовый установщик: `desktop\release\Kinetix CRM Setup *.exe`

### Запуск в режиме разработки

```bash
cd frontend && npm run build
cd ../desktop && npm install && npm start
```

> Для dev-режима нужен Python 3.12 в PATH. В собранном `.exe` Python не требуется.

## API

Все эндпоинты доступны по префиксу `/api`:

| Модуль | Эндпоинты |
|--------|-----------|
| CRM | `/api/crm/leads`, `/api/crm/deals`, `/api/crm/contacts`, `/api/crm/companies` |
| Склад | `/api/warehouse/products`, `/api/warehouse/warehouses`, `/api/warehouse/stocks`, `/api/warehouse/movements` |
| Аналитика | `/api/dashboard` |

При первом запуске база автоматически заполняется демо-данными.

## Архитектура

```
backend/
  app/
    models/      — SQLAlchemy модели (CRM + склад)
    schemas/     — Pydantic схемы
    routers/     — API маршруты
    services/    — бизнес-логика (складские операции)
    seed.py      — демо-данные

frontend/
  src/
    pages/       — страницы (дашборд, CRM, склад)
    components/  — UI компоненты
    api/         — HTTP клиент
```

## Лицензия

MIT
