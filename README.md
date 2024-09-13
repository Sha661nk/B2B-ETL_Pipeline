# B2B E-Commerce Data Warehouse ETL/ELT System

## Project Overview
This project involves designing and implementing a **Data Warehouse/Data Store ETL/ELT system** for a B2B e-commerce platform. The system ingests and processes data from three distinct sources: a **B2B platform database**, **web server log data**, and a **marketing lead spreadsheet file**.

The goal is to demonstrate the ability to implement a real-life data management system, paying close attention to development best practices, error handling, and scalability. The system will support a B2B e-commerce site in reporting key insights, including device usage, product popularity, and monthly sales data.

## Task Scope
This project evaluates proficiency in the following areas:
- Setting up proper project infrastructure.
- Solving real-world problems using efficient methods.
- Effectively leveraging chosen frameworks and libraries.

## Data Sources
- **B2B Platform Database**: This database manages information about companies, customers, suppliers, products, and orders.
  - **End Customers**: Identified by document number, full name, and date of birth.
  - **Companies**: Identified by CUIT (unique identifier) and name.
  - **Suppliers**: Companies offering products and prices.
  - **Orders**: Links between companies and end customers for receiving goods.

- **Web Server Logs**: Logs include various client and server interaction data.
  - Relevant fields: client IP, username, request time, and user-agent (browser).

- **Marketing Lead Spreadsheet**: Contains customer information collected from marketing campaigns.

## Reports Generated
The ETL/ELT system will support the generation of the following reports:
1. **Top 5 most popular devices** used by B2B clients.
2. **Most popular products** in countries from which the most users log in.
3. **Monthly sales reports** for the B2B platform over the past year.

## Key Requirements
- **Database Implementation**: Create a database to simulate the B2B platform.
- **Weblog Generation**: Script to simulate web server log data.
- **ETL/ELT Process**: Transform and load data into the target data warehouse/data mart.
  - Restartable jobs in case of failure.
  - Handle large data volumes.
  - Detect and handle erroneous data.
  - Track ETL/ELT metadata (start, break, finish times).
  - Ensure data is readable and properly formatted for reporting.

## Technologies Used
- **Database**: Relational or NoSQL for the data warehouse/data mart.
- **ETL/ELT Process**: Any preferred ETL tool or custom-coded process.

