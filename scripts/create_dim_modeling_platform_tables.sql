-- -- Dimension Tables

CREATE TABLE Dim_Company (
    company_id SERIAL PRIMARY KEY,
    cuit VARCHAR(20) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(20) NOT NULL
);

CREATE TABLE Dim_Customer (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    document_number VARCHAR(20) NOT NULL
);

CREATE TABLE Dim_Product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    supplier_id INT REFERENCES Dim_Company(company_id),
    default_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE Dim_Device (
    device_id SERIAL PRIMARY KEY,
    device_type VARCHAR(20) NOT NULL,
    user_agent VARCHAR(500) NOT NULL
);

CREATE TABLE Dim_Date (
    date_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL
);

CREATE TABLE Dim_Lead (
    lead_id SERIAL PRIMARY KEY,              -- Auto-incrementing lead ID
    first_name VARCHAR(255) NOT NULL,        -- First name of the lead
    last_name VARCHAR(255) NOT NULL,         -- Last name of the lead
    email VARCHAR(255),                      -- Email of the lead
    phone_number VARCHAR(50),                -- Phone number of the lead
    company_name VARCHAR(255),               -- Company associated with the lead
    lead_source VARCHAR(50),                 -- Source of the lead (e.g., website, email campaign)
    lead_status VARCHAR(50),                 -- Status of the lead (e.g., new, contacted, qualified)
    engagement_score INT,                    -- Engagement score for the lead
    contact_date DATE                        -- Date when the lead was last contacted
);

-- -- Fact Table

CREATE TABLE Fact_Orders (
    order_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES Dim_Company(company_id),
    customer_id INT REFERENCES Dim_Customer(customer_id),
    product_id INT REFERENCES Dim_Product(product_id),
    date_id INT REFERENCES Dim_Date(date_id),
    device_id INT REFERENCES Dim_Device(device_id),
    quantity INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_timestamp TIMESTAMP NOT NULL
);


