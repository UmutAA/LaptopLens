import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import os

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        ' like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.idefix.com/',
    'Connection': 'keep-alive',
}

def save_html(html, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding="utf-8") as f:
            f.write(html)

    except IOError:
        print("File not found")

    except UnicodeDecodeError:
        print("File not decoded")

    except UnicodeEncodeError:
        print("File not encoded")

    except Exception as e:
        print(e)


def open_html(path):
    try:
        with open(path, 'r', encoding="utf-8") as f:
            html = f.read()
            return html

    except IOError:
        print("File not found")
    except UnicodeDecodeError:
        print("File not decoded")
    except UnicodeEncodeError:
        print("File not encoded")
    except Exception as e:
        print(e)

def get_html_pages(base_url, path_prefix, start_page=1, end_page=3, page_indicator='page'):
  """Loops for pages times and saves each one to a different file"""
  for page in range(start_page, end_page + 1):
    url = base_url + f'?{page_indicator}={page}'
    print('Attempting to open ' + url)
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
      print('Error code: ' + str(response.status_code))
      continue

    print('Successfully opened ' + url)
    file_path = f'{path_prefix}_{page}.html'
    print('Saving HTML to ' + file_path)
    save_html(response.text, file_path)
    time.sleep(0.5)

def parse_all_pages(path_prefix, start_page=1, end_page=3):
  all_item_links = []

  for page in range(start_page, end_page + 1):
    file_path = f'{path_prefix}_{page}.html'
    print(f'\nReading {file_path}')
    html = open_html(file_path)

    if not html:
      continue

    soup = BeautifulSoup(html, 'html.parser')
    link_elements = soup.find_all(
        'a', class_='absolute inset-0 z-30 h-full w-full cursor-pointer'
    )

    page_links = []
    for element in link_elements:
      link = element.get('href')
      if link:
        if not link.startswith('http'):
          full_link = 'https://www.idefix.com' + link
        else:
          full_link = link
        page_links.append(full_link)

    print(f'Found {len(page_links)} links in this page.')
    all_item_links.extend(page_links)

  print(f'\nTotal {len(all_item_links)} links found across all pages.')
  return all_item_links



url = 'https://www.idefix.com/gaming-notebook-laptop-c-230881904'
html_path = '../categories/categories'

START_PAGE = 13
END_PAGE = 13

get_html_pages(url, html_path, start_page=START_PAGE, end_page=END_PAGE, page_indicator='sayfa')

all_links = parse_all_pages(html_path, start_page=START_PAGE, end_page=END_PAGE)

if all_links:
  parse_product_details(all_links)