.PHONY: up down test clean

up:
	docker-compose up -d

down:
	docker-compose down

test:
	pytest -q

clean:
	docker-compose down -v
	docker system prune -f

