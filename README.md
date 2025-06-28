# PDF Processing API

A secure Flask API for uploading, storing, and viewing PDFs using AWS S3 and MongoDB. The application provides modular endpoints for health checks, database tests, PDF upload, listing, and viewing with comprehensive security features.

## Features

- **Secure PDF Upload**: Upload PDFs to private S3 bucket with metadata storage in MongoDB
- **PDF Management**: List and view PDFs with secure backend proxying
- **Security**: No S3 URLs exposed, private bucket access, secure file handling
- **Comprehensive Testing**: 100% test coverage with mocked S3 interactions
- **Containerized**: Docker support for easy deployment and dependency management
- **Production Ready**: Gunicorn WSGI server, external nginx support, SSL ready, rate limiting

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- AWS credentials configured
- External MongoDB instance
- External nginx (for production)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pdf-processing
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your AWS credentials and MongoDB URI
   ```

3. **Run with Docker Compose**
   ```bash
   # Development mode (Flask dev server)
   make dev
   
   # Or manually
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:5000
   - Swagger UI: http://localhost:5000/swagger
   - Health Check: http://localhost:5000/api/v1/health

### Production Deployment

#### Option 1: External Nginx (Recommended)

1. **Deploy the Flask app with Gunicorn**
   ```bash
   make prod
   
   # Or manually
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. **Configure external nginx**
   ```bash
   # Copy the external nginx config
   sudo cp nginx-external.conf /etc/nginx/sites-available/pdf-api
   
   # Update the domain and SSL paths in the config
   sudo nano /etc/nginx/sites-available/pdf-api
   
   # Enable the site
   sudo ln -s /etc/nginx/sites-available/pdf-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **Access the production API**
   - API: https://your-domain.com
   - Health Check: https://your-domain.com/health

#### Option 2: Load Balancer (Cloud)

1. **Deploy to cloud platform**
   ```bash
   # Deploy container with Gunicorn
   make prod
   
   # Configure load balancer to point to port 5000
   # Set up SSL termination at load balancer level
   ```

## Docker Commands

```bash
# Build the image
make build

# Run in development (Flask dev server)
make dev

# Run in production (Gunicorn)
make prod

# Test Gunicorn locally
make gunicorn

# Stop all containers
make stop

# View logs
make logs

# Run tests
make test

# Clean up everything
make clean

# Health check
make health

# Database test
make dbtest

# List PDFs
make list
```

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.11+
- MongoDB
- AWS S3 bucket
- AWS credentials

### Installation

1. **Clone and setup virtual environment**
   ```bash
   git clone <repository-url>
   cd pdf-processing
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   # Development mode (Flask dev server)
   export FLASK_ENV=development
   python run.py
   
   # Production mode (Gunicorn)
   export FLASK_ENV=production
   gunicorn -c gunicorn.conf.py run:app
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
# MongoDB Configuration (External)
MONGODB_URI=mongodb://localhost:27017/pdf_processing
# For MongoDB Atlas:
# MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/pdf_processing?retryWrites=true&w=majority

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-pdf-bucket

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
```

## Production Features

### Gunicorn WSGI Server
- **Multi-worker processes**: Handles concurrent requests efficiently
- **Process management**: Automatic restart on crashes
- **Load balancing**: Distributes requests across workers
- **Production logging**: Structured logging with request tracking
- **Graceful shutdown**: Proper handling of SIGTERM signals

### Configuration
- **Workers**: Automatically scales based on CPU cores (CPU_COUNT * 2 + 1)
- **Timeout**: 120 seconds for long-running PDF operations
- **Memory management**: Workers restart after 1000 requests to prevent memory leaks
- **Security**: Request size limits and field validation

## API Endpoints

### Health Check
- **GET** `/api/v1/health`
- Returns application health status

### Database Test
- **GET** `/api/v1/dbtest`
- Tests MongoDB connection

### Upload PDF
- **POST** `/api/v1/upload`
- Upload a PDF file to S3 and store metadata in MongoDB
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (PDF file)

### List PDFs
- **GET** `/api/v1/list`
- Returns list of all PDFs with metadata

### View PDF
- **GET** `/api/v1/view/<filename>`
- Streams PDF file from S3 through backend proxy

## Security Features

- **Private S3 Bucket**: All PDFs stored in private S3 bucket
- **No URL Exposure**: S3 URLs never exposed in API responses
- **Backend Proxying**: PDF viewing through secure backend proxy
- **Input Validation**: Comprehensive file type and size validation
- **Rate Limiting**: API rate limiting in production
- **SSL/TLS**: HTTPS support with proper security headers
- **Non-root Container**: Docker containers run as non-root user

## Testing

### Run Tests
```bash
# With Docker
make test

# Without Docker
python -m pytest applications/pdf/api/tests/ -v
```

### Test Coverage
```bash
python -m pytest applications/pdf/api/tests/ --cov=applications/pdf/api --cov-report=html
```

## Project Structure

```
pdf-processing/
├── applications/
│   ├── common/
│   │   ├── response_factory.py
│   │   └── s3_utils.py
│   └── pdf/
│       ├── api/
│       │   ├── tests/
│       │   ├── v1.py
│       │   └── health.py
│       ├── config.py
│       ├── specs/
│       └── swagger_config.py
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx-external.conf
├── Makefile
├── requirements.txt
└── run.py
```

## Development

### Adding New Endpoints

1. Create endpoint in `applications/pdf/api/v1.py`
2. Add OpenAPI spec in `applications/pdf/specs/`
3. Write tests in `applications/pdf/api/tests/`
4. Update Swagger configuration if needed

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Maintain 100% test coverage

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check MongoDB service is running
   - Verify connection string in `.env`
   - Check network connectivity

2. **S3 Upload Failed**
   - Verify AWS credentials
   - Check S3 bucket permissions
   - Ensure bucket exists and is accessible

3. **Docker Build Fails**
   - Check Docker is running
   - Verify Dockerfile syntax
   - Clear Docker cache: `docker system prune`

4. **Port Already in Use**
   - Change port in docker-compose.yml
   - Stop conflicting services
   - Use different port mapping

5. **Nginx Configuration Issues**
   - Check nginx syntax: `nginx -t`
   - Verify SSL certificate paths
   - Check file permissions

### Logs

```bash
# Application logs
make logs

# Docker container logs
docker-compose logs app

# Nginx logs (external)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
