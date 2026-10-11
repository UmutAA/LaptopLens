import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        ' like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
}

def save_html(html, path):
    try:
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

def get_html_pages(base_url, path_prefix, pages=3, page_indicator='page'):
  """Loops for pages times and saves each one to a different file"""
  for page in range(1, pages + 1):
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

def parse_all_pages(path_prefix, pages):
  all_item_links = []

  for page in range(1, pages + 1):
    file_path = f'{path_prefix}_{page}.html'
    print(f'\n{file_path} okunuyor...')
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

def parse_product_details(item_links):
    items = []
    print('\nParsing product page...')
    for index, link in enumerate(item_links, 1):
        print(f'{index}. Link: {link}')
        detail_resp = requests.get(link, headers=HEADERS)
        if detail_resp.status_code == 200:
            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')

            try:
                h1 = detail_soup.find('h1', class_='text-title-lg text-neutral-600')
                item_name = h1.get_text(strip=True)
                item_price = 0
                price_tag = detail_soup.find('span', class_='text-title-md text-neutral-500')
                if price_tag:
                    item_price = price_tag.get_text(separator=' ', strip=True)
                item_price = item_price.replace(' TL', '')
                item_price = item_price.replace('.', '')
                item_price = item_price.replace(',', '.')
                item_price = float(item_price)

                items.append({"Link": link, "Name": item_name, "Price": item_price})

            except AttributeError:
                print("Could not resolve elements")

        time.sleep(0.5)

    if items:
        df = pd.DataFrame(items)
        df.to_csv('../data/products_raw.csv', index=False, encoding='utf-8-sig')
        print("Process completed! Datas have been saved to 'products.csv' file")
    else:
        print('\nNo products found')


url = 'https://www.idefix.com/gaming-notebook-laptop-c-230881904'
html_path = '../categories/categories'
total_pages = 1

get_html_pages(url, html_path, pages=total_pages, page_indicator='sayfa')

all_links = parse_all_pages(html_path, pages=total_pages)

if all_links:
  parse_product_details(all_links)