import requests
import xmltodict
import os

from send_email import *


response = requests.get('https://www.msvinicna.cz/feed')
dict_data = xmltodict.parse(response.content)

worker_url = os.environ.get('WORKER_URL')

def get_id():
  response = requests.get(worker_url + '/last_id', headers={ 'X-Auth-Token': os.environ.get('WORKER_AUTH_TOKEN')} )

  if response.status_code != 200:
    raise RuntimeError(f'Unexpected error when retireving last id, worker response { response.status_code} {response.text}.')
  last_id = response.json()['last_id']
  print(f'Received last id is {last_id}.')
  return last_id

def set_new_id(id):
  response = requests.post(worker_url + '/last_id', json={'last_id':id}, headers={ 'X-Auth-Token': os.environ.get('WORKER_AUTH_TOKEN')})
  if response.status_code != 200:
    raise RuntimeError(f'Unexpected error when updating last id, worker response { response.status_code} {response.text}.')

def get_articles_from_rss(dict_data):
  rss = dict_data['rss']
  rss_article_channel = rss['channel']

  rss_article_item = rss_article_channel['item']
  articles =[]

  for article in rss_article_item:
    article = [article['title'], article['link'], article['content:encoded'], article['guid']]
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
    article_id = int(article[3]['#text'].split('=')[1])
    print(article_id)

    if article_id > old_id:
      print(header)
      print(article_id)

      if 'Jídelníček' in header or 'Jídelní lístek' in header or 'Jidelní lístek' in header:
        send_email_with_content_to_download(header, url, content)
      else:
        send_email_with_content(header, url, content)

      set_new_id(article_id)
    
if __name__ == '__main__':
  get_new_articles()
