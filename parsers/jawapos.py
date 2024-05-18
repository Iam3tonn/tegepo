def run():
    import requests
    from bs4 import BeautifulSoup
    from googletrans import Translator
    import json
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news
    from time import sleep
    from random import randint

    collection_name = 'jawapos'
    url = 'https://www.jawapos.com'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        news_list = []
        news_elements = soup.find_all(['div'], class_=["col-bs10-7", "latest clearfix", "latest__wrap"])
        translator = Translator()
        remove_old_news(collection_name)

        for news_element in news_elements:
            news_data = {}
            link_element = news_element.find('a', href=True)
            if link_element:
                news_data['link'] = link_element['href']

            text_element = news_element.find('img')
            if text_element:
                news_data['News Text'] = text_element.get('alt', '')
                translation = translator.translate(news_data['News Text'], src='auto', dest='ru')
                news_data['title'] = translation.text

            date_element = news_element.find('date', class_='latest__date')
            if date_element:
                publication_date = date_element.get_text(strip=True).replace('WIB', '')
                news_data['date'] = publication_date

            if is_news_in_db(news_data['link'], collection_name):
                continue

            add_news_to_db(news_data, collection_name)
            news_list.append(news_data)

            # Add a random delay between requests to avoid being blocked
            sleep(randint(1, 3))

    else:
        print('Ошибка парсинга jawapos:', response.status_code)

run()
