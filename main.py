import os
import re
from bs4 import BeautifulSoup as bs
import requests
from queue import Queue
import threading
import time
import concurrent.futures

exitFlag = 0
no_threads = 50
threadlist=[]

for t in range(1, no_threads):
   threadlist.append(t)

queueLock = threading.Lock()
workQueue = Queue(100)
threads = []
threadID = 1
   

def html_parser(url):
   # parse url to html
   # param: url - website url to scrape
   response = requests.get(url)
   soup = bs(response.content, 'html.parser')
   return soup

def get_book_info(book_url):
   # book information and download book image
   print('Sraping url : ', book_url)
   html_book_content = html_parser(book_url)
   download_book_image(get_book_url_image(book_url, html_book_content))
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
   if description:
      return description.string
   else: 
      return False   


def get_book_title(html_book_content):
   # book title
   title = html_book_content.title.text
   return title.strip()


def get_book_category(html_book_content):
   # book category
   category = html_book_content.find('ul', class_='breadcrumb')
   content = category.findChildren()[4]
   if content:
      return content.text.strip()
   else:
      return False

def get_book_url_image(book_url, html_book_content):
   # image url
   url_image = html_book_content.find('img', class_=False, id=False)
   if url_image.has_attr('src'):
      filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', url_image['src'])
      if filename and 'http' not in url_image['src']:
         # modify image url
         img = url_image['src'][6:]
         url = '{}{}'.format(book_url[:27], img)
         return str(url)
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
def get_next_page(url):
   # retrieve all url of all pages existing
   tmp = url[:-10]
   category_url = [url] 
   while True:
      html = html_parser(category_url[-1])
      next_page = html.find('li', class_='next')
      if next_page:
         link = next_page.find('a')
         working_url = requests.get('{}{}'.format(tmp, link['href']))
         if working_url.status_code == 200:  
            category_url.append('{}{}'.format(tmp, link['href']))
         else:
            break   
      else:
         break   

   return category_url


def get_tmp_books_urls(url):
   # return all value foun in href in each books
   html = html_parser(url)
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

   return temp_links

def get_all_books_url(category_url):
   
   # https://books.toscrape.com/catalogue
   category_tmp = category_url[:36]

   temp_links = []
   # If next page 
   next_page_urls = get_next_page(category_url)
   if next_page_urls:
      for url in next_page_urls:
         temp_links.extend(get_tmp_books_urls(url))
   else:
      get_tmp_books_urls(category_url)

   # working urls
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
   filename = 'misc/csv/%s.csv' % book['category']

   if os.path.isfile(filename):
      with open(filename, 'a', newline='') as output_file:
         writer = csv.DictWriter(output_file, fieldnames=header)
         writer.writerow(book)
   else: 
      with open(filename, 'w') as output_file:
         writer = csv.DictWriter(output_file, fieldnames=header)
         writer.writeheader()
         writer.writerow(book)      


def download_book_image(book_image_url):  
   # download image to misc/images/
   # get image file name
   img = str(book_image_url[45:]) 
   with open('misc/images/'+ str(img), 'wb') as f:
      response = requests.get(book_image_url)
      return f.write(response.content)

# ================================      main    ================================ #
"""
book information extraction on each category present
"""

"""
create misc folder with 2 sub folder:
1. csv folder - which will contain csv files for the scrape data
2. images folder - which contains images of each book
"""
import os
folders = ['misc', "misc/csv", "misc/images"]
for folder in folders:
   if not os.path.exists(folder):
      os.mkdir(folder)
   

################################### version 1 : 20 min ###################################
"""
try:
   website_url = 'https://books.toscrape.com/'
   main_html = html_parser(website_url)
   category_url = get_category_url(website_url, main_html)
   for category in category_url[1:]:
      books_link = get_all_books_url(category)
      for book_url in  books_link:
         print('data collection : ', book_url)
         data = get_book_info(book_url)
         save_csv(data)       
   print('collection of data and download image was successfull')      
except:
   print('Unexpected error!')  
"""

################################### version 2 : 5 min ###################################
"""
categories =[]

try:
   website_url = 'https://books.toscrape.com/'
   main_html = html_parser(website_url)
   category_url = get_category_url(website_url, main_html)
   
   for url in category_url[1:]:
      categories.append(url)

   print('Collection of data and download image was successfull')      
except:
   print('Unexpected error!')  

class myThread (threading.Thread):
   def __init__(self, threadID, name, q):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.q = q
   def run(self):
      print("Starting " + self.name)
      process_data(self.name, self.q)
      print("Exiting " + self.name)

def process_data(q):
   while not exitFlag:
      queueLock.acquire()
      if not workQueue.empty():
         data = q.get()
         queueLock.release()
         books_link = get_all_books_url(data)
         for book_url in  books_link:
            print('data collection : ', book_url)
            try:
               data = get_book_info(book_url)
               save_csv(data) 
            except:
               print("erreur")   
      else:
         queueLock.release()
      time.sleep(1)


# Create new threads
tic = time.perf_counter() # Start Time
for tName in threadlist:
   thread = myThread(threadID, tName, workQueue)
   thread.start()
   threads.append(thread)
   threadID += 1

# Fill the queue
queueLock.acquire()
for word in categories:
   workQueue.put(word)
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
   pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
   t.join()

toc = time.perf_counter() # End Time 
print(f"Build finished in {(toc - tic)/60:0.0f} minutes {(toc - tic)%60:0.0f} seconds")   

"""

################################### version 3 : 3 min ###################################

def scrape(category_url): 
   books_link = get_all_books_url(category_url)
   for book_url in  books_link:
      try:
         data = get_book_info(book_url)
         save_csv(data) 
      except Exception as e:
         print(f"Error has occur on this url: {book_url}")

tic = time.perf_counter() # Start Time
try:
   website_url = 'https://books.toscrape.com/'
   main_html = html_parser(website_url)
   category_url = get_category_url(website_url, main_html)
   with concurrent.futures.ThreadPoolExecutor() as executor:
      executor.map(scrape, category_url[1:])
   print('Collection of data and download image was successfull')      
except:
   print('Unexpected error!')  
toc = time.perf_counter() # End Time 
print(f"Build finished in {(toc - tic)/60:0.0f} minutes {(toc - tic)%60:0.0f} seconds")