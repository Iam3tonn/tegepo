import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import json
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed
import pytz
from mongodb import is_news_in_db, add_news_to_db, remove_old_news

collection_name = 'kilasbali'

def translate_date(ind_date):
    # Indonesian to English month mapping
    months = {
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
    parts = ind_date.split()
    day = parts[1].strip(',')
    month = months[parts[2]]
    year = parts[3]
    time = "12:00"
    formatted_date = f"{day} {month} {year} {time}"
    return formatted_date

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def get_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = soup.find('div', class_='mag-box-container clearfix').find_all('li', class_='post-item tie-standard')

    news_list = []
    translator = Translator()

    for item in news_items:
        title_link = item.find('h2', class_='post-title').find('a')
        title = title_link.get_text(strip=True)
        link = title_link['href']
        translated_title = translator.translate(title, src='id', dest='ru').text

        date_info = item.find('span', class_='date meta-item tie-icon')
        news_date = translate_date(date_info.get_text(strip=True)) if date_info else 'No date found'

        news_item = {
            'title': translated_title,
            'link': link,
            'date': news_date
        }

        if not is_news_in_db(link, collection_name):
            add_news_to_db(news_item, collection_name)
            news_list.append(news_item)

    return news_list

def run():
    news_url = 'https://www.kilasbali.com/'
    latest_news = get_news(news_url)

    print("kilasbali completed")

run()
