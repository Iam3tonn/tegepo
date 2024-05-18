def run():
    import requests
    from bs4 import BeautifulSoup
    from googletrans import Translator
    from datetime import datetime
    import json
    from mongodb import is_news_in_db, add_news_to_db, remove_old_news

    collection_name = 'tribunnews'

    def get_news(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('li', class_='p1520 art-list pos_rel')

        news_list = []
        translator = Translator()

        for item in news_items:
            title_tag = item.find('h3')
            if title_tag and title_tag.a:
                original_title = title_tag.a.get_text(strip=True)
                translated_title = translator.translate(original_title, src='id', dest='ru').text
                link = title_tag.a['href']

                time_tag = item.find('time', class_='foot timeago')
                if time_tag:
                    news_time = datetime.strptime(time_tag['title'], '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y %H:%M')
                else:
                    news_time = 'Time not available'

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

    news_url = 'https://bali.tribunnews.com/news'
    latest_news = get_news(news_url)

    print("tribunnews completed")

run()
