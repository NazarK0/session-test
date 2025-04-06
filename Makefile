dev:
	fastapi dev app/main.py
prod:
	docker compose up
db:
	docker run -p 9000:8000 chromadb/chroma
