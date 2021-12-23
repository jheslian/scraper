import re
from bs4 import BeautifulSoup as bs
import requests
import json

def html_parser(url):
   # parse url to html
   # param: url - website url to scrape
   response = requests.get(url).content
   soup = bs(response, 'html.parser')
   return soup

def get_book_info(book_url):
   # book information
   html_book_content = html_parser(book_url)  
   info = product_info(html_book_content)

   book_info = {
      # 1. product page url
      'product_page_url' : book_url,
      # 2. universal product code (upc)
      'universal_product_code' : info['UPC'],
      # 3. title
      'title' : get_book_title(html_book_content),
      # 4. price_including_tax
      'price_including_tax' : info['Price (incl. tax)'],
      # 5. price_excluding_tax'
      'price_excluding_tax' : info['Price (excl. tax)'],
      # 6. number_available
      'number_available' : get_stock_number(info['Availability']),
      # 7. product description
      'product_description' : get_book_description(html_book_content),
      # 8. category
      'category' : get_book_category(html_book_content),
      # 9. review_rating - class="star-rating One”
      'review_rating' : get_rating(html_book_content),
      # 10. image_url 
      'image_url' : get_book_url_image(book_url, html_book_content)
   }
   if book_info:
      return json.dumps(book_info, sort_keys=False, indent=4)
   return False

def get_stock_number(content):
   # stock available
   stock = re.sub(r'[()]','', content).split()
   return stock[2]

def product_info(html_book_content):
   # get product information: UPC, prices, stock availability
   content = html_book_content.findAll('tr')   
   info = {}
   for i in content:
      info[i.findChildren()[0].text] = i.findChildren()[1].text 
   
   return info

def get_rating(html_book_content):
   content = html_book_content.find('p', class_='star-rating')
   stars = content['class'][-1]
   # rating view
   rating = {
      'One' : 1,
      'Two' : 2,
      'Three' : 3,
      'Four' : 4,
      'Five' : 5
   }
   if stars in rating:
      return rating[stars]

   return False

def get_book_description(html_book_content):
   # book description
   description = html_book_content.find('p', class_=False, id=False)
   return description.string


def get_book_title(html_book_content):
   # book title
   title = html_book_content.title.text
   return title.strip()


def get_book_category(html_book_content):
   # book category
   category = html_book_content.find('ul', class_='breadcrumb')
   a = category.findChildren()[4]
   return a.text.strip()


def get_book_url_image(book_url, html_book_content):
   # image url
   url_image = html_book_content.find('img', class_=False, id=False)
   if url_image.has_attr('src'):
      filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', url_image['src'])     
      if filename and 'http' not in url_image['src']:
         # modify image url
         img = url_image['src'][6:]
         url = '{}{}'.format(book_url, img)   
         return url
      else:
         # if image extension doesn't exist
         print("Error filename: {}".format(url_image['src']))
         return False


def get_book_url(content):
   # return book full url
   content = main_html.find('div', class_='image_container')
   get_link = content.find('a')['href']
   if 'http' not in get_link:
      url = '{}{}'.format(website_url, get_link)
      return url
   return False


# ================================      main    ================================ #

website_url = 'https://books.toscrape.com/'

# parse content to html
main_html = html_parser(website_url)

#book url
book_url = get_book_url(website_url)
print('Book Information : ',get_book_info(book_url))