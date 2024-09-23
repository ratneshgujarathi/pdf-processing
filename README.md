
# PDF Processing API

## Description:
This project provides a set of public APIs for performing various operations on PDF files. It is designed as an open-source project, allowing developers to easily integrate PDF-related functionalities into their applications. The current implementation provides basic file handling features, and future work aims to expand its capabilities to include more advanced PDF processing operations.

## Features Completed:
1. **File Upload API**: Upload PDFs to the server and store metadata in MongoDB.
2. **File Download API**: Download stored PDF files by filename or ID.
3. **List Files API**: Retrieve a paginated list of uploaded PDF files with filters for:
   - Date range (from_date, to_date)
   - Specific upload date
   - Filename search (case-insensitive)
   - Sorting and pagination capabilities

## Technologies Used:
- **Flask**: For the web framework and API management.
- **MongoDB**: As the database for storing file metadata.
- **PyMongo**: For MongoDB integration.
- **BSON**: Handling MongoDB ObjectId serialization.
- **Docker**: Containerization for easy deployment.
- **File Handling**: Upload and store files in a specific directory with metadata saved in MongoDB.

## How to Run:
1. Clone the repository.
2. Install the dependencies listed in `requirements.txt`.
3. Set up a `.env` file with your MongoDB credentials and other configuration.
4. Run the Flask app using Docker or locally.

## Future Work:
1. **PDF Merging API**: Merge multiple PDFs into a single document.
2. **PDF Splitting API**: Split a single PDF into multiple documents.
3. **PDF Form Field Extraction**: Extract and process form fields from PDFs.
4. **PDF Metadata Extraction**: Extract metadata like author, title, etc., from the PDF.
5. **Text and Image Extraction**: Extract text and images from PDF files.
6. **Security Enhancements**: Add API key authentication and access controls.
7. **File Versioning**: Implement a version control system for uploaded PDFs.
8. **Advanced Error Handling**: Improve logging and detailed error responses.

## How to Contribute:
- Fork the repository and submit a pull request for any new feature or bug fix.
- Review the "Future Work" section to see areas that need contributions.

Feel free to open issues or reach out for any questions!
