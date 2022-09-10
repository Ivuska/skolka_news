import requests
import xmltodict

from send_email import *


response = requests.get('https://www.msvinicna.cz/?feed=rss2')
dict_data = xmltodict.parse(response.content)

# We store the id of the last article in id.txt.
def get_id():
  with open("id.txt") as id_file:
      id = int(id_file.read())
      return id

def set_new_id(id):
  with open("id.txt","w") as id_file:
      id_file.write(str(id))

def get_articles_from_rss(dict_data):
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
  reversed_articles_list = get_articles_from_rss(dict_data)
  reversed_articles_list.reverse()
  old_id = get_id()

  for article in reversed_articles_list:
    header = article[0]
    url = article[1]
    content = article[2]
    #link_to_menu = article[]
    article_id = int(url[-4:])

    if article_id >= 4140:
      #print(header)
      #print(article_id)

      if 'Jídelníček' in header or 'Jídelní lístek' in header:
        send_email_with_content_to_download(header, url, content)
      else:
        send_email_with_content(header, url, content)

      set_new_id(article_id)
    
if __name__ == '__main__':
  get_new_articles()