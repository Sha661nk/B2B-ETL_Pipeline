#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import psycopg2
import configparser
from faker import Faker
import random
from datetime import datetime
import user_agents

# Create connection using config file
def create_connection(config_file_path, section):
    config = configparser.ConfigParser()
    config.read(config_file_path)

    db_params = {key: value for key, value in config.items(section)}

    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.DatabaseError as e:
        print(f"Error: {e}")
        return None

# Truncate all necessary tables before populating
def truncate_tables(cursor):
    cursor.execute("TRUNCATE TABLE weblog_data RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE marketing_data RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE order_items RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE orders RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE price_lists RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE products RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE end_customers RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE companies RESTART IDENTITY CASCADE;")
    print("Tables truncated successfully.")

# Populate the companies table
def populate_companies(cursor, num_companies=20):
    fake = Faker()
    company_ids = []
    for _ in range(num_companies):
        cuit = fake.unique.random_number(digits=9)
        company_name = fake.company()
        company_type = random.choice(['Company', 'Supplier'])
        cursor.execute(
            "INSERT INTO companies (cuit, company_name, company_type) VALUES (%s, %s, %s) RETURNING company_id;",
            (str(cuit), company_name, company_type)
        )
        company_id = cursor.fetchone()[0]
        company_ids.append((company_id, company_type))
    print(f"{num_companies} companies inserted.")
    return company_ids

# Populate the end_customers table with referential integrity
def populate_end_customers(cursor, company_ids, num_customers=50):
    fake = Faker()
    customer_ids = []
    for _ in range(num_customers):
        document_number = fake.unique.random_number(digits=8)
        full_name = fake.name()
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)
        company_id = random.choice([cid for cid, ctype in company_ids if ctype == 'Company'])
        cursor.execute(
            "INSERT INTO end_customers (document_number, full_name, date_of_birth, company_id) VALUES (%s, %s, %s, %s) RETURNING customer_id;",
            (str(document_number), full_name, date_of_birth, company_id)
        )
        customer_id = cursor.fetchone()[0]
        customer_ids.append(customer_id)
    print(f"{num_customers} customers inserted.")
    return customer_ids

# Populate the products table with referential integrity for suppliers
def populate_products(cursor, company_ids, num_products=30):
    fake = Faker()
    product_ids = []
    for _ in range(num_products):
        product_name = fake.word().capitalize()
        default_price = round(random.uniform(50, 500), 2)
        supplier_id = random.choice([cid for cid, ctype in company_ids if ctype == 'Supplier'])
        cursor.execute(
            "INSERT INTO products (product_name, supplier_id, default_price) VALUES (%s, %s, %s) RETURNING product_id;",
            (product_name, supplier_id, default_price)
        )
        product_id = cursor.fetchone()[0]
        product_ids.append(product_id)
    print(f"{num_products} products inserted.")
    return product_ids

# Populate the price_lists table with referential integrity for companies and products
def populate_price_lists(cursor, company_ids, product_ids):
    for company_id, company_type in company_ids:
        if company_type == 'Company':
            selected_products = random.sample(product_ids, random.randint(3, 10))
            for product_id in selected_products:
                price = round(random.uniform(50, 500), 2)
                cursor.execute(
                    "INSERT INTO price_lists (company_id, product_id, price) VALUES (%s, %s, %s);",
                    (company_id, product_id, price)
                )
    print("Price lists inserted for companies.")

# Populate the orders table with referential integrity for companies and customers
def populate_orders(cursor, company_ids, customer_ids, num_orders=50):
    fake = Faker()
    order_ids = []
    for _ in range(num_orders):
        company_id = random.choice([cid for cid, ctype in company_ids if ctype == 'Company'])
        customer_id = random.choice(customer_ids)
        order_date = fake.date_time_between(start_date='-1y', end_date='now')
        total_amount = round(random.uniform(100, 1000), 2)
        cursor.execute(
            "INSERT INTO orders (company_id, customer_id, order_date, total_amount) VALUES (%s, %s, %s, %s) RETURNING order_id;",
            (company_id, customer_id, order_date, total_amount)
        )
        order_id = cursor.fetchone()[0]
        order_ids.append(order_id)
    print(f"{num_orders} orders inserted.")
    return order_ids

# Populate the order_items table with referential integrity for orders and products
def populate_order_items(cursor, order_ids, product_ids):
    for order_id in order_ids:
        selected_products = random.sample(product_ids, random.randint(1, 5))
        for product_id in selected_products:
            quantity = random.randint(1, 10)
            price = round(random.uniform(50, 500), 2)
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s);",
                (order_id, product_id, quantity, price)
            )
    print("Order items inserted.")

# Populate the marketing_data table
def populate_marketing_data(cursor, company_ids, product_ids, num_campaigns=10):
    fake = Faker()
    for _ in range(num_campaigns):
        campaign_name = fake.catch_phrase()
        campaign_start_date = fake.date_this_decade()
        campaign_end_date = fake.date_between_dates(campaign_start_date, datetime.now())
        target_audience_size = random.randint(100, 10000)
        conversions = random.randint(10, target_audience_size)
        company_id = random.choice([cid for cid, ctype in company_ids if ctype == 'Company'])
        product_id = random.choice(product_ids)
        cursor.execute(
            "INSERT INTO marketing_data (campaign_name, campaign_start_date, campaign_end_date, target_audience_size, conversions, company_id, product_id) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (campaign_name, campaign_start_date, campaign_end_date, target_audience_size, conversions, company_id, product_id)
        )
    print(f"{num_campaigns} marketing campaigns inserted.")

# Populate the weblog_data table
def populate_weblog_data(cursor, company_ids, customer_ids, num_entries=100):
    fake = Faker()
    user_agents_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1', 
        'Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',  
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
        'Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1'
    ]
    
    for _ in range(num_entries):
        client_ip = fake.ipv4()
        username = fake.user_name() if random.choice([True, False]) else '-'
        log_time = fake.date_time_this_year()
        user_agent_str = random.choice(user_agents_list)
        ua = user_agents.parse(user_agent_str)
        device_type = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "Desktop"
        customer_id = random.choice(customer_ids)
        company_id = random.choice([cid for cid, ctype in company_ids if ctype == 'Company'])
        cursor.execute(
            "INSERT INTO weblog_data (client_ip, username, log_time, device_type, user_agent, customer_id, company_id) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (client_ip, username, log_time, device_type, user_agent_str, customer_id, company_id)
        )
    print(f"{num_entries} weblog entries inserted.")

# Main function to execute the population process
def main():
    config_file_path = r'..\config\db_config.ini'
    conn = create_connection(config_file_path, 'source_db')
    if conn:
        cursor = conn.cursor()
        truncate_tables(cursor)

        # Populate companies table
        company_ids = populate_companies(cursor)

        # Populate end_customers table
        customer_ids = populate_end_customers(cursor, company_ids)

        # Populate products table
        product_ids = populate_products(cursor, company_ids)

        # Populate price_lists table
        populate_price_lists(cursor, company_ids, product_ids)

        # Populate orders table
        order_ids = populate_orders(cursor, company_ids, customer_ids)

        # Populate order_items table
        populate_order_items(cursor, order_ids, product_ids)

        # Populate marketing_data table
        populate_marketing_data(cursor, company_ids, product_ids)

        # Populate weblog_data table
        populate_weblog_data(cursor, company_ids, customer_ids)

        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        print("Data population completed successfully.")
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    main()

