# Makefile

VENV_ALEMBIC = .venv/bin/alembic
VENV_PIP = .venv/bin/pip
VENV_UVICORN = .venv/bin/uvicorn

include make/docker-bd.mk

.PHONY: help install migrate dev

help:
	@echo "Доступні команди:"
	@echo "  make install   - Встановлення/оновлення залежностей з requirements.txt"
	@echo "  make deps-up   - Запуск Postgres та Redis"
	@echo "  make deps-down - Зупинка Postgres та Redis"
	@echo "  make migrate   - Застосування миграцій Alembic"
	@echo "  make dev       - Запуск веб-сервера (Uvicorn)"

install:
	$(VENV_PIP) install -r requirements.txt

dev:
	$(VENV_UVICORN) app.main:app --reload
