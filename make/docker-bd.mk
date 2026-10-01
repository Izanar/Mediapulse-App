.PHONY: deps-up deps-down migrate up down build rebuild logs ps clean

# --- Полный стек приложений (Standard Docker Compose) ---

up:
	@echo "🚀 Запуск полного стека MediaPulse..."
	docker compose up -d

down:
	@echo "🛑 Остановка полного стека..."
	docker compose down -v

build:
	@echo "🛠 Пересборка Docker-образов..."
	docker compose build

rebuild:
	@echo "🛠 Чистая пересборка Docker-образов без кэша..."
	docker compose build --no-cache

clean:
	@echo "🧹 Полная очистка системных ресурсов Docker..."
	docker compose down -v --remove-orphans
	docker system prune -a --volumes -f

logs:
	docker compose logs -f

ps:
	docker compose ps

# --- Локальная разработка (Только БД + Redis + MinIO) ---

deps-up:
	@echo "🔍 Проверка и очистка старых контейнеров..."
	@docker rm -f mediapulse-postgres mediapulse-redis mediapulse-minio mediapulse-createbuckets >/dev/null 2>&1 || true
	@echo "🚀 Запуск фоновых зависимостей (Postgres, Redis & MinIO)..."
	docker compose -f docker-compose.deps.yml up -d

deps-down:
	@echo "🛑 Остановка и удаление зависимостей..."
	docker compose -f docker-compose.deps.yml down -v