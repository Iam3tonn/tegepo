# convert_dates.py

from pymongo import MongoClient
from datetime import datetime
import pytz
import re

client = MongoClient('mongodb+srv://root:admin@db.2vm7r5v.mongodb.net/TGP?retryWrites=true&w=majority&appName=db')
db = client['TGP']

# Перечислите все коллекции, которые нужно обновить
collections_to_update = [
    'balisun', 'bisnis', 'cnbc', 'cnn', 'detik', 'expat', 
    'google_bali_en', 'google_bali_ru', 'google_indonesia_en', 
    'infodenpasar', 'jawapos', 'kilasbali', 'nusabali', 'tribunnews'
]

# Словарь для преобразования индонезийских месяцев в английские
indonesian_months = {
    'Januari': 'January',
    'Februari': 'February',
    'Maret': 'March',
    'April': 'April',
    'Mei': 'May',
    'Juni': 'June',
    'Juli': 'July',
    'Agustus': 'August',
    'September': 'September',
    'Oktober': 'October',
    'November': 'November',
    'Desember': 'December'
}

def clean_date_string(date_str):
    # Удаление запятых и лишних пробелов
    date_str = date_str.replace(",", "").strip()
    return re.sub(' +', ' ', date_str)

def convert_dates():
    for collection_name in collections_to_update:
        collection = db[collection_name]
        document_count = collection.count_documents({})

        if document_count == 0:
            continue

        for item in collection.find():
            date_str = item.get('date', None)

            if not date_str:
                continue

            if isinstance(date_str, str):
                # Преобразование индонезийских месяцев в английские
                for indo_month, eng_month in indonesian_months.items():
                    date_str = date_str.replace(indo_month, eng_month)

                # Очистка строки даты
                date_str = clean_date_string(date_str)

                try:
                    # Попробуйте преобразовать строку в datetime объект
                    date_obj = datetime.strptime(date_str, '%d %B %Y %H:%M').replace(tzinfo=pytz.utc)
                    # Обновите документ с новым форматом даты
                    collection.update_one({'_id': item['_id']}, {'$set': {'date': date_obj}})
                except ValueError:
                    print(f"Error parsing date for item {item['_id']}: invalid format '{date_str}'")
                except Exception as e:
                    print(f"Error converting date for item {item['_id']}: {e}")

    print("Date conversion completed.")

if __name__ == '__main__':
    convert_dates()
