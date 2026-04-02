import os
import json
from pymongo import MongoClient

client = MongoClient('mongodb://admin:password@mongodb:27017/youtube_ai?authSource=admin')
db = client.youtube_ai
collection = db.topics

topics_dir = '/data/topics'

for filename in os.listdir(topics_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(topics_dir, filename)
        with open(filepath) as f:
            data = json.load(f)
        data['filename'] = filename
        collection.update_one({'filename': filename}, {'$set': data}, upsert=True)

print("Topics imported")