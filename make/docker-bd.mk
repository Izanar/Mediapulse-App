.PHONY: deps-up deps-down migrate up down build rebuild logs ps clean

# --- Полный стек приложений (Standard Docker Compose) ---

up:
	@echo "🚀 Запуск полного стека MediaPulse..."
	docker compose up -d

down:
	@echo "🛑 Остановка полного стека..."
	docker compose down

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