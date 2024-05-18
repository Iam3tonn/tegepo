def run():
    import re
    import requests
    from bs4 import BeautifulSoup
    from googletrans import Translator
    import datetime
    import pytz
    import logging
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news
    import json

    logging.basicConfig(filename='news_parser.log', level=logging.INFO, 
                        format='%(asctime)s %(levelname)s %(message)s')

    collection_name = 'balisun'

    def get_article_details(article_url):
        article_response = requests.get(article_url)
        if article_response.status_code == 200:
            article_soup = BeautifulSoup(article_response.text, 'html.parser')

            description_element = article_soup.find('meta', property='og:description')
            description = description_element['content'] if description_element else ''

            date_element = article_soup.find('meta', property='article:published_time')
            date_published = date_element['content'] if date_element else ''

            formatted_date = ''
            if date_published:
                datetime_obj = datetime.datetime.fromisoformat(date_published)
                utc_timezone = pytz.timezone('UTC')
                datetime_obj_utc = datetime_obj.replace(tzinfo=pytz.utc)
                formatted_date = datetime_obj_utc.astimezone(utc_timezone).strftime('%d %B %Y %H:%M')

            article_text = ' '.join([p.get_text() for p in article_soup.find_all('p')])

            pattern_to_remove = "Posted on Published: [^\n]+"
            article_text = re.sub(pattern_to_remove, '', article_text)
            article_text = article_text.replace("\n\t\tShare The Article\t", "")

            start_index = article_text.find("Book The Best")
            if start_index != -1:
                article_text = article_text[:start_index]

            return {'description': description, 'date': formatted_date, 'text_content': article_text}
        else:
            logging.error(f'Error accessing article page: {article_url}')
            return {'description': '', 'date': '', 'text_content': ''}

    url = 'https://thebalisun.com'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        translator = Translator()

        remove_old_news(collection_name)

        for article in soup.find_all('article'):
            title_element = article.find('h2')
            if title_element:
                title = title_element.text.strip()
                translated_title = translator.translate(title, src='en', dest='ru').text
                link = article.find('a')['href']

                if is_news_in_db(link, collection_name):
                    continue

                article_details = get_article_details(link)
                article_details['text_content'] = article_details['text_content'][1:]
                translated_description = translator.translate(article_details['description'], src='en', dest='ru').text

                news_item = {'title': translated_title, 'link': link,
                             'description': translated_description,
                             'date': article_details['date'],
                             'text_content': article_details['text_content']}
                
                add_news_to_db(news_item, collection_name)
                news_items.append(news_item)

        logging.info('Данные успешно записаны balisun')
    else:
        logging.error('Ошибка при выполнении запроса к странице')

run()
