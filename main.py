from psycopg2.pool import ThreadedConnectionPool
from faker import Faker
from concurrent.futures import ThreadPoolExecutor
import os

# Configurações do banco de dados
db_config = {
    'dbname': 'Database_BD2',
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}


fake = Faker()

# Criação do pool de conexões para I/O-bound
num_cores = os.cpu_count()  # Número de núcleos da CPU
num_threads_cpu = num_cores  # Número de threads CPU-bound
num_threads_io = num_cores * 2  # Número de threads I/O-bound
qtd_por_thread = 1_000  # Quantidade de dados por thread

# Criação do pool de conexões
connection_pool = ThreadedConnectionPool(1, num_threads_io, **db_config)

# Função para criar a tabela no banco de dados


def criar_tabela():
    """Cria a tabela Usuario, se não existir."""
    conn = connection_pool.getconn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS my_table (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            idade INTEGER,
            descricao_tsv TSVECTOR,
            texto TEXT,
            data DATE
        )
    """)

    # Criando índices
    cur.execute("""
        -- Índice Hash para a coluna 'nome'.
        CREATE INDEX IF NOT EXISTS idx_tabela_hash ON my_table USING HASH(nome);

        -- Índice B-tree para a coluna 'nome'.
        CREATE INDEX IF NOT EXISTS idx_tabela_nome_b_tree ON my_table(nome);
        
        -- Índice GIN para o campo 'nome' caso tenha buscas por partes do texto
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        CREATE INDEX IF NOT EXISTS idx_tabela_nome_gin ON my_table USING GIN (nome gin_trgm_ops);
        
        -- Índice GIST para a coluna 'descricao_tsv'.
        CREATE INDEX IF NOT EXISTS idx_descricao_gist ON my_table USING GIST (descricao_tsv);
        
        -- Índice SPGIST para o campo 'texto' caso tenha buscas por partes do texto
        CREATE INDEX IF NOT EXISTS idx_texto_spgist ON my_table USING SPGIST (texto);
        
        -- Índice BRIN para o campo 'data' caso tenha buscas por partes do texto
        CREATE INDEX idx_transacoes_data_brin ON my_table USING BRIN (data);
    """)

    conn.commit()
    cur.close()
    connection_pool.putconn(conn)

# Função para inserir dados no banco usando uma conexão do pool


def inserir_dados_pool(dados):
    """Insere dados no banco usando uma conexão do pool."""
    conn = connection_pool.getconn()
    try:
        cur = conn.cursor()
        cur.executemany("""
            INSERT INTO my_table (nome, idade, descricao_tsv, texto, data)
            VALUES (%s, %s, to_tsvector(%s), %s, %s)
        """, dados)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
        conn.rollback()
    finally:
        connection_pool.putconn(conn)

# Função para gerar dados com Faker (CPU-bound)
def gerar_dados(qtd):
    """Gera dados usando Faker para inserção no banco."""
    
    elementos = []
    for _ in range(qtd):
        description = fake.text()
        elementos.append((fake.name(), fake.random_int(0, 100), description, description, fake.date()))
    return elementos

# Função para gerenciar a geração e inserção dos dados em paralelo
def inserir_infinitamente():
    """Insere dados infinitamente utilizando dois pools de threads."""
    with ThreadPoolExecutor(max_workers=num_threads_cpu) as executor_cpu, ThreadPoolExecutor(max_workers=num_threads_io) as executor_io:
        while True:
            # Gera os dados utilizando as threads CPU-bound
            futuros_dados = [executor_cpu.submit(
                gerar_dados, qtd_por_thread) for _ in range(num_threads_io)]
            dados = [futuro.result() for futuro in futuros_dados]

            # Envia os dados para o banco usando as threads I/O-bound
            futuros_insercao = [executor_io.submit(
                inserir_dados_pool, dados[i]) for i in range(num_threads_io)]
            for futuro in futuros_insercao:
                try:
                    futuro.result()  # Espera a inserção ser concluída
                except Exception as e:
                    print(f"Erro na inserção de dados: {e}")


if __name__ == "__main__":
    try:
        criar_tabela()
        print("Iniciando inserções em massa...")
        inserir_infinitamente()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    finally:
        # Fecha todas as conexões do pool
        if connection_pool:
            connection_pool.closeall()
        print("Conexões fechadas.")
