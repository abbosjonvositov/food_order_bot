import sqlite3

database = sqlite3.connect('database.db')
cursor = database.cursor()
cursor.execute('''
    SELECT * FROM carts
''')
output = cursor.fetchall()
database.close()
# print(output)


def create_users_table():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        telegram_id BIGINT NOT NULL UNIQUE,
        phone TEXT
    ); 
    ''')
    database.commit()
    database.close()


# create_users_table()

def create_carts_table():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts(
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(user_id),
            total_price DECIMAL(12, 2) DEFAULT 0,
            total_products INTEGER DEFAULT 0           
    ); 
    ''')
    database.commit()
    database.close()


# create_carts_table()

def create_cart_products_table():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_products(
                cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cart_id INTEGER REFERENCES carts(cart_id),
                product_name VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL,
                final_price DECIMAL(12, 2) NOT NULL,
                
                UNIQUE(cart_id, product_name)
                                         
    ); 
    ''')
    database.commit()
    database.close()


# create_cart_products_table()

def create_categories_table():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories(
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name VARCHAR(100) NOT NULL UNIQUE
    ); 
    ''')
    database.commit()
    database.close()


# create_categories_table()

def insert_categories():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO categories(category_name) VALUES
        ('Lavash'), 
        ('Burger'), 
        ('Hot-dog'), 
        ('Pizza'), 
        ('Sauces'), 
        ('Drinks') 
        ''')
    database.commit()
    database.close()


# insert_categories()

def create_table_products():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            product_name VARCHAR(50) NOT NULL UNIQUE,
            price DECIMAL(12, 2) NOT NULL,
            description VARCHAR(150),
            image TEXT,
            
            FOREIGN KEY(category_id) REFERENCES categories(category_id)
    ); 
    ''')
    database.commit()
    database.close()


# create_table_products()

def insert_product_table():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO products(category_id, product_name, price, description, image) VALUES
            (1, 'Lavash with meat', 30000, 'Floor, tomato, pickle, chips, sauce', 'media/lavash/lavash_1.jpg'),
            (1, 'Lavash with chicken', 28000, 'Floor, tomato, pickle, chips, sauce', 'media/lavash/lavash_2.jpg'),
            (1, 'Lavash with meat and cheese', 32000, 'Floor, tomato, pickle, chips, sauce, cheese', 'media/lavash/lavash_3.jpg')
    ''')
    database.commit()
    database.close()


def first_select_user(chat_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
            SELECT * FROM users WHERE telegram_id = ?;
        ''', (chat_id,))

    user = cursor.fetchone()
    database.close()
    return user


def first_register_user(full_name, chat_id, phone):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO users(full_name, telegram_id, phone) VALUES(?,?,?)
    ''', (full_name, chat_id, phone))
    database.commit()
    database.close()


def insert_to_cart(chat_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO carts(user_id) VALUES
    (
        (SELECT user_id FROM users WHERE telegram_id = ?)
    )
    ''', (chat_id,))
    database.commit()
    database.close()


def get_all_categories():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM categories
    ''')
    categories = cursor.fetchall()
    database.close()
    return categories


def get_products_by_category_id(category_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT product_id, product_name FROM products WHERE category_id = ?
        ''', (category_id,))
    products = cursor.fetchall()
    database.close()
    return products


def get_product_detail(product_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
            SELECT * FROM products WHERE product_id = ?
            ''', (product_id,))
    product = cursor.fetchone()
    database.close()
    # print(product)
    return product


def get_user_cart_id(chat_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT cart_id FROM carts WHERE user_id = (SELECT user_id FROM users WHERE telegram_id = ?);
    ''', (chat_id,))
    cart_id = cursor.fetchone()[0]
    database.close()
    return cart_id


def get_quantity(cart_id, product_name):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT quantity FROM cart_products WHERE cart_id = ? AND product_name = ?;
    ''', (cart_id, product_name))
    quantity = cursor.fetchone()[0]
    database.close()
    # print(product)
    return quantity


def insert_or_update_cart_products(cart_id, product_name, quantity, final_price):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    try:
        cursor.execute('''
            INSERT INTO cart_products(cart_id, product_name, quantity, final_price) VALUES (?,?,?,?)
        ''', (cart_id, product_name, quantity, final_price))
        database.commit()
        return True
    except:
        cursor.execute('''
            UPDATE cart_products
            SET quantity = ?, final_price = ?
            WHERE product_name = ? AND cart_id = ?
        ''', (quantity, final_price, product_name, cart_id))
        database.commit()
        return False

    finally:
        database.close()


def update_carts(cart_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        UPDATE carts
        SET total_products = (SELECT SUM(quantity) FROM cart_products WHERE cart_id = :cart_id),
        total_price = (SELECT SUM(final_price) FROM cart_products WHERE cart_id = :cart_id)
        WHERE cart_id = :cart_id
        ''', {'cart_id': cart_id})
    database.commit()
    database.close()


def get_cart_products(cart_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        
        SELECT product_name, quantity, final_price
        FROM cart_products WHERE cart_id = ?    
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    database.close()
    return cart_products


def get_total_products_total_price(cart_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT total_products,total_price
        FROM carts WHERE cart_id = ?
       
    ''', (cart_id,))

    total_products, total_price = cursor.fetchone()
    database.close()
    return total_products, total_price


def get_cart_product_for_delete(cart_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        SELECT cart_product_id, product_name FROM cart_products
        WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    database.close()
    return cart_products


def delete_cart_product_from(cart_product_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        DELETE FROM cart_products WHERE cart_product_id = ?
    ''', (cart_product_id,))
    database.commit()
    database.close()


def drop_cart_products_default(cart_id):
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
            DELETE FROM cart_products WHERE cart_id = ?;
        ''', (cart_id,))
    database.commit()
    database.close()


def create_sales_report():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales(
            sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            telegram_id BIGINT NOT NULL UNIQUE,
            phone TEXT
        ); 
        ''')
    database.commit()
    database.close()


def create_sales_detailed_report():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales(
                sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                telegram_id BIGINT NOT NULL UNIQUE,
                phone TEXT
            ); 
            ''')
    database.commit()
    database.close()
