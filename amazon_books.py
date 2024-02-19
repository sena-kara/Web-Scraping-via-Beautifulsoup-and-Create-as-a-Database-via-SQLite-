# With Python Beautiful Soup, we will extract the book name, author, review score and price information 
 #from the best-selling books category on the Amazon website and save it to the SQLite database.


# We will import SQLite3 to save the data we extracted in Python to SQLite.
# We will also import the request that will send a request to the website to retrieve the data.
# We will import the Beautiful Soup library to scrape data from the Amazon website.
# and we will save the studies in JSON format;

import sqlite3
import requests
from bs4 import BeautifulSoup
import json

# Extracting data from mighty websites- such as Amazon- is not always possible due to the precautions the site takes against bots.
  # Therefore, we will assign a user-agent.
headers_param = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

# For save information about books in the database; 
 # to create a table named "book" and insert new book information into table;
def create_books_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        price TEXT,
        rating TEXT
    )
    """)
    connection.commit()

def insert_book(connection, book):
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO books (title, author, price, rating) VALUES (?, ?, ?, ?)
    """, book)
    connection.commit()

def scrape_amazon_books(kitap, page_count):
    all_books_info = []
 
 # To return each page that we want to extract information;
    for page in range(1, page_count + 1):
        url = f"https://www.amazon.com.tr/gp/bestsellers/books/ref=zg_bs_nav_books"

# To get the content of the Amazon web page and parse it down via BeautifulSoup library;
        response = requests.get(url, headers=headers_param)
        soup = BeautifulSoup(response.content, "html.parser")

        book_containers = soup.find_all("div", class_="a-column a-span12 a-text-center _cDEzb_grid-column_2hIsc")
        if not book_containers:
            print(f"No books found on page {page}.")
            break
        
        for container in book_containers:

            # Book title
            book_title = container.find("div", class_="_cDEzb_p13n-sc-css-line-clamp-1_1Fn1y")
            book_title_text = book_title.get_text(strip=True) if book_title else "Bilgi bulunamadı"

            # Author
            author = container.find("span", class_="a-size-small a-color-base")
            author_text = author.get_text(strip=True) if author else "Bilgi bulunamadı"

            # Price
            price = container.find("span", class_="a-size-base a-color-price")
            price_text = price.get_text(strip=True) if price else "Ürün stokta yok"
            
            # Rating (Out of 5 Stars)
            evaluation_score = container.find("i", class_="a-star-small-5")
            evaluation_score_text = evaluation_score.get_text(strip=True) if evaluation_score else "Ürün henüz değerlendirilmedi"

            # Save all info as a tuple
            book_info = (book_title_text, author_text, price_text, evaluation_score_text)
            all_books_info.append(book_info)

    return all_books_info


def save_books_to_json(Amazon_books_info):
    with open("Amazon_books_info.json", "w", encoding="utf-8") as json_file:
        json.dump(Amazon_books_info, json_file, ensure_ascii=False, indent=4)


def main():
    kitap = "kitap"
    page_count = 50  # For first 50 pages

    # To create the SQLite database connection with a file named "Amazon_books.db";
    connection = sqlite3.connect("Amazon_books.db")
    
    # To create table;
    create_books_table(connection)

    # To scrape all books and add them to database;
    all_books = scrape_amazon_books(kitap, page_count)
    for book in all_books:
        insert_book(connection, book)
    
    # To save all informations as JSON format;
    save_books_to_json(all_books)

    # To close the database connection;
    connection.close()

    print("Kitap bilgileri veritabanına başarıyla kaydedildi.")

if __name__ == "__main__":
    main()