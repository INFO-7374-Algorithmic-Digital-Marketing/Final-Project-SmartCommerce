CREATE VIEW product_price_summary_view AS 
WITH order_list_agg AS ( 
    SELECT 
        product_id,
        MAX(price) AS max_price,
        MIN(price) AS min_price
    FROM 
        "Order_Items"
    GROUP BY 
        product_id
    ORDER BY
        product_id
), 

joined_with_category AS (
SELECT 
    o.product_id, 
    o.max_price, 
    o.min_price,
    p.product_category_name
FROM 
    order_list_agg o
JOIN 
    "Products" p
ON 
    o.product_id = p.product_id
)

SELECT 
    j.product_id, 
    j.min_price, 
    j.max_price, 
    t.product_category_name_english
FROM 
    joined_with_category j
JOIN 
    "Product_Category_Translation" t
ON 
    t.product_category_name = j.product_category_name;


CREATE VIEW top_products_with_price_summary AS 
WITH temp AS (
    SELECT 
        *
    FROM 
        "Reviews" r
    JOIN 
       "Order_Items" o
    ON 
        o.order_id = r.order_id
), 
counted_products_review AS (
    SELECT 
        PRODUCT_ID, 
        COUNT(*) AS CNT
    FROM 
        temp
    GROUP BY 
        PRODUCT_ID
    ORDER BY 
        cnt DESC
    LIMIT 
        1000
)

SELECT 
    c.product_id, 
    c.cnt, 
    p.min_price, 
    p.max_price, 
    p.product_category_name_english
FROM 
    counted_products_review c
JOIN 
    product_price_summary_view p
ON 
    c.product_id = p.product_id;