def run():
    import requests
    from bs4 import BeautifulSoup
    import datetime
    import json
    from googletrans import Translator
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news
    import pytz

    url = "https://www.infodenpasar.id"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        news_elements = soup.find_all('div', class_='td_module_column')
        data_list = []
        translator = Translator()
        collection_name = 'infodenpasar'
        
        remove_old_news(collection_name)
        end_date = datetime.datetime.now(pytz.utc)  # текущая дата и время в UTC
        start_date = end_date - datetime.timedelta(days=3)  # последние 3 дня

        for news_element in news_elements:
            title_element = news_element.find('h3', class_='entry-title td-module-title')
            title = title_element.text.strip() if title_element else "Нет заголовка"

            translated_title = translator.translate(title, src='auto', dest='ru').text
            link = title_element.a['href'] if title_element and title_element.a else "Нет ссылки"
            date_element = news_element.find('time', class_='entry-date')
            date = date_element['datetime'] if date_element else "Нет даты"

            try:
                if date != "Нет даты":
                    datetime_obj = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=pytz.utc)
                    formatted_date = datetime_obj.strftime('%d %B %Y %H:%M')
                else:
                    formatted_date = "Нет даты"
            except ValueError:
                formatted_date = "Нет даты (неверный формат)"

            if date != "Нет даты" and datetime_obj >= start_date:
                if is_news_in_db(link, collection_name):
                    continue

                news_data = {
                    "title": translated_title,
                    "link": link,
                    "date": formatted_date
                }

                add_news_to_db(news_data, collection_name)
                data_list.append(news_data)

        print("Данные сохранены в файл 'infodenpasar.json'.")
    else:
        print(f"Ошибка при получении страницы infodenpasar. Код статуса: {response.status_code}")

run()
