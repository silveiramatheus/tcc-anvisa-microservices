# Pipeline de Dados ANVISA/CMED 💊

Repositório oficial do projeto de extração, transformação e disponibilização do catálogo oficial de medicamentos da ANVISA/CMED.

## 📌 Sobre o Projeto
Este sistema foi construído para resolver a ausência de uma base de dados padronizada de medicamentos em aplicações de saúde digital. A arquitetura implementa um processo automatizado de **Engenharia de Dados (ETL)**, estruturando as planilhas governamentais brutas para garantir que as apresentações medicamentosas tenham correspondência exata com o rigor da Denominação Comum Brasileira (DCB). A complexidade do armazenamento é totalmente isolada da aplicação cliente através de um microsserviço de API.

## 🏗️ Arquitetura e Tecnologias
O sistema foi projetado sob o paradigma de microsserviços e está 100% conteinerizado.

* **Orquestração e Ingestão (ETL):** Apache Airflow e Python (Pandas/Requests).
* **Armazenamento:** PostgreSQL (Modelagem Dimensional em Esquema Estrela).
* **Camada de Disponibilização (API):** FastAPI, SQLAlchemy e Pydantic.
* **Infraestrutura:** Docker e Docker Compose.

## ⚙️ Destaques Técnicos
* **Eager Loading:** O Mapeamento Objeto-Relacional (ORM) resolve relacionamentos lógicos do Esquema Estrela em uma única varredura antecipada (JOIN), prevenindo gargalos de N+1 consultas.
* **Contratos Seguros:** Conversão automática dos objetos do ORM para payloads JSON hierárquicos e rigorosamente tipados.
* **Operações Idempotentes:** A carga de dados no banco utiliza chaves únicas (como o Código GGREM) para garantir atualizações via *Upsert*, mantendo o catálogo temporalmente consistente e livre de duplicidades.

## 🚀 Como Executar Localmente

**Pré-requisitos:** Certifique-se de ter o Docker e o Docker Compose instalados.

1. Clone o repositório:
git clone https://github.com/silveiramatheus/tcc-anvisa-microservices.git

2. Acesse a pasta do projeto:
cd tcc-anvisa-microservices

3. Configure as variáveis de ambiente:
cp .env.example .env

4. Suba a infraestrutura via Docker:
docker-compose up -d --build

5. Acesse o painel do Airflow (`http://localhost:8080`) para engatilhar a DAG de ingestão.

## 📖 Documentação da API
O microsserviço gera nativamente a documentação interativa baseada no padrão OpenAPI. Com os contêineres em execução, acesse:

* **Swagger UI:** `http://localhost:8000/docs`

Através desta interface, é possível explorar os esquemas de validação e realizar testes práticos parametrizados buscando os medicamentos por substância, forma farmacêutica e concentração.

## 👨‍💻 Autor
**Matheus Souza da Silveira**  
Graduando em Engenharia de Computação - Universidade Federal do Rio Grande do Sul (UFRGS)