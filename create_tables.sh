#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL    
    CREATE TABLE IF NOT EXISTS dim_laboratory (
        laboratory_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        cnpj VARCHAR(20) NOT NULL,
        laboratory_name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_cnpj UNIQUE (cnpj)
    );

    CREATE TABLE IF NOT EXISTS dim_product (
        product_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        substance TEXT,
        therapeutic_class VARCHAR(255),
        product_type VARCHAR(100),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_product_composite UNIQUE (product_name, product_type)
    );

    CREATE TABLE IF NOT EXISTS fact_medication_presentation (
        presentation_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        laboratory_id INT REFERENCES dim_laboratory(laboratory_id),
        product_id INT REFERENCES dim_product(product_id),
        ggrem_code BIGINT NOT NULL,
        registration_number VARCHAR(20),
        ean1 VARCHAR(14),
        ean2 VARCHAR(14),
        presentation_details TEXT,
        price_regime VARCHAR(50),
        stripe VARCHAR(50),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_ggrem_code UNIQUE (ggrem_code)
    );

    CREATE INDEX IF NOT EXISTS idx_fact_lab_id ON fact_medication_presentation(laboratory_id);
    CREATE INDEX IF NOT EXISTS idx_fact_prod_id ON fact_medication_presentation(product_id);

EOSQL