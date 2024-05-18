from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup
import json
from googletrans import Translator
from mongodb import is_news_in_db, add_news_to_db, remove_old_news

def get_full_text(article_url, translator):
    article_response = requests.get(article_url)
    if article_response.status_code == 200:
        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        full_text_element = article_soup.find('div', class_='penci-entry-content entry-content')
        if full_text_element:
            full_text = full_text_element.get_text(strip=True)
            translated_full_text = translator.translate(full_text, src='en', dest='ru').text
            return translated_full_text
    return None

def run():
    url = 'https://indonesiaexpat.id/news/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        translator = Translator()
        current_date = datetime.now(pytz.utc)
        target_timezone = pytz.timezone('Europe/Moscow')
        collection_name = 'expat'

        remove_old_news(collection_name)

        for article in soup.find_all('article'):
            title_element = article.find('h2')
            date_element = article.find('time')

            if title_element and date_element:
                title = title_element.text.strip()
                link = article.find('a')['href']
                pub_date_str = date_element['datetime']
                pub_date = datetime.strptime(pub_date_str, "%Y-%m-%dT%H:%M:%S%z")
                pub_date = pub_date.astimezone(target_timezone)

                if current_date - pub_date <= timedelta(days=3):
                    translated_title = translator.translate(title, src='en', dest='ru').text

                    if is_news_in_db(link, collection_name):
                        continue

                    full_text = get_full_text(link, translator)
                    if full_text:
                        news_item = {
                            'title': translated_title,
                            'link': link,
                            'date': pub_date.strftime("%d %B %Y %H:%M"),
                            'text_content': full_text
                        }
                        add_news_to_db(news_item, collection_name)
                        news_items.append(news_item)

        print('Данные успешно записаны expat')
    else:
        print('Ошибка при выполнении запроса к странице')

if __name__ == "__main__":
    run()
