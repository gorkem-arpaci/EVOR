.PHONY: up down seed reset

up:
	docker compose up -d

down:
	docker compose down -v

seed:
	docker cp mock_data.sql evor-postgres-1:/mock_data.sql
	docker exec -it evor-postgres-1 psql -U gorkem -d evor-db -f /mock_data.sql

reset: down up
	@echo "Waiting for postgres..."
	@sleep 3
	$(MAKE) seed
