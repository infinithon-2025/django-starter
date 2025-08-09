# django-starter

Reproducible Django starter using pyenv + virtualenv.

## Prerequisites
- Homebrew + pyenv installed
- Python 3.12.5 installed via pyenv: `pyenv install -s 3.12.5`
- Set local version: `pyenv local 3.12.5`

## Setup
```bash
git clone <your-repo-url>
cd django-starter
python3 -m virtualenv .venv
./.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env
```

## Run
```bash
make migrate
make dev
# open http://127.0.0.1:8000/ -> {"status":"ok"}
```

## Dependency management
- Edit `requirements.in` and `requirements-dev.in`, then:
```bash
make freeze
```

## Notes
- `.python-version` pins the Python version for pyenv.
- Use `pyenv install -s 3.12.5 && pyenv local 3.12.5` to match the project.
