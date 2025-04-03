dev:
	docker run -d -p 9000:8000 chromadb/chroma && fastapi dev main.py
prod:
	docker compose up
