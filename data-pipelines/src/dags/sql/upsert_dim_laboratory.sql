INSERT INTO {{ params.table_dim_laboratory }} (
    cnpj, 
    laboratory_name, 
    updated_at
)
SELECT DISTINCT ON (cnpj)
    cnpj, 
    laboratory, 
    NOW()
FROM {{ params.table_staging }}
WHERE cnpj IS NOT NULL
ORDER BY cnpj, laboratory
ON CONFLICT (cnpj) 
DO UPDATE SET 
    laboratory_name = EXCLUDED.laboratory_name,
    updated_at = NOW();