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
   print(book_url)
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
      #return json.dumps(book_info, sort_keys=False, indent=4)
      return book_info
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


# def get_book_url(website_url, main_html):
#    # return book full url
#    content = main_html.find('div', class_='image_container')
#    get_link = content.find('a')['href']
#    if 'http' not in get_link:
#       url = '{}{}'.format(website_url, get_link)
#       return url
#    return False

def get_all_books_url(website_url, category_url):
   html = html_parser(category_url)
   category_tmp = category_url[:36]

   # return book full url
   content = html.findAll('ol', class_='row')
   temp_links = []
   for div in content:
      # product container
      divs = div.findAll('div', class_='image_container')
      for a in divs:
         # get book links
         hlinks = a.findAll('a', href= True)
         for link in hlinks:
            temp_links.append(link['href'])

   links = []
   for link in temp_links:
      # modifies the links since url isn't complete
      if 'http' not in link:
         tmp_url = link[8:]
         book_url = '{}{}'.format(category_tmp ,tmp_url)
         links.append(book_url)
  
   return links
   

def get_category_url(website_url, main_html):
   content = main_html.find('ul', class_='nav-list')
   get_link = content.findAll('a')
   links = []
   for link in get_link:
      if 'http' not in link:
         url = '{}{}'.format(website_url, link['href'])
         links.append(url)
   return links

import csv
def save_csv(book):
   # create csv file with book data
   header = [
      'product_page_url',
      'universal_product_code',
      'title',
      'price_including_tax',
      'price_excluding_tax',
      'number_available',
      'product_description',
      'category',
      'review_rating',
      'image_url'
   ]
   # save information to csv file
   with open('misc/csv/%s.csv'% book['category'], 'a', newline='') as output_file:
      writer = csv.DictWriter(output_file, fieldnames=header)
      writer.writeheader()
      writer.writerow(book)
   
# ================================      main    ================================ #

website_url = 'https://books.toscrape.com/'

# parse content to html
main_html = html_parser(website_url)

#book url
#book_url = get_book_url(website_url, main_html)
#print('Book Information : ',get_book_info(book_url))


category_url = get_category_url(website_url, main_html)
#print('CAT', category_url)
books_link = get_all_books_url(website_url,category_url[2])
#print(get_book_info(books_link[2]))
for book in  books_link:
   data = get_book_info(book)
   save_csv(data)

