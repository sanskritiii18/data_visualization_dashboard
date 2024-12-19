import json
from logging import exception, error
from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client['database']
    collection = db['collection']
    print("connection succesful")
except:
    print("error")

with open('jsondata.json', 'r') as file:
    data = json.load(file)

if isinstance(data, list):
    collection.insert_many(data)
else:
    collection.insert_one(data)

print("Data inserted into MongoDB successfully!")


