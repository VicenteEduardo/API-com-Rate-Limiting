install:
	pip install -r requirements.txt

test:
	pytest -v

run:
	uvicorn app.main:app --reload --port 8000

docker:
	docker compose up --build
