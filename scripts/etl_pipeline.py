import psycopg2
import configparser
import pandas as pd
from user_agents import parse
from datetime import datetime
import os
import logging

# Function to set up logging
def setup_logging():
    log_dir = r'..\logs'
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_folder = os.path.join(log_dir, timestamp)
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, "pipeline.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Logging initialized. Logs will be saved in: {log_file}")
    return log_file

# Create a database connection
def create_connection(host, database, user, password):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        logging.info(f"Connected to database: {database}")
        return conn
    except psycopg2.DatabaseError as e:
        logging.error(f"Error connecting to database: {e}")
        return None

# Read configurations from the config file
def read_config(config_file_path, section):
    config = configparser.ConfigParser()
    config.read(config_file_path)

    if config.has_section(section):
        params = config.items(section)
        return {key: value for key, value in params}
    else:
        raise Exception(f"Section {section} not found in the {config_file_path} file")

# Extract data from source database
def extract_data(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies")
        companies = cursor.fetchall()

        cursor.execute("SELECT * FROM end_customers")
        customers = cursor.fetchall()

        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()

        cursor.execute("SELECT * FROM order_items")
        order_items = cursor.fetchall()

        # New tables: Extract marketing data and weblog data
        cursor.execute("SELECT * FROM marketing_data")
        marketing_data = cursor.fetchall()

        cursor.execute("SELECT * FROM weblog_data")
        weblog_data = cursor.fetchall()

        cursor.close()
        logging.info("Data extracted from source database")
        return companies, customers, products, orders, order_items, marketing_data, weblog_data
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        return None


def transform_data(companies, customers, products, orders, order_items, marketing_data, weblog_data):
    df_companies = pd.DataFrame(companies, columns=['company_id', 'cuit', 'company_name', 'company_type', 'created_at', 'updated_at'])
    df_customers = pd.DataFrame(customers, columns=['customer_id', 'document_number', 'full_name', 'date_of_birth', 'company_id', 'created_at', 'updated_at'])
    df_products = pd.DataFrame(products, columns=['product_id', 'product_name', 'supplier_id', 'default_price', 'created_at', 'updated_at'])
    df_orders = pd.DataFrame(orders, columns=['order_id', 'company_id', 'customer_id', 'order_date', 'total_amount', 'created_at', 'updated_at'])
    df_order_items = pd.DataFrame(order_items, columns=['order_item_id', 'order_id', 'product_id', 'quantity', 'price', 'total', 'created_at', 'updated_at'])
    df_marketing = pd.DataFrame(marketing_data, columns=['marketing_id', 'campaign_name', 'campaign_start_date', 'campaign_end_date', 'target_audience_size', 'conversions', 'company_id', 'product_id', 'created_at', 'updated_at'])
    df_weblog = pd.DataFrame(weblog_data, columns=['weblog_id', 'client_ip', 'username', 'log_time', 'device_type', 'user_agent', 'customer_id', 'company_id', 'created_at', 'updated_at'])
    
    # Create dimension tables
    dim_company = df_companies[['company_id', 'cuit', 'company_name', 'company_type']]
    dim_customer = df_customers[['customer_id', 'full_name', 'document_number']]
    dim_product = df_products[['product_id', 'product_name', 'supplier_id', 'default_price']]
    
    # Create Dim_Date table
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])  # Ensure order_date is datetime
    df_orders['date'] = df_orders['order_date'].dt.date  # Extract date part
    dim_date = df_orders[['date']].drop_duplicates().copy()
    dim_date['month'] = pd.to_datetime(dim_date['date']).dt.month
    dim_date['year'] = pd.to_datetime(dim_date['date']).dt.year
    dim_date['date_id'] = range(1, len(dim_date) + 1)
    
    # Ensure both columns are datetime64[ns] type before merging
    dim_date['date'] = pd.to_datetime(dim_date['date'])  # Convert to datetime64[ns]
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date']).dt.normalize()  # Ensure `order_date` is normalized to date

    # Create fact table for orders
    fact_orders = df_order_items.merge(df_orders[['order_id', 'company_id', 'customer_id', 'order_date']], on='order_id')
    fact_orders = fact_orders.merge(dim_date[['date', 'date_id']], left_on='order_date', right_on='date')
    fact_orders = fact_orders[['order_id', 'company_id', 'customer_id', 'product_id', 'date_id', 'quantity', 'total', 'order_date']]
    fact_orders.rename(columns={'total': 'total_amount', 'order_date': 'order_timestamp'}, inplace=True)
    fact_orders = fact_orders.drop_duplicates(subset=['order_id'])
    
    # Create Dim_Lead from marketing data
    dim_lead = pd.DataFrame({
        'first_name': df_marketing['campaign_name'],  
        'last_name': df_marketing['campaign_name'],   
        'email': None,                                
        'phone_number': None,                         
        'company_name': df_marketing['company_id'],   
        'lead_source': df_marketing['product_id'],    
        'lead_status': None,                         
        'engagement_score': df_marketing['conversions'],  
        'contact_date': df_marketing['campaign_start_date'],
    })

    # Create Dim_Device from weblog data
    dim_device = df_weblog[['device_type', 'user_agent']]

    logging.info("Data transformed into dimensional model")
    return dim_company, dim_customer, dim_product, dim_date, fact_orders, dim_lead, dim_device

# Load the data into the database
def load_data(conn, dim_company, dim_customer, dim_product, dim_date, fact_orders, dim_lead, dim_device):
    try:
        cursor = conn.cursor()
        # Truncate and reload tables
        cursor.execute("TRUNCATE TABLE Dim_Company CASCADE;")
        cursor.execute("TRUNCATE TABLE Dim_Customer CASCADE;")
        cursor.execute("TRUNCATE TABLE Dim_Product CASCADE;")
        cursor.execute("TRUNCATE TABLE Dim_Date CASCADE;")
        cursor.execute("TRUNCATE TABLE Fact_Orders CASCADE;")
        cursor.execute("TRUNCATE TABLE Dim_Lead CASCADE;")
        cursor.execute("TRUNCATE TABLE Dim_Device CASCADE;")

        # Load dimension and fact tables
        insert_data(cursor, "Dim_Company", dim_company)
        insert_data(cursor, "Dim_Customer", dim_customer)
        insert_data(cursor, "Dim_Product", dim_product)

        # Correct columns for Dim_Date
        dim_date = dim_date[["date_id", "date", "month", "year"]]  # Select only relevant columns
        insert_data(cursor, "Dim_Date", dim_date)

        insert_data(cursor, "Fact_Orders", fact_orders)
        insert_data(cursor, "Dim_Lead", dim_lead)
        insert_data(cursor, "Dim_Device", dim_device)

        conn.commit()
        cursor.close()
        logging.info("Data loaded into target database")
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        conn.rollback()

# Generic function to insert data
def insert_data(cursor, table_name, dataframe):
    for index, row in dataframe.iterrows():
        columns = ', '.join(dataframe.columns)
        placeholders = ', '.join(['%s'] * len(dataframe.columns))
        sql = f"""
            INSERT INTO {table_name} ({columns}) 
            VALUES ({placeholders})
        """
        cursor.execute(sql, tuple(row))

# Main ETL pipeline
def etl_pipeline(source_conn, target_conn):
    logging.info("ETL pipeline started")
    companies, customers, products, orders, order_items, marketing_data, weblog_data = extract_data(source_conn)
    if companies:
        dim_company, dim_customer, dim_product, dim_date, fact_orders, dim_lead, dim_device = transform_data(companies, customers, products, orders, order_items, marketing_data, weblog_data)
        load_data(target_conn, dim_company, dim_customer, dim_product, dim_date, fact_orders, dim_lead, dim_device)
    logging.info("ETL pipeline completed")

# Example usage
if __name__ == "__main__":
    log_file = setup_logging()
    config_file_path = r'..\config\db_config.ini'

    source_db_config = read_config(config_file_path, 'source_db')
    target_db_config = read_config(config_file_path, 'target_db')

    source_conn = create_connection(**source_db_config)
    target_conn = create_connection(**target_db_config)

    if source_conn and target_conn:
        etl_pipeline(source_conn, target_conn)
        source_conn.close()
        target_conn.close()

        logging.info("Pipeline run completed, connections closed.")

