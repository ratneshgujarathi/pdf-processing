import pytest
from unittest.mock import MagicMock
from applications.pdf import create_app
from flask import current_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    # Set up a mock mongo extension
    mock_mongo = MagicMock()
    mock_collection = MagicMock()
    mock_cx = MagicMock()
    mock_cx.__getitem__.return_value = MagicMock()
    mock_cx.__getitem__.return_value.pdfs = mock_collection
    mock_mongo.cx = mock_cx
    
    # Default mock behaviors (can be overridden in tests)
    mock_collection.find.return_value = []
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value = MagicMock(inserted_id='test_id')
    mock_collection.update_one.return_value = MagicMock(modified_count=1)
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)

    # Patch app.extensions for the test context
    app.extensions = getattr(app, 'extensions', {})
    app.extensions['mongo'] = mock_mongo

    with app.test_client() as client:
        yield client 