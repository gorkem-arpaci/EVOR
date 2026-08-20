
# GÜNCEL BACKEND ÇALIŞTIRMA
#
# Docker (önerilen) - tüm servisleri ayağa kaldırır, sonra migration çalıştır:
#   make up
#   make venv
#   make install
#   export DATABASE_URL="postgresql+psycopg2://<user>:<pass>@localhost:5432/evor-db"
#   make migrate
#
# Lokal (Docker yoksa) - venv içinde çalıştırma:
#   python3 -m venv .venv
#   . .venv/bin/activate
#   python -m pip install --upgrade pip setuptools wheel
#   python -m pip install -r requirements.txt
#   export DATABASE_URL="postgresql+psycopg2://<user>:<pass>@localhost:5432/evor-db"
#   .venv/bin/python app/app.py
#
# Eski/manuel seed (SQL fallback):
#   make seed   # (konteyner adı/compose ayarına bağlı çalışır)
#
# Not: Tercih edilen akış Alembic-first (make migrate). Raw SQL sadece acil durum/manuel kurulum içindir.

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

# --- Alembic-first helpers (venv-based) ---
.PHONY: venv install migrate init-db archive-sql

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ALEMBIC := $(VENV)/bin/alembic

venv:
	@echo "Creating virtualenv $(VENV) if missing..."
	@test -d $(VENV) || python3 -m venv --upgrade-deps $(VENV) || python3 -m venv $(VENV)

install: venv
	@echo "Installing Python dependencies into $(VENV)"
	$(PY) -m pip install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt

migrate: venv
	@echo "Running Alembic migrations (alembic upgrade head)"
	@if [ -z "$$DATABASE_URL" ]; then echo "Set DATABASE_URL before running migrate"; exit 1; fi
	@if [ -x "$(ALEMBIC)" ]; then \
		$(ALEMBIC) upgrade head; \
	else \
		$(PY) -m alembic upgrade head; \
	fi

# init-db: raw SQL fallback (opt-in). Prefer `make migrate` in normal workflows.
init-db:
	@if [ -z "$$DATABASE_URL" ]; then echo "Set DATABASE_URL before running init-db"; exit 1; fi
	@echo "Applying raw SQL files (init.sql + mock_data.sql) as fallback"
	@psql "$$DATABASE_URL" -f init.sql
	@psql "$$DATABASE_URL" -f mock_data.sql

archive-sql:
	@mkdir -p data/sql-backups
	@mv -f init.sql data/sql-backups/ || true
	@mv -f mock_data.sql data/sql-backups/ || true
	@echo "Moved init.sql and mock_data.sql to data/sql-backups/"
