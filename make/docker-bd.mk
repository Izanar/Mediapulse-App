.PHONY: deps-up deps-down migrate dev

deps-up:
	@echo "🔍 Проверка и очистка старых контейнеров..."
	@docker rm -f mediapulse-postgres mediapulse-redis >/dev/null 2>&1 || true
	@echo "🚀 Запуск фоновых зависимостей (Postgres & Redis)..."
	docker compose -f docker-compose.deps.yml up -d

deps-down:
	@echo "🛑 Остановка и удаление зависимостей..."
	docker compose -f docker-compose.deps.yml down

migrate:
	$(VENV_ALEMBIC) upgrade head

dev:
	$(VENV_UVICORN) app.main:app --reload