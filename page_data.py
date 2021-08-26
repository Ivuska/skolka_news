import requests
import xmltodict

from send_email import send_me_email


response = requests.get('https://www.msvinicna.cz/?feed=rss2')
dict_data = xmltodict.parse(response.content)

def get_articles_from_page(dict_data):
    rss = dict_data['rss']
    rss_article_channel = rss['channel']

    rss_article_item = rss_article_channel['item']
    articles =[]

    for article in rss_article_item:
        article = [article['title'], article['link'], article['content:encoded']]
        articles.append(article)

    # Returns list of lists. Each list consists of two items - article title and link. 
    return articles


def get_new_articles():
    reversed_articles_list = get_articles_from_page(dict_data)
    reversed_articles_list.reverse()
    with open("id.txt") as id_file:
        id = int(id_file.read())

    for article in reversed_articles_list:
        header = article[0]
        url = article[1]
        content = article[2]
        article_id = int(article[1][-4:])
        if article_id > 3800:
            print(article_id)
            send_me_email(header, url, content)
            set_id(article_id)
    
def set_id(id):
    with open("id.txt","w") as id_file:
        id_file.write(str(id))

if __name__ == '__main__':
    get_new_articles()