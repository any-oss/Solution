.PHONY: build test lint smoke health push clean

IMAGE_NAME := anydockerhub/solution
TAG := $(IMAGE_NAME):latest

build:
	docker build -t $(TAG) .

test:
	python -m pytest tests/ -v

lint:
	flake8 core/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

smoke:
	docker compose up -d
	sleep 5
	bash scripts/smoke_test.sh
	docker compose down

health:
	@curl -s http://localhost:8000/health | jq .

push:
	docker push $(TAG)

clean:
	docker system prune -f
