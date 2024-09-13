--- Monthly Sales Report ---
SELECT 
    TO_CHAR(dd.date, 'YYYY-MM') AS sales_month, 
    SUM(fo.total_amount) AS total_sales,         
    SUM(fo.quantity) AS total_quantity           
FROM 
    Fact_Orders fo
JOIN 
    Dim_Date dd ON fo.date_id = dd.date_id       
WHERE 
    dd.date >= (CURRENT_DATE - INTERVAL '1 year')  
GROUP BY 
    TO_CHAR(dd.date, 'YYYY-MM')                  
ORDER BY 
    sales_month;    

--- User Device Usage Report ---
SELECT 
    dd.device_type,                  
    COUNT(fo.device_id) AS usage_count  
FROM 
    Fact_Orders fo
JOIN 
    Dim_Device dd ON fo.device_id = dd.device_id  
GROUP BY 
    dd.device_type                           
ORDER BY 
    usage_count DESC                         
LIMIT 5;  

--- Most Popular Products from which users log into Report ---
WITH Device_Type_Count AS (
    SELECT device_type, COUNT(*) AS login_count
    FROM Dim_Device
    GROUP BY device_type
    ORDER BY login_count DESC
    LIMIT 1  
),
Device_Customers AS (
    SELECT DISTINCT fo.customer_id
    FROM Fact_Orders fo
    JOIN Dim_Device dd ON fo.device_id = dd.device_id
    JOIN Device_Type_Count dtc ON dd.device_type = dtc.device_type
),
Popular_Products AS (
    SELECT fo.product_id, COUNT(fo.product_id) AS product_count
    FROM Fact_Orders fo
    JOIN Device_Customers dc ON fo.customer_id = dc.customer_id
    GROUP BY fo.product_id
    ORDER BY product_count DESC
)

SELECT dp.product_name, pp.product_count
FROM Popular_Products pp
JOIN Dim_Product dp ON pp.product_id = dp.product_id;





