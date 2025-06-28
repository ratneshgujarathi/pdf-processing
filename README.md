# PDF Processing API

A secure Flask-based API for uploading, storing, and viewing PDF files using AWS S3 and MongoDB.

## Features

- **Secure PDF Upload**: Files uploaded to private S3 bucket with metadata stored in MongoDB
- **Comprehensive Metadata**: MD5 hash, timestamps, file size, and original filename tracking
- **Swagger Documentation**: Interactive API documentation
- **Modular Test Structure**: Robust test suite with comprehensive coverage
- **Factory Pattern**: Standardized API responses using ResponseFactory

## Project Structure

```
pdf-processing/
├── applications/
│   ├── common/
│   │   ├── response_factory.py    # Standardized API response factory
│   │   └── s3_utils.py            # S3 upload and utility functions
│   └── pdf/
│       ├── api/
│       │   ├── v1.py              # Main API endpoints (upload, list, view)
│       │   ├── health.py          # Health check and database test endpoints
│       │   ├── tests/             # Modular test structure
│       │   │   ├── conftest.py    # Shared test fixtures
│       │   │   ├── test_upload.py # Upload endpoint tests
│       │   │   ├── test_list.py   # List and view endpoint tests
│       │   │   ├── test_health.py # Health endpoint tests
│       │   │   ├── test_dbtest.py # Database test endpoint tests
│       │   │   └── test_errors.py # Error handler tests
│       │   └── specs/             # Swagger YAML specifications
│       │       ├── upload.yaml
│       │       ├── list_pdfs.yaml
│       │       ├── health.yaml
│       │       └── dbtest.yaml
│       ├── config.py              # Application configuration
│       ├── swagger_config.py      # Swagger UI configuration
│       └── __init__.py            # Flask app factory
├── requirements.txt               # Python dependencies
├── run.py                         # Application entry point
└── .env                          # Environment variables (create this)
```

## Setup

### 1. Environment Variables (.env file)

Create a `.env` file in the project root with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your_secret_key_here

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/pdf_engine
# OR for MongoDB Atlas:
# MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/pdf_engine?retryWrites=true&w=majority

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET_NAME=your_s3_bucket_name
AWS_REGION=your_aws_region
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health & Database
- `GET /api/v1/health` - Service health check
- `GET /api/v1/dbtest` - Database connection test

### PDF Management
- `POST /api/v1/upload` - Upload a PDF file
- `GET /api/v1/list` - List all uploaded PDFs
- `GET /api/v1/view/<filename>` - View a specific PDF

## Testing

### Run All Tests
```bash
PYTHONPATH=. pytest applications/pdf/api/tests/
```

### Run Tests with Coverage
```bash
PYTHONPATH=. pytest --cov=applications/pdf/api --cov-report=term-missing applications/pdf/api/tests/
```

### Test Structure
- **Modular Tests**: Each endpoint has its own test file
- **Mocked S3**: Tests use mocked S3 operations for reliability
- **Error Coverage**: All error paths are tested
- **100% Coverage**: All business logic is covered

## Swagger Documentation

### Access Swagger UI
Visit `http://localhost:5000/swagger/` to access the interactive API documentation.

### Features
- Interactive API testing
- Request/response examples
- Endpoint descriptions
- Schema definitions

## Security Features

### S3 Security
- **Private Bucket**: All files stored in private S3 bucket
- **No URL Exposure**: S3 URLs never exposed in API responses
- **Proxied Access**: All file access goes through backend
- **ACL Control**: Files uploaded with private ACL

### API Security
- **Input Validation**: File type and size validation
- **Secure Filenames**: Uses `secure_filename` for safe file names
- **Error Handling**: Comprehensive error handling without information leakage
- **Standardized Responses**: Consistent API response format

## File Metadata

Each uploaded PDF stores the following metadata:
- `filename`: Secure filename used in S3
- `original_filename`: Original uploaded filename
- `content_type`: MIME type of the file
- `size`: File size in bytes
- `md5`: MD5 hash for integrity verification
- `created_at`: Upload timestamp (UTC)
- `updated_at`: Last update timestamp (UTC)

## Response Format

All API responses follow a standardized format:

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": { ... }
}
```

## Development

### Code Quality
- **Modular Structure**: Clean separation of concerns
- **Factory Pattern**: Standardized response handling
- **Error Handling**: Comprehensive error management

### Testing Strategy
- **Unit Tests**: Individual endpoint testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Testing**: External service mocking
- **Error Testing**: All error paths covered

## Deployment

### Requirements
- Python 3.8+
- MongoDB instance
- AWS S3 bucket
- AWS credentials with S3 permissions

### Environment Variables
Ensure all required environment variables are set in production (see Setup section for detailed examples).

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Maintain test coverage
4. Update documentation as needed
5. Use the ResponseFactory for consistent API responses
