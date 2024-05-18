def run():
    import requests
    from bs4 import BeautifulSoup
    from googletrans import Translator
    import json
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news

    collection_name = 'cnbc'

    def translate_to_russian(text):
        translator = Translator()
        translation = translator.translate(text, dest='ru')
        return translation.text

    def extract_date(news_url):
        response = requests.get(news_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            date_element = soup.find('div', class_='date')
            if date_element:
                return date_element.text.strip()
        return None

    url = 'https://www.cnbcindonesia.com'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_elements = soup.select('ul.list.media_rows.middle.thumb.terbaru li article')
        news_list = []
        remove_old_news(collection_name)

        for news_element in news_elements:
            title = news_element.find('h2').text
            translated_title = translate_to_russian(title)
            link = news_element.find('a')['href']
            if is_news_in_db(link, collection_name):
                continue

            date = extract_date(link)
            if date is None:
                continue

            news_data = {
                'title': translated_title,
                'link': f'{link}',
                'date': date
            }
            add_news_to_db(news_data, collection_name)
            news_list.append(news_data)


            print('Данные успешно загружены в cnbc.json.')
        else:
            print('Новых новостей для cnbc не найдено.')

    else:
        print(f'Ошибка парсинга страницы cnbc. Status code: {response.status_code}')

run()
