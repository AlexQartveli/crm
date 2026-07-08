# Как открыть Kinetix с телефона

## Адрес

### https://alexqartveli.github.io/crm/

---

## Если не открывается

### 1. Включите GitHub Pages

1. Откройте: **https://github.com/AlexQartveli/crm/settings/pages**
2. **Source:** Deploy from a branch
3. **Branch:** `gh-pages` → `/ (root)`
4. **Save**

### 2. Подключите backend на Render

1. **https://render.com** → войти через GitHub
2. **New → Blueprint** → репозиторий `AlexQartveli/crm`
3. **Apply**

API: https://crm-ced4.onrender.com

> Первый запрос после простоя может идти ~30 секунд.

### Render вручную (без Blueprint)

1. **New → Web Service → Public Git Repository**
2. URL: `https://github.com/AlexQartveli/crm`
3. Настройки:

| Поле | Значение |
|------|----------|
| Name | `kinetix-api` |
| Language | **Python 3** |
| Branch | `main` |
| Root Directory | `backend` |
| Build Command | `pip install --upgrade pip && pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. **Environment** → добавьте переменную:
   - `PYTHON_VERSION` = `3.12.10`

5. **Health Check Path** — опционально, в разделе **Advanced** после создания сервиса:
   - `/api/health`
   - Если поля нет — пропустите, сервис всё равно запустится.

> Важно: не используйте Python 3.14 — сборка упадёт на Rust-зависимостях.

---

## Создать отдельный репозиторий `kinetix`

```bash
git clone https://github.com/AlexQartveli/crm.git kinetix
cd kinetix
gh repo create kinetix --public --source=. --push
```

Потом в **Settings → Pages** включите ветку `gh-pages`.

Адрес: **https://alexqartveli.github.io/kinetix/**
