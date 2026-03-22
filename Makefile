.PHONY: install test run run-payment docker-build

install:
	python3 -m venv .venv
	.venv/bin/python -m pip install -U pip
	.venv/bin/pip install -r requirements-dev.txt

test:
	.venv/bin/pytest tests/ -q

run:
	.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

run-payment:
	./scripts/run_with_payment_gate.sh

docker-build:
	docker build -t verinode .
