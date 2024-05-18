def run():
    import requests
    from bs4 import BeautifulSoup
    from googletrans import Translator
    from datetime import datetime
    import json
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news

    collection_name = 'nusabali'

    def get_news(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find('div', id='article-list').find_all('div', class_='row feature-items')

        news_list = []
        translator = Translator()

        for item in news_items:
            title_tag = item.find('h5').find('a')
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            translated_title = translator.translate(title, src='id', dest='ru').text

            time_tag = item.find('span', class_='entry-date').find('span', class_='month')
            news_time = datetime.strptime(time_tag.get_text(strip=True), '%d %b %Y %H:%M').strftime('%d %B %Y %H:%M')

            news_item = {
                'title': translated_title,
                'link': link,
                'date': news_time
            }

            if is_news_in_db(link, collection_name):
                continue

            add_news_to_db(news_item, collection_name)
            news_list.append(news_item)

        return news_list

    news_url = 'https://www.nusabali.com/'
    latest_news = get_news(news_url)
    print("nusabali completed")

run()
