.PHONY: install test run run-payment docker-build a2a-registry-payload

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

# 例: make a2a-registry-payload PUBLIC_BASE_URL=https://verinode.onrender.com
a2a-registry-payload:
	@test -n "$(PUBLIC_BASE_URL)" || (echo "usage: make a2a-registry-payload PUBLIC_BASE_URL=https://your-host" && exit 1)
	PUBLIC_BASE_URL="$(PUBLIC_BASE_URL)" .venv/bin/python scripts/print_a2a_registry_payload.py
