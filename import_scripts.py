import os
import json
from pymongo import MongoClient

client = MongoClient('mongodb://admin:password@mongodb:27017/youtube_ai?authSource=admin')
db = client.youtube_ai
collection = db.scripts

scripts_dir = '/data/scripts'

for filename in os.listdir(scripts_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(scripts_dir, filename)
        with open(filepath) as f:
            data = json.load(f)
        data['filename'] = filename
        collection.update_one({'filename': filename}, {'$set': data}, upsert=True)

print("Scripts imported")