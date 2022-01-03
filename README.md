# Scraper
### A beta version of this system to track the book prices at [Books to Scrape](http://books.toscrape.com/) 
## Goal:
An application to retrieve the following data at the time of execution:
 - product page url 
 - universal product code (upc) 
 - title 
 - price including tax 
 - price excluding tax 
 - number available
 - product description 
 - category 
 - review rating 
 - image url
 - book image

## Getting started:
**Note**: Make sure python3 is installed in your machine : "python -V" and verify that you have the venv module : "python -m venv --help" if not please check https://www.python.org/downloads/:
 1. Clone the repository https://github.com/jheslian/scraper.git on the terminal or command prompt
 2. Create a virtual environment with "venv"  
	 - cd scaper :  to access the folder 
	 - python -m venv ***environment name*** : to create the virtual environment - exemple: "python -m venv env" 
3. Activate the virtual environment:
	for unix or macos:
	- source ***environment name***/bin/activate - ex : "source env/bin/activate" if "env" is used as environment name 
	for windows:
	- ***environment name***\Scripts\activate.bat - ex: "env\Scripts\activate.bat"
4. Install the packages with pip: pip install -r requirements.txt	
6. Run the program with : python3 main.py

***Without any connection problem at the end of the program you should have:***

 - an **"csv"** folder under misc folder which contains 50 csv files with book category name on each file containing the data of each book under that categotry
 - an **"images"** folder under misc folder which contains 1000 images since there are 1000 books books on the gallery/site
