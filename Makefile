.PHONY: setup install migrate dev test lint fmt freeze superuser api-test docs

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

superuser:
	./.venv/bin/python manage.py createsuperuser

api-test:
	@echo "API 테스트를 위한 curl 명령어들:"
	@echo "프로젝트 목록: curl http://localhost:8000/api/projects/"
	@echo "프로젝트 생성: curl -X POST http://localhost:8000/api/projects/ -H 'Content-Type: application/json' -d '{\"author_email\":\"test@example.com\",\"project_name\":\"Test Project\",\"project_code\":\"TEST001\",\"project_keyword\":\"test,api\"}'"
	@echo "프로젝트 상세: curl http://localhost:8000/api/projects/1/"
	@echo "프로젝트 자료: curl http://localhost:8000/api/projects/1/materials/"
	@echo "외부 데이터 매칭 (키워드): curl http://localhost:8000/api/projects/1/external_matches_by_keyword/"
	@echo "외부 데이터 매칭 (코드): curl http://localhost:8000/api/projects/1/external_matches_by_code/"
	@echo "외부 데이터로 아이템 생성 (키워드): curl -X POST http://localhost:8000/api/projects/1/create_items_from_external_matches_by_keyword/"
	@echo "외부 데이터로 아이템 생성 (코드): curl -X POST http://localhost:8000/api/projects/1/create_items_from_external_matches_by_code/"

docs:
	@echo "API 문서 URL들:"
	@echo "Swagger UI: http://localhost:8000/api/docs/"
	@echo "ReDoc: http://localhost:8000/api/redoc/"
	@echo "OpenAPI Schema: http://localhost:8000/api/schema/"
