INSERT INTO {{ params.table_fact_medication_presentation }} (
    laboratory_id, 
    product_id, 
    ggrem_code, 
    registration_number, 
    ean1, 
    ean2, 
    presentation_details,
    concentration,
    pharmaceutical_form, 
    price_regime, 
    stripe, 
    updated_at
)
SELECT DISTINCT ON (s.ggrem_code)
    l.laboratory_id,
    p.product_id,
    CAST(s.ggrem_code AS BIGINT),
    s.registration,
    s.ean1,
    s.ean2,
    s.presentation,
    s.concentration,
    s.pharmaceutical_form,
    s.price_regime,
    s.stripe,
    NOW()
FROM {{ params.table_staging }} s
JOIN {{ params.table_dim_laboratory }} l 
    ON s.cnpj = l.cnpj
JOIN {{ params.table_dim_product }} p 
    ON s.product = p.product_name 
    AND s.product_type = p.product_type
WHERE s.ggrem_code IS NOT NULL
ORDER BY s.ggrem_code
ON CONFLICT (ggrem_code) 
DO UPDATE SET 
    laboratory_id = EXCLUDED.laboratory_id,
    product_id = EXCLUDED.product_id,
    registration_number = EXCLUDED.registration_number,
    ean1 = EXCLUDED.ean1,
    ean2 = EXCLUDED.ean2,
    presentation_details = EXCLUDED.presentation_details,
    concentration = EXCLUDED.concentration,
    pharmaceutical_form = EXCLUDED.pharmaceutical_form,
    price_regime = EXCLUDED.price_regime,
    stripe = EXCLUDED.stripe,
    updated_at = NOW();