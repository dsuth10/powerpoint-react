lint:
	cd backend && ruff . && black --check . && mypy .

test:
	cd backend && pytest --cov=backend/app --cov-report=term-missing

up:
	docker compose -f docker-compose.dev.yml up -d --build

down:
	docker compose -f docker-compose.dev.yml down -v

logs:
	docker compose -f docker-compose.dev.yml logs -f --tail=200

quality:
	$(MAKE) lint && $(MAKE) test