INSERT INTO {{ params.table_dim_product }} (
    product_name, 
    substance, 
    therapeutic_class, 
    product_type, 
    updated_at
)
SELECT DISTINCT ON (product, product_type)
    product, 
    substance, 
    therapeutic_class, 
    product_type, 
    NOW()
FROM {{ params.table_staging }}
WHERE product IS NOT NULL
ORDER BY product, product_type, substance
ON CONFLICT (product_name, product_type) 
DO UPDATE SET 
    substance = EXCLUDED.substance,
    therapeutic_class = EXCLUDED.therapeutic_class,
    updated_at = NOW();