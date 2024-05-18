from datetime import datetime, timedelta
import requests
import json
import pytz
from mongodb import is_news_in_db, add_news_to_db, remove_old_news

def run():
    # Замените 'YOUR_API_KEY' на ваш действительный API ключ
    api_key = '31296e1c7c944861a1176a45fe535e41'
    
    topic = 'Бали'
    language = 'ru'
    page_size = 10
    
    # Определите диапазон дат (в данном случае, последние 3 дня)
    end_date = datetime.now(pytz.utc)  # offset-aware datetime
    start_date = end_date - timedelta(days=3)
    
    # Формируем строку с диапазоном дат для запроса
    api_url = f'https://newsapi.org/v2/everything?q={topic}&pageSize={page_size}&language={language}&apiKey={api_key}&from={start_date.strftime("%Y-%m-%dT%H:%M:%SZ")}&to={end_date.strftime("%Y-%m-%dT%H:%M:%SZ")}'
    
    # Отправьте запрос к News API
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        collection_name = 'google_bali_ru'
        remove_old_news(collection_name)

        if articles:
            translated_articles = []

            for article in articles:
                title = article.get('title', '')
                link = article.get('url', '')
                published_at = article.get('publishedAt', '')
                
                # Преобразуем published_at в offset-aware datetime
                article_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)

                if article_date >= start_date:
                    if is_news_in_db(link, collection_name):
                        continue

                    formatted_published_at = article_date.strftime('%d %B %Y %H:%M')
                    news_item = {
                        'title': title,
                        'link': link,
                        'date': formatted_published_at
                    }
                    add_news_to_db(news_item, collection_name)
                    translated_articles.append(news_item)

            print(f'Сохранено {len(articles)} новостей google_bali_ru за последние 3 дня')
        else:
            print('Нет новостей по запросу за последние 3 дня.')
    else:
        print(f'Произошла ошибка при выполнении запроса: {response.status_code}')
        if response.status_code == 401:
            print('Ошибка 401: Неправильный API ключ или истек срок действия ключа.')
run()
