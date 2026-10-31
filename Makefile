VENV_ALEMBIC = .venv/bin/alembic
VENV_PIP = .venv/bin/pip
VENV_UVICORN = .venv/bin/uvicorn

include make/docker-bd.mk

.PHONY: help install migrate dev up down build rebuild logs ps clean deps-up deps-down

help:
	@echo "Доступные команды:"
	@echo "  make install   - Системные зависимости + venv + pip install -r requirements.txt"
	@echo "  make dev       - Запуск FastAPI локально через Uvicorn (.venv)"
	@echo "  --- Docker Compose (Полный стек) ---"
	@echo "  make up        - Запуск стека (Postgres, Redis, API, Worker)"
	@echo "  make down      - Остановка всего стека"
	@echo "  make build     - Пересборка Docker-образов"
	@echo "  make rebuild   - Чистая пересборка Docker-образов без кэша"
	@echo "  make clean     - Удаление Compose volumes и системная очистка Docker (включая volumes)"
	@echo "  make logs      - Просмотр логов всех контейнеров"
	@echo "  make ps        - Статус запущенных контейнеров"

install:
	@if ! command -v python3.12 >/dev/null 2>&1; then \
		echo "📦 Установка python3.12, python3.12-venv, python3-pip..."; \
		sudo apt-get update -y && sudo apt-get install -y python3.12 python3.12-venv python3-pip; \
	else \
		echo "✅ python3.12 уже установлен."; \
	fi
	@if [ ! -d ".venv" ]; then \
		echo "Створення віртуального оточення..."; \
		python3.12 -m venv .venv; \
	fi
	$(VENV_PIP) install --upgrade pip --quiet
	$(VENV_PIP) install -r requirements.txt

dev:
	$(VENV_UVICORN) app.main:app --reload
