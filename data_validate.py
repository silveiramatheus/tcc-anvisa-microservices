import duckdb
import pandas as pd
import glob

arquivos_excel = glob.glob('prescriptions/*.xlsx')
lista_receitas = []

for arquivo in arquivos_excel:
    try:
        df_temp = pd.read_excel(arquivo)
        if 'Medicamento' in df_temp.columns:
            lista_receitas.append(df_temp[['Medicamento']])
    except Exception as e:
        print(f"Erro ao ler {arquivo}: {e}")

df_todas_receitas = pd.concat(lista_receitas, ignore_index=True).dropna()

con = duckdb.connect()
con.execute("INSTALL postgres; LOAD postgres;")
con.execute("""
    ATTACH 'dbname=anvisa_db user=admin password=password123 host=localhost port=5432' 
    AS postgres_db (TYPE POSTGRES);
""")

query = """
    WITH receitas_unicas AS (
        SELECT DISTINCT Medicamento AS nome_receita
        FROM df_todas_receitas
    ),
    pre_processamento AS (
        SELECT 
            nome_receita,
            regexp_extract(nome_receita, '^[^ ]+', 0) AS palavra_chave
        FROM receitas_unicas
    )
    SELECT 
        r.nome_receita AS "Prescrição Original",
        r.palavra_chave AS "Palavra Buscada",
        MAX(p.product_name) AS "Produto no Banco (Exemplo)",
        MAX(p.substance) AS "Substância no Banco (Exemplo)",
        CASE WHEN MAX(p.product_id) IS NOT NULL THEN '✅ Encontrado' ELSE '❌ Não Encontrado' END AS "Status do Match"
    FROM pre_processamento r
    LEFT JOIN postgres_db.dim_product p 
        ON p.substance ILIKE '%' || r.palavra_chave || '%'
        OR p.product_name ILIKE '%' || r.palavra_chave || '%'
    GROUP BY r.nome_receita, r.palavra_chave
    ORDER BY "Status do Match" ASC, "Prescrição Original";
"""

df_validacao = con.execute(query).df()

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print(f"Total de medicamentos únicos nas receitas: {len(df_validacao)}")
print("-" * 80)
print(df_validacao)