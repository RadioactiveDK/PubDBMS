from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime, timedelta

def connectDB(cursor):
    try:
        cursor.execute("USE {}".format(DB_NAME))
        print('\n\tConnection established!!!\n')
    except mysql.connector.Error as err:
        print("Database {} does not exist".format(DB_NAME))
        exit(1)

def table_exists(cursor, table_name):
    try:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if cursor.fetchone():
            return True
        else:
            print('Table does not exist.')        
    except Error as e:
        return False

def sign_up(username, password, table):
    cursor = cnx.cursor()

    try:
        query = f"SELECT * FROM {table} WHERE {table[:-1]}_username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if user:
            print("\tError: Username already exists.\n")
        else:
            insert_query = f"INSERT INTO {table} ( {table[:-1]}_username,  {table[:-1]}_password) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, password))

            cnx.commit()

            print("\tSign-up successful!\n")
    except Error as err:
        print(f"Error: {err}")
        
def log_in(username, password, table):
    try:
        query = f"SELECT * FROM {table} WHERE  {table[:-1]}_username = %s AND  {table[:-1]}_password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            print("\tLog-in successful!\n")
            session(table,username)
        else:
            print("\tLog-in failed. Invalid username or password.\n")
    except Error as e:
        print("Error")

def publish_request_as_author(table,username):
    if table == 'authors':
        try:
            book_title = input("Enter the book title: ")
            auth_username = username
            pub_username = input("Enter the publisher's username: ")

            # Insert values into the 'requests' table
            query = "INSERT INTO requests (book_title, author_username, publisher_username) VALUES (%s, %s, %s)"
            values = (book_title, auth_username, pub_username)

            cursor.execute(query, values)
            cnx.commit()

            print("\tRequest pending...")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    else:
        print('You do not have access.')

def view_requests_as_author(table, username):
    if table!='authors':
        print('You do not have access.')
        return
    try:
        query = f"SELECT * FROM requests WHERE author_username = '{username}';"
        cursor.execute(query)
        result = cursor.fetchall()
        print("Requests as an author:")
        for row in result:
            print(row)
    except Error as e:
        print(f"Error: {e}")

def view_requests_as_publisher(table, username):
    if table!='publishers':
        print('You do not have access.')
        return
    try:
        query = f"SELECT * FROM requests WHERE publisher_username = '{username}';"
        cursor.execute(query)
        result = cursor.fetchall()
        print("Requests as a publisher:")
        for row in result:
            print(row)
    except Error as e:
        print(f"Error: {e}")

def approve_request_as_publisher(table, username):
    if table!='publishers':
        print('You do not have access.')
        return
    try:
        author_name = input("Enter the author name: ")
        book_title = input("Enter the book title: ")
        query = f"UPDATE requests SET request_status = 'approved' WHERE author_username = '{author_name}' AND book_title = '{book_title}' AND publisher_username = '{username}';"
        cursor.execute(query)
        cnx.commit()
        print("Request approved successfully as a publisher.")
    except Error as e:
        print(f"Error: {e}")

def insert_keyword_as_author(table, username):
    if table!='authors':
        print('You do not have access.')
        return
    
    book_title = input("Enter the book title: ")
    get_book_id_query = "SELECT book_id FROM books WHERE book_title = %s LIMIT 1"
    cursor.execute(get_book_id_query, (book_title,))
    book_id_result = cursor.fetchone()

    if book_id_result:
        keyword = input("Enter a keyword: ")
        book_id = book_id_result[0]
        fill_keyword_query = "CALL fill_keyword(%s, %s)"
        cursor.execute(fill_keyword_query, (book_id, keyword))
        print("Keyword added successfully!")
        cnx.commit()
    else:
        print("Book not found.")

def view_all_books():
    view_books_query = "SELECT * FROM books"
    cursor.execute(view_books_query)
    books = cursor.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No books found.")

def search_using_keyword():
    keyword = input("Enter the keyword to search for: ")

    # Retrieve books corresponding to the keyword from the books table
    search_query = f"SELECT * FROM books WHERE book_id IN (SELECT book_id FROM keywords WHERE keyword = '{keyword}')"
    cursor.execute(search_query)
    books = cursor.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print(f"No books found for the keyword '{keyword}'.")

def place_order_as_user(table,username):
    if table!='users':
        print('You do not have access.')
        return
    book_id = input("Enter the book ID to place an order: ")

    # Check if the book exists
    check_book_query = f"SELECT * FROM books WHERE book_id = {book_id}"
    cursor.execute(check_book_query)
    book = cursor.fetchone()

    if book:
        # order_date = date.today()
        insert_order_query = f"INSERT INTO sales (user_username, book_id) VALUES ('{username}', {book_id})"
        cursor.execute(insert_order_query)
        cnx.commit()

        print("Order placed successfully!")
    else:
        print(f"No book found with ID {book_id}.")

def view_orders_as_user(table, username):
    if table!='users':
        print('You do not have access.')
        return
    try:
        query = f"SELECT * FROM sales WHERE user_username = '{username}';"
        cursor.execute(query)
        result = cursor.fetchall()
        print("Orders:")
        for row in result:
            print(row)
    except Error as e:
        print(f"Error: {e}")

def view_orders_as_publisher(table, username):
    if table!='publishers':
        print('You do not have access.')
        return
    try:
        query = f"SELECT * FROM books WHERE publisher_username = '{username}';"
        cursor.execute(query)
        result = cursor.fetchall()
        print("Orders:")
        for row in result:
            query2 = f"SELECT * FROM sales WHERE book_id = '{row[0]}';"
            cursor.execute(query2)
            result2 = cursor.fetchall()
            for row2 in result2:
                print(row2)
    except Error as e:
        print(f"Error: {e}")

def deliver_order_as_publisher(table, username):
    if table!='publishers':
        print('You do not have access.')
        return
    try:
        sale_id = input("Enter the sale_id: ")
        query = f"UPDATE sales SET order_status = 'delivered' WHERE sale_id = '{sale_id}' AND order_status='pending';"
        cursor.execute(query)
        cnx.commit()
        print("Delivered successfully.")
    except Error as e:
        print(f"Error: {e}")

def session(table, username):
    query = 1
    while query != 0:
        query = int(input("\n\tWhat do you wanna do? (Enter 21 for a list of available queries): "))
        if query == 1 :
            publish_request_as_author(table,username)
        elif query == 2:
            view_requests_as_author(table,username)
        elif query == 3:
            view_requests_as_publisher(table,username)
        elif query == 4:
            approve_request_as_publisher(table,username)
        elif query == 5:
            insert_keyword_as_author(table,username)
        elif query == 6:
            view_all_books()
        elif query == 7:
            search_using_keyword()
        elif query == 8:
            place_order_as_user(table,username)
        elif query == 9:
            view_orders_as_user(table,username)
        elif query == 10:
            view_orders_as_publisher(table,username)
        elif query == 11:
            deliver_order_as_publisher(table,username)
        elif query == 21:
            print(
            "0)quit\n"
            "1)publish_request_as_author\n"
            "2)view_requests_as_author\n"
            "3)view_requests_as_publisher\n"
            "4)approve_request_as_publisher\n"
            "5)insert_keyword_as_author\n"
            "6)view_all_books\n"
            "7)search_using_keyword\n"
            "8)place_order_as_user\n"
            "9)view_orders_as_user\n"
            "10)view_orders_as_publisher\n"
            "11)deliver_order_as_publisher\n")    

def home():
    choice = 'A'
    category = ['admins', 'publishers', 'authors', 'users']
    while choice!='Q':
        choice = input("\n\tSign-up (S) or Log-in (L) or Quit(Q): ")
        if choice != 'S' and choice != 'L' :
            continue

        if choice!='Q':
            table=input("Enter category (admin=0, publisher=1, author=2, user=3): ")
            if not table_exists(cursor, category[int(table)]):
                continue

        if choice == 'S':
            username_input = input("Enter your username: ")
            password_input = input("Enter your password: ")    
            sign_up(username_input, password_input,category[int(table)])
        elif choice == 'L':
            username_input = input("Enter your username: ")
            password_input = input("Enter your password: ")    
            log_in(username_input, password_input,category[int(table)])

DB_NAME = 'dbfb'
cnx = mysql.connector.connect(user='root',password='mysqlPass')
cursor = cnx.cursor()
connectDB(cursor)

home()

cnx.commit()
cursor.close()
cnx.close()