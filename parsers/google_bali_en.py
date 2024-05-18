def run():
    import time
    from datetime import datetime, timedelta
    import requests
    import json
    from googletrans import Translator
    import pytz
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news

    # Замените 'YOUR_API_KEY' на ваш действительный API ключ
    api_key = '31296e1c7c944861a1176a45fe535e41'
    
    # Определите диапазон дат (в данном случае, последние 3 дня)
    end_date = datetime.now(pytz.utc)
    start_date = end_date - timedelta(days=3)
    
    # Задайте параметры запроса
    topic = 'bali'
    language = 'en'
    page_size = 10
    
    # Формируем строку с диапазоном дат для запроса
    api_url = f'https://newsapi.org/v2/everything?q={topic}&pageSize={page_size}&language={language}&from={start_date.strftime("%Y-%m-%d")}&to={end_date.strftime("%Y-%m-%d")}&apiKey={api_key}'
    
    # Отправьте запрос к News API
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        collection_name = 'google_bali_en'
        remove_old_news(collection_name)

        if articles:
            translated_articles = []
            translator = Translator()

            for article in articles:
                title = article.get('title', '')
                link = article.get('url', '')
                published_at = article.get('publishedAt', '')

                article_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
                if article_date >= start_date:
                    if is_news_in_db(link, collection_name):
                        continue

                    time.sleep(3)  # Sleep for 3 seconds
                    translated_title = translator.translate(title, src='en', dest='ru').text
                    formatted_date = article_date.strftime('%d %B %Y %H:%M')

                    news_item = {
                        'title': translated_title,
                        'link': link,
                        'date': formatted_date
                    }
                    add_news_to_db(news_item, collection_name)
                    translated_articles.append(news_item)

            print(f'Сохранено {len(translated_articles)} новостей google_bali_en за последние 3 дня')
        else:
            print('Нет новостей по запросу.')
    else:
        print(f'Произошла ошибка при выполнении запроса: {response.status_code}')
        if response.status_code == 401:
            print('Ошибка 401: Неправильный API ключ или истек срок действия ключа.')

if __name__ == "__main__":
    run()
