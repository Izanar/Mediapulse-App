VENV_ALEMBIC = .venv/bin/alembic
VENV_PIP = .venv/bin/pip
VENV_UVICORN = .venv/bin/uvicorn

include make/docker-bd.mk

.PHONY: help install migrate dev up down build rebuild logs ps clean deps-up deps-down

help:
	@echo "Доступные команды приложения:"
	@echo "  make install   - Установка зависимостей из requirements.txt в виртуальное окружение"
	@echo "  make dev       - Запуск FastAPI локально через Uvicorn"
	@echo "  --- Docker Compose (Локальный запуск) ---"
	@echo "  make up        - Запуск полного стека (Postgres, Redis, API, Worker)"
	@echo "  make down      - Остановка полного стека"
	@echo "  make build     - Пересборка Docker-образов"
	@echo "  make rebuild   - Чистая пересборка без кэша"
	@echo "  make clean     - Полная очистка Docker-ресурсов"
	@echo "  make logs      - Просмотр логов"
	@echo "  make ps        - Статус контейнеров"
	@echo "  --- Инфраструктура (только базы и кэш) ---"
	@echo "  make deps-up   - Запуск только Postgres и Redis"
	@echo "  make deps-down - Остановка инфраструктурных сервисов"

install:
	@if [ ! -d ".venv" ]; then \
		echo "Создание виртуального окружения..."; \
		python3 -m venv .venv; \
	fi
	$(VENV_PIP) install -r requirements.txt

dev:
	$(VENV_UVICORN) app.main:app --reload
