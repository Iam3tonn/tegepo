from datetime import datetime, timedelta
import requests
import json
import pytz
from mongodb import is_news_in_db, add_news_to_db, remove_old_news

def is_family_friendly(content):
    family_friendly = [
        "погибли", "погаорели", "арест", "суд", "тюрьму", "тюрьма", "гениталии", "гениталия", "половой", "интимный", "интинмая", "половым",
        "криминал", "преступность", "убийство", "преступность", "преступная", "мертвый", "мертвыми", "эрекции", "пенис", "насилии", "насилие",
        "бомбардировщик", "приступности", "наркотики", "наркотиках", "наркотикам", "погибли", "погибла", "погиб", "мертвая", "мертвым", "незаконной",
        "госпитализирована","госпитализированы", "госпитализирован", "изнасиловали", "изнасиловал", "казахстанском", "бомбардировщик", "умер", "умерли",
        "умерла", "ограбили", "ограбил", "ограбила", "Сан-Франциско", "секс", "сексом", "смерти", "изнасиловано", "убит", "убита", "убиты", "самоубийства",
        "самоубийство", "убил", "убила", "убило", "несчастные", "несчастный", "убийства", "члена", "ХАМАС", "газа", "газе", "газу", " война", "войну",
        "войны", "covid", "прогноз погоды", "премьер-лига", "расписание", "билетов", "оружие", "хакер", "гороскоп", "зодиака", "зодиак", "молитвенный",
        "партия", "вакансии", "преступники", "обстрел", "выстрел", "лига", "вакансий", "авария", "загорелся", "Израиль", "политика", "палестина",
        "вирус", "акции", "военные", "футбол", "безработица", "Шот муляни", "грабеж", "жертвы", "Сектор Газа", "прогноз погоды", "лига", "Shopee",
        "похоронен", "похоронны", "заключенные", "шпион", "нефтяные резервы", "инфляция", "скидки", "беженцы", "Ливерпуль", "ВИЧ", "СПИД", "трансмарт",
        "transmart", "фанат", "проституция", "нападающий", "сборная", "теннис", "палестина", "газы", "лига чемпионов", "футбол", "выборы", "дебаты", "думв",
        "Путин", "Путина", "лига", "Лига", "Лиге", "лиге", "кубкой", "кубок", "кубка", "мошенничество", "мошенничества"
    ]
    return any(word.lower() in content.lower() for word in family_friendly)

def run():
    # Замените 'YOUR_API_KEY' на ваш действительный API ключ
    api_key = '31296e1c7c944861a1176a45fe535e41'
    
    topic = 'Индонезия'
    language = 'ru'
    page_size = 10
    
    # Определите диапазон дат (в данном случае, последние 3 дня)
    end_date = datetime.now(pytz.utc)  # offset-aware datetime
    start_date = end_date - timedelta(days=3)
    
    # Формируем строку с диапазоном дат для запроса
    api_url = f'https://newsapi.org/v2/everything?q={topic}&pageSize={page_size}&language={language}&from={start_date.strftime("%Y-%m-%dT%H:%M:%SZ")}&to={end_date.strftime("%Y-%m-%dT%H:%M:%SZ")}&apiKey={api_key}'
    
    # Отправьте запрос к News API
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        collection_name = 'google_news_indonesia'
        remove_old_news(collection_name)

        if articles:
            translated_articles = []

            for article in articles:
                title = article.get('title', '')
                link = article.get('url', '')
                published_at = article.get('publishedAt', '')

                # Преобразуем published_at в offset-aware datetime
                article_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)

                if article_date >= start_date and is_family_friendly(title):
                    if is_news_in_db(link, collection_name):
                        continue

                    formatted_date = article_date.strftime('%d %B %Y %H:%M')
                    news_item = {
                        'title': title,
                        'link': link,
                        'date': formatted_date
                    }
                    add_news_to_db(news_item, collection_name)
                    translated_articles.append(news_item)

            print(f'Saved {len(translated_articles)} family-friendly news articles from google_news_indonesia within the last 3 days.')
        else:
            print('No news articles found for the query.')
    else:
        print(f'Произошла ошибка при выполнении запроса: {response.status_code}')
        if response.status_code == 401:
            print('Ошибка 401: Неправильный API ключ или истек срок действия ключа.')
run()
