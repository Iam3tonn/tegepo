from pymongo import MongoClient
from datetime import datetime
import pytz

client = MongoClient('mongodb+srv://root:admin@db.2vm7r5v.mongodb.net/TGP?retryWrites=true&w=majority&appName=db')
db = client['TGP']
collection = db['balisun']

for item in collection.find():
    date_str = item['date']
    try:
        # Попробуйте преобразовать строку в datetime объект
        date_obj = datetime.strptime(date_str, '%d %B %Y %H:%M').replace(tzinfo=pytz.utc)
        # Обновите документ с новым форматом даты
        collection.update_one({'_id': item['_id']}, {'$set': {'date': date_obj}})
    except Exception as e:
        print(f"Error converting date for item {item['_id']}: {e}")
