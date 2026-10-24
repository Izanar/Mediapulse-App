# ⚡ MediaPulse App (Backend & Worker)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-Async%20Worker-green?style=for-the-badge&logo=celery)](https://docs.celeryq.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Cloudflare R2](https://img.shields.io/badge/Cloudflare-R2-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://www.cloudflare.com/)
[![CI / CD](https://github.com/Izanar/Mediapulse-App/actions/workflows/ci.yml/badge.svg)](https://github.com/Izanar/Mediapulse-App/actions)

</div>

> Высоконагруженная отказоустойчивая микросервисная платформа для асинхронной обработки медиа-контента: REST API на FastAPI, распределенная очередь задач на Celery + Redis, хранение данных в PostgreSQL и объектном хранилище Cloudflare R2 (S3-compatible).

---

## 🛠 Технологический стек

* **API Framework:** FastAPI (AsyncIO, Pydantic v2)
* **Background Tasks:** Celery + Redis 7
* **Database & ORM:** PostgreSQL 16 + SQLAlchemy 2.0 (asyncpg) + Alembic
* **Cloud Storage:** Cloudflare R2 (S3-совместимый API, `boto3`)
* **Image Processing:** Pillow (PIL)
* **CI/CD:** GitHub Actions (автоматический линтинг, тестирование и публикация образов в GHCR)

В локальном Kind UI/API доступны по адресу `https://mediapulse.izanar.dev/`
через Cloudflare Tunnel; Argo CD и административные панели защищаются
Cloudflare Access.

---

## ⚙️ Конфигурация окружения (.env)

Перед запуском проекта скопируйте файл с примером конфигурации и укажите ваши параметры (включая доступы к Cloudflare R2):

```bash
cp -n .env.example .env
```

Для локального Kind также заполните `CLOUDFLARE_TUNNEL_TOKEN` в `.env`
значением connector token из Cloudflare Dashboard. Инфраструктурный bootstrap
перенесёт его в `~/.config/mediapulse/cloudflare/tunnel-token` с правами `0600`;
переменная не загружается в Vault/Kubernetes и не должна попадать в Git. Если
`.env` уже существует, не перезаписывайте его: добавьте туда строку
`CLOUDFLARE_TUNNEL_TOKEN=` из `.env.example` и заполните значение локально.