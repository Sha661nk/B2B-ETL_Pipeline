-- Table to store details about companies and suppliers
-- Companies can be either of type 'Company' or 'Supplier'
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,  -- Unique ID for each company (auto-incremented)
    cuit VARCHAR(20) UNIQUE NOT NULL,  -- Unique tax identifier for companies
    company_name VARCHAR(255) NOT NULL,  -- Name of the company or supplier
    company_type VARCHAR(20) NOT NULL CHECK (company_type IN ('Company', 'Supplier')),  -- Defines whether it's a 'Company' or 'Supplier'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when the record is last updated
);

-- Table to store end customers' information
-- End customers are associated with a company through a foreign key
CREATE TABLE end_customers (
    customer_id SERIAL PRIMARY KEY,  -- Unique ID for each customer (auto-incremented)
    document_number VARCHAR(20) UNIQUE NOT NULL,  -- Unique identification document number for the customer
    full_name VARCHAR(255) NOT NULL,  -- Full name of the customer
    date_of_birth DATE NOT NULL,  -- Date of birth of the customer
    company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,  -- Foreign key linking to the company
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the customer record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when the record is last updated
);

-- Table to store information about products offered by suppliers
-- Each product is associated with a supplier company
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,  -- Unique ID for each product (auto-incremented)
    product_name VARCHAR(255) NOT NULL,  -- Name of the product
    supplier_id INT REFERENCES companies(company_id) ON DELETE CASCADE,  -- Foreign key linking the product to the supplier
    default_price DECIMAL(10, 2) NOT NULL,  -- Default price set by the supplier for the product
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the product record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when the record is last updated
);

-- Table to store price lists for products for each company
-- Each company can set their own price for a product from the supplier
CREATE TABLE price_lists (
    price_list_id SERIAL PRIMARY KEY,  -- Unique ID for each price list record (auto-incremented)
    company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,  -- Foreign key linking to the company setting the price
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,  -- Foreign key linking to the product
    price DECIMAL(10, 2) NOT NULL,  -- Custom price set by the company for the product
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the price list record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the record is last updated
    UNIQUE (company_id, product_id)  -- Ensures that each company can set only one price per product
);

-- Table to store information about orders placed by companies for their customers
-- Orders contain multiple products and are associated with an end customer
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,  -- Unique ID for each order (auto-incremented)
    company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,  -- Foreign key linking the order to the company placing it
    customer_id INT REFERENCES end_customers(customer_id) ON DELETE CASCADE,  -- Foreign key linking the order to the end customer
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the order is placed
    total_amount DECIMAL(10, 2) NOT NULL,  -- Total amount of the order
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the order record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when the record is last updated
);

-- Table to store individual items in an order
-- Each order can have multiple products (items) with quantity and price
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,  -- Unique ID for each order item (auto-incremented)
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,  -- Foreign key linking to the order
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,  -- Foreign key linking to the product
    quantity INT NOT NULL,  -- Quantity of the product ordered
    price DECIMAL(10, 2) NOT NULL,  -- Price at which the product is sold (from price list)
    total DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * price) STORED,  -- Total price for the order item (calculated automatically)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the order item record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when the record is last updated
);

CREATE TABLE marketing_data (
    marketing_id SERIAL PRIMARY KEY,  -- Unique ID for each marketing record
    campaign_name VARCHAR(255) NOT NULL,  -- Name of the marketing campaign
    campaign_start_date DATE NOT NULL,  -- Campaign start date
    campaign_end_date DATE NOT NULL,  -- Campaign end date
    target_audience_size INT NOT NULL,  -- Size of the target audience
    conversions INT NOT NULL,  -- Number of conversions from the campaign
    company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,  -- Foreign key linking to the company running the campaign
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,  -- Foreign key linking to the product the campaign is promoting
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the campaign record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when the record is last updated
);

CREATE TABLE weblog_data (
    weblog_id SERIAL PRIMARY KEY,  -- Unique ID for each weblog record
    client_ip VARCHAR(50) NOT NULL,  -- Client IP address from which the request originated
    username VARCHAR(50),  -- Username of the customer (optional, can be null)
    log_time TIMESTAMP NOT NULL,  -- Timestamp of the web log event
    device_type VARCHAR(50) NOT NULL,  -- Type of device (Desktop, Mobile, Tablet)
    user_agent TEXT NOT NULL,  -- User agent string from the device making the request
    customer_id INT REFERENCES end_customers(customer_id) ON DELETE CASCADE,  -- Foreign key linking to the end customer
    company_id INT REFERENCES companies(company_id) ON DELETE CASCADE,  -- Foreign key linking to the company (optional if needed)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the web log is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when the record is last updated
);
