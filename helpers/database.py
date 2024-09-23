import logging
from flask_pymongo import PyMongo

def db_init(app):
    db = PyMongo(app)
    return db

def validate_collections(db):
    try:
        collections = db.collection_names(include_system_collections=False)
        for collection in collections:
            db.validate_collection(collection)
        logging.info('Validation successfull...')
    except Exception as err:
        logging.error(f"Failed to validate database collection: {err}")