.PHONY: setup install migrate dev test lint fmt freeze

PY_VERSION := 3.12.5

setup:
	@echo "Ensure pyenv installed, then run: pyenv install -s $(PY_VERSION) && pyenv local $(PY_VERSION)"

install:
	python3 -m virtualenv .venv || true
	./.venv/bin/pip install -r requirements-dev.txt

migrate:
	./.venv/bin/python manage.py migrate

dev:
	DJANGO_DEBUG=True ./.venv/bin/python manage.py runserver 0.0.0.0:8000

test:
	./.venv/bin/pytest -q || true

lint:
	./.venv/bin/ruff check .

fmt:
	./.venv/bin/black .

freeze:
	./.venv/bin/pip-compile --generate-hashes -o requirements.txt requirements.in
	./.venv/bin/pip-compile --generate-hashes -o requirements-dev.txt requirements-dev.in
