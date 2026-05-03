from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = "mongodb+srv://abi:abi@cluster0.tf5kgki.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["stylemate"]

necklace_collection = db["necklaces"]

print("MongoDB connected successfully")