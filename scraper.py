from bs4 import BeautifulSoup
from pathlib import Path
from itertools import count
from functools import partial

import traceback
import multiprocessing as mp
import requests
import csv
import re

def fetch_html(n_page):
  url = f'https://bina.az/baki/alqi-satqi/menziller?page={n_page}'
  print(url)

  r = requests.get(url)
  return r.content

def fetch_item_html(item_id):
  url = f'https://bina.az/items/{item_id}'
  print('readign item', url)

  r = requests.get(url)
  return r.content

def parse_item(id, csv_writer):
  html = fetch_item_html(id)
  soup = BeautifulSoup(html, 'lxml')

  price_val = int(soup.select_one('.price-val').get_text().replace(' ', ''))
  price_cur = soup.select_one('.price-cur').get_text().strip()

  params = [tr.contents[1] for tr in soup.find_all('tr')]

  floor_parts = params[1].get_text().split('/')

  new_build = 'Yeni' in params[0].get_text()
  floor = int(floor_parts[0].strip())
  max_floors = int(floor_parts[1].strip())

  area = float(params[2].get_text().strip().split(' ')[0])

  rooms = params[3].get_text()
  heating = params[4].get_text() == 'var'

  badge_tags = soup.select('ul.locations > li > a')
  badges = [badge_tag.get_text().strip() for badge_tag in badge_tags]

  map_tag = soup.select_one('img[alt="Map"]')
  search = re.search('(\d+\.\d+)%2C(\d+\.\d+)', map_tag['data-src'])

  lat = float(search.group(1))
  lon = float(search.group(2))

  csv_writer.writerow([id, price_val, price_cur, new_build, floor, 
                       max_floors, area, rooms, heating, 
                       ','.join(badges), lat, lon])

def parse_page(i, csv_writer):
  html = fetch_html(i)
  soup = BeautifulSoup(html, 'lxml')

  items = [item['data-item-id'] for item in soup.select('div[data-item-id]')]

  for item in items:
    try:
      parse_item(item, csv_writer)
    except Exception as e:
      print('Skipping', item, 'because', e)
      traceback.print_stack()

def main():
  with open('data/output.csv', 'a') as csv_file:
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(['id', 'price_val', 'price_cur', 'new_build', 'floor', 'ax_floors', 
                        'area', 'rooms', 'heating', 'badges', 'lat', 'lon'])

    try:
      for i in range(12, 690):
        parse_page(i, csv_writer)
        csv_file.flush()
    except Exception as e:
      print('Exception', e)
      traceback.print_stack()
    finally:
      pass

if __name__ == '__main__':
  main()
