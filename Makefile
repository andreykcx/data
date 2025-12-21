COMPOSE ?= docker compose

.PHONY: up down logs format test

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

format:
	python -m pip install -q -r api/requirements.txt black
	black api
	npm --prefix frontend install
	npm --prefix frontend run format

test:
	python -m pip install -q -r api/requirements.txt pytest
	pytest api
	npm --prefix frontend install
	npm --prefix frontend run test
