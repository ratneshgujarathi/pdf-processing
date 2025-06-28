.PHONY: help build run stop clean logs test dev prod

# Default target
help:
	@echo "Available commands:"
	@echo "  build    - Build the Docker image"
	@echo "  run      - Run the application with docker-compose"
	@echo "  stop     - Stop all containers"
	@echo "  clean    - Remove containers, images, and volumes"
	@echo "  logs     - Show application logs"
	@echo "  test     - Run tests in container"
	@echo "  dev      - Run in development mode"
	@echo "  prod     - Run in production mode"
	@echo "  logfiles - Show log file locations"
	@echo "  logtail  - Tail all log files"
	@echo "  logclean - Clean old log files"

# Build the Docker image
build:
	docker-compose build

# Run in development mode
dev:
	docker-compose up --build

# Run in production mode
prod:
	docker-compose -f docker-compose.prod.yml up --build -d

# Stop all containers
stop:
	docker-compose down
	docker-compose -f docker-compose.prod.yml down

# Show logs
logs:
	docker-compose logs -f app

# Clean up everything
clean:
	docker-compose down -v --rmi all
	docker-compose -f docker-compose.prod.yml down -v --rmi all
	docker system prune -f

# Run tests in container
test:
	docker-compose run --rm app python -m pytest applications/pdf/api/tests/ -v

# Health check
health:
	curl -f http://localhost:5000/api/v1/health || echo "Health check failed"

# Database test
dbtest:
	curl -f http://localhost:5000/api/v1/dbtest || echo "Database test failed"

# List PDFs
list:
	curl -f http://localhost:5000/api/v1/list || echo "List endpoint failed"

# Build and run with specific environment
run: build dev

# Production deployment
deploy: prod
	@echo "Production deployment started"
	@echo "Check logs with: make logs"
	@echo "Health check: make health"

# Log management
logfiles:
	@echo "Log file locations:"
	@echo "  Core logs: ./logs/core/"
	@echo "  API logs:  ./logs/api/"
	@echo "  PDF logs:  ./logs/pdf/"
	@echo "  Errors:    ./logs/core/errors.log"

logtail:
	@echo "Tailing all log files..."
	@tail -f logs/core/app.log logs/api/api.log logs/pdf/pdf_api.log logs/core/errors.log

logclean:
	@echo "Cleaning old log files..."
	@find logs/ -name "*.log.*" -delete
	@echo "Log cleanup completed" 