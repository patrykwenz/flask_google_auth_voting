import os
import pymongo

MONGODB_CLIENT_URI = os.environ.get('MONGODB_CLIENT_URI', None).replace('"', '')
client = pymongo.MongoClient(MONGODB_CLIENT_URI)
db = client["Glosowanie"]
