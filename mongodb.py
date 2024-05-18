# mongodb.py
from pymongo import MongoClient
import datetime

client = MongoClient('mongodb+srv://root:admin@db.2vm7r5v.mongodb.net/TGP?retryWrites=true&w=majority&appName=db')
db = client['TGP']  # Подключаемся к вашей базе данных TGP

def get_collection(collection_name):
    return db[collection_name]

def is_news_in_db(news_link, collection_name):
    collection = get_collection(collection_name)
    return collection.find_one({"link": news_link}) is not None

def add_news_to_db(news_item, collection_name):
    collection = get_collection(collection_name)
    collection.insert_one(news_item)

def remove_old_news(collection_name, days=5):
    collection = get_collection(collection_name)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    collection.delete_many({"date": {"$lt": cutoff_date}})
