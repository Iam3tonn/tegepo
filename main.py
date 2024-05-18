import asyncio
from aiogram import Bot, Dispatcher
import random
import logging
import schedule
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from googletrans import Translator
from convert_dates import convert_dates  # Импортируем функцию конвертации дат

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram Bot Configuration
bot = Bot(token='7190426477:AAHaNQgUV4cFZzxTpl62Aajboigr9Y04LXI')
dp = Dispatcher(bot)
channel_id = -1002057745919  # Убедитесь, что это правильный идентификатор канала
sent_links = set()

# MongoDB Configuration
client = MongoClient('mongodb+srv://root:admin@db.2vm7r5v.mongodb.net/TGP?retryWrites=true&w=majority&appName=db')
db = client['TGP']

# Translator Configuration
translator = Translator()

# Keywords to filter non-family-friendly content
family_friendly = [
    "погибли", "погаорели", "арест", "суд", "тюрьму", "тюрьма", "гениталии", "гениталия", "половой", "интимный", "интинмая", "половым",
    "криминал", "преступность", "убийство", "преступность", "преступная", "мертвый", "мертвыми", "эрекции", "пенис", "насилии", "насилие",
    "бомбардировщик", "приступности", "наркотики", "наркотиках", "наркотикам", "погибли", "погибла", "погиб", "мертвая", "мертвым", "незаконной",
    "госпитализирована","госпитализированы", "госпитализирован", "изнасиловали", "изнасиловал", "казахстанском", "умер", "умерли", "умерла",
    "ограбили", "ограбил", "ограбила", "Сан-Франциско", "секс", "сексом", "смерти", "изнасиловано", "убит", "убита", "убиты", "самоубийства",
    "самоубийство", "убил", "убила", "убило", "несчастные", "несчастный", "убийства", "члена", "ХАМАС", "газа", "газе", "газу", "война", "войну",
    "войны", "covid", "оружие", "хакер", "преступники", "обстрел", "выстрел", "авария", "загорелся", "Израиль", "политика", "палестина",
    "вирус", "военные", "грабеж", "жертвы", "Сектор Газа", "похоронен", "похоронны", "заключенные", "шпион", "нефтяные резервы", "инфляция",
    "беженцы", "ВИЧ", "СПИД", "проституция", "нападающий", "Путин", "Путина", "мошенничество", "мошенничества",
    # Спортивные новости
    "спорт", "футбол", "теннис", "баскетбол", "хоккей", "волейбол", "плавание", "бокс", "легкая атлетика", "бейсбол", "гольф", "спортсмен", 
    "соревнование", "матч", "турнир", "чемпионат", "лига", "тренировка", "спортивный", "сборная", "спортзал", "спортивные новости", "атлет", "игра"
]

async def send_new_data():
    try:
        # Запуск конвертации дат перед отправкой новых данных
        convert_dates()

        # Define date range (last 3 days)
        end_date = datetime.now(pytz.utc)
        start_date = end_date - timedelta(days=3)
        
        collections = db.list_collection_names()
        all_data = []

        logging.info(f"Start date: {start_date}, End date: {end_date}")

        for collection_name in collections:
            collection = db[collection_name]
            logging.info(f"Checking collection: {collection_name}")
            data = collection.find({"date": {"$gte": start_date, "$lte": end_date}, "sent": {"$exists": False}})
            count = collection.count_documents({"date": {"$gte": start_date, "$lte": end_date}, "sent": {"$exists": False}})
            logging.info(f"Found {count} documents in {collection_name} matching criteria")

            for item in data:
                logging.info(f"Document: {item}")
                all_data.append(item)
        
        random.shuffle(all_data)
        logging.info(f"Total new items to send: {len(all_data)}")

        for item in all_data:
            title = item['title']
            link = item['link']
            date = item['date']

            if any(word.lower() in title.lower() for word in family_friendly):
                logging.info(f"Skipping news with title: {title}")
                continue

            if link not in sent_links:
                try:
                    # Translate title to Russian
                    translated_title = translator.translate(title, src='auto', dest='ru').text

                    # Format date
                    if isinstance(date, datetime):
                        formatted_date = date.strftime('%d %B %Y %H:%M')
                    else:
                        formatted_date = date  # Keep as is if not datetime

                    message = f"{translated_title}\n\n{link}\n\n<i>{formatted_date}</i>"
                    await bot.send_message(chat_id=channel_id, text=message, parse_mode='HTML')
                    logging.info(f"Successfully sent message: {translated_title}")
                    sent_links.add(link)

                    # Mark the news as sent in MongoDB
                    collection.update_one({'_id': item['_id']}, {'$set': {'sent': True}})
                    logging.info(f"Marked as sent in MongoDB: {link}")
                    
                except Exception as e:
                    logging.error(f"Failed to send message: {e}")
                
                await asyncio.sleep(20)
    except Exception as e:
        logging.error(f"Error in send_new_data: {e}")

def execute_jsons_files():
    try:
        import jsons_files
        print("Starting jsons_files")
        jsons_files.main()
    except Exception as e:
        print(f"Error in execute_jsons_files: {e}")

async def main():
    while True:
        try:
            execute_jsons_files()
            await send_new_data()
            await asyncio.sleep(1800)
        except Exception as e:
            print(f"Произошла ошибка в main: {e}")

if __name__ == '__main__':
    schedule.every(20).minutes.do(execute_jsons_files)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main())

    while True:
        schedule.run_pending()
        loop.run_until_complete(asyncio.sleep(1))
