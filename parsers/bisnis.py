def run():
    import requests
    import json
    from bs4 import BeautifulSoup
    from googletrans import Translator
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news

    collection_name = 'bisnis'

    def remove_day_from_date(date_string):
        date_string = date_string.replace("Selasa,", "").replace("|", "").strip()
        if ',' in date_string:
            date_string = date_string.split(',', 1)[1].strip()
        return date_string

    def translate_to_russian(text):
        translator = Translator()
        translation = translator.translate(text, dest='ru')
        return translation.text

    url = "https://bisnis.com"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_block = soup.find('div', class_='list-news')
        if not news_block:
            news_titles = soup.find_all('h2')
        else:
            news_titles = news_block.find_all('h2')

        news_list = []
        remove_old_news(collection_name)

        for title in news_titles:
            news_link_tag = title.find('a')
            if news_link_tag:
                news_link = news_link_tag['href']
                if is_news_in_db(news_link, collection_name):
                    continue

                news_response = requests.get(news_link)
                if news_response.status_code == 200:
                    news_soup = BeautifulSoup(news_response.text, 'html.parser')
                    date_element = news_soup.find('div', class_='detailsAttributeDates')
                    if date_element:
                        news_date = remove_day_from_date(date_element.get_text(strip=True))
                        news_text = translate_to_russian(news_link_tag.get_text(strip=True))
                        news_item = {
                            "title": news_text,
                            "link": news_link,
                            "date": news_date
                        }
                        add_news_to_db(news_item, collection_name)
                        news_list.append(news_item)

        print("Данные успешно записаны в файл bisnis.json")
    else:
        print(f"Ошибка: {response.status_code}")

run()
