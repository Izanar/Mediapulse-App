# ⚡ MediaPulse App (Backend & Worker)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-Async%20Worker-green?style=for-the-badge&logo=celery)](https://docs.celeryq.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/MinIO-S3%20Storage-C71585?style=for-the-badge&logo=minio&logoColor=white)](https://min.io/)

</div>

> Исходный код бэкенд-сервиса **MediaPulse**: REST API на FastAPI, асинхронная очередь задач на Celery + Redis, обработка изображений через Pillow и хранение данных в PostgreSQL / S3.

---

## 🛠 Технологический стек

* **API Framework:** FastAPI (AsyncIO, Pydantic v2)
* **Background Tasks:** Celery + Redis 7
* **Database & ORM:** PostgreSQL 16 + SQLAlchemy 2.0 (asyncpg) + Alembic
* **Storage:** S3-compatible (MinIO)
* **Image Processing:** Pillow (PIL)

---

## 🚀 Локальный запуск проекта

### 1. Подготовка зависимостей

Следуйте этим шагам для полного запуска бэкенда, воркера и инфраструктуры в среде разработки.
Убедитесь, что у вас установлен Python 3.12, затем создайте и активируйте виртуальное окружение:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install

### 2. Запуск инфраструктуры (Docker Compose)
Поднимите необходимые сервисы (PostgreSQL, Redis, MinIO) в фоновом режиме:
make deps-up

### 3. Применение миграций базы данных
Выполните миграции через Alembic, чтобы развернуть актуальные таблицы в PostgreSQL:
make migrate

### 4. Запуск Celery Воркера (Асинхронная обработка)
В отдельном окне терминала (не забудьте активировать виртуальное окружение) запустите воркер для обработки изображений:
.venv/bin/celery -A app.worker.celery_app worker --loglevel=info

### 5. Запуск FastAPI сервера разработки
В основном терминале запустите сервер API:
make dev

📌 Основные эндпоинты API
POST /api/v1/auth/register — Регистрация нового пользователя.

POST /api/v1/auth/login — Аутентификация и получение JWT Access Token.

POST /api/v1/tasks/ — Загрузка медиафайла, сохранение оригинала в S3 и постановка задачи в очередь Celery.

GET /api/v1/tasks/{task_id} — Получение статуса, деталей задачи и ссылки на результат.