import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "smart_wardrobe")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "wardrobe")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

wardrobe_collection = db[COLLECTION_NAME]