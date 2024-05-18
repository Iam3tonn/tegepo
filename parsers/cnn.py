def run():
    import requests
    from bs4 import BeautifulSoup
    from googletrans import Translator
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news

    collection_name = 'cnn'

    def translate_to_russian(text):
        translator = Translator()
        translation = translator.translate(text, dest='ru')
        return translation.text if translation.text else text

    def extract_date_from_article_page(article_url):
        month_mapping = {
            'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April', 'Mei': 'May', 'Jun': 'June',
            'Jul': 'July', 'Agu': 'August', 'Sep': 'September', 'Okt': 'October', 'Des': 'December'
        }

        response = requests.get(article_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            date_element = soup.find('div', class_='text-cnn_grey text-sm mb-4')
            if date_element:
                date_text = date_element.text.strip().split(' ', 1)[1].rsplit(' ', 1)[0]
                for month_short, month_full in month_mapping.items():
                    date_text = date_text.replace(month_short, month_full)
                return date_text
        return None

    url = 'https://www.cnnindonesia.com'
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_elements = soup.select('.flex.flex-col.gap-5.nhl-list article.flex-grow')
        news_list = []
        remove_old_news(collection_name)

        for news_element in news_elements:
            title_element = news_element.find('h2')
            if title_element:
                title = title_element.text.strip()
                translated_title = translate_to_russian(title)
                link = news_element.find('a')['href']

                if is_news_in_db(link, collection_name):
                    continue

                date = extract_date_from_article_page(link)
                if date is not None:
                    news_data = {
                        'title': translated_title,
                        'link': link,
                        'date': date
                    }
                    add_news_to_db(news_data, collection_name)
                    news_list.append(news_data)

    else:
        print(f'Ошибка парсинга cnn.json: {response.status_code}')

run()
