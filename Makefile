VENV_ALEMBIC = .venv/bin/alembic
VENV_PIP = .venv/bin/pip
VENV_UVICORN = .venv/bin/uvicorn

include make/docker-bd.mk

.PHONY: help install migrate dev up down build rebuild logs ps clean deps-up deps-down

help:
	@echo "Доступные команды:"
	@echo "  make install   - Установка/обновление зависимостей из requirements.txt"
	@echo "  make dev       - Запуск FastAPI локально через Uvicorn (.venv)"
	@echo "  make migrate   - Применение миграций Alembic (.venv)"
	@echo "  --- Docker Compose (Полный стек) ---"
	@echo "  make up        - Запуск всего стека (Postgres, Redis, MinIO, API, Worker)"
	@echo "  make down      - Остановка всего стека"
	@echo "  make build     - Пересборка Docker-образов"
	@echo "  make rebuild   - Чистая пересборка Docker-образов без кэша"
	@echo "  make clean     - Полная очистка: остановка, удаление volumes и кэша Docker"
	@echo "  make logs      - Просмотр логов всех контейнеров"
	@echo "  make ps        - Статус запущенных контейнеров"
	@echo "  --- Только инфраструктура ---"
	@echo "  make deps-up   - Запуск только Postgres, Redis и MinIO"
	@echo "  make deps-down - Остановка только инфраструктурных сервисов"

install:
@if [ ! -d ".venv" ]; then \
		echo "Створення віртуального оточення..."; \
		python3 -m venv .venv; \
	fi
	$(VENV_PIP) install -r requirements.txt

dev:
	$(VENV_UVICORN) app.main:app --reload