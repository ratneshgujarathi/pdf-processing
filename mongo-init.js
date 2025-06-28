// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the application database
db = db.getSiblingDB('pdf_processing');

// Create a user for the application
db.createUser({
  user: 'pdf_user',
  pwd: 'pdf_password',
  roles: [
    {
      role: 'readWrite',
      db: 'pdf_processing'
    }
  ]
});

// Create collections with proper indexes
db.createCollection('pdfs');

// Create indexes for better performance
db.pdfs.createIndex({ "filename": 1 }, { unique: true });
db.pdfs.createIndex({ "created_at": -1 });
db.pdfs.createIndex({ "original_filename": 1 });

print('MongoDB initialization completed successfully'); 