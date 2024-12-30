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
        CREATE TABLE IF NOT EXISTS Usuario (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            email VARCHAR(100),
            endereco VARCHAR(100),
            genero CHAR(1),
            senha VARCHAR(100),
            idioma VARCHAR(100),
            numero_amigos INT,
            idade INT,
            salario FLOAT,
            ponto_fidelidade INT,
            quantidade_compras INT
        )
    """)
    
    # Criando índices
    cur.execute("""
        -- Índice Hash para a coluna 'email', útil para buscas de igualdade
        CREATE INDEX IF NOT EXISTS idx_usuario_email_hash ON Usuario USING HASH (email);

        -- Índice B-tree para a coluna 'nome', caso seja utilizado em buscas frequentes
        CREATE INDEX IF NOT EXISTS idx_usuario_nome ON Usuario (nome);

        -- Índice B-tree para a coluna 'idade', para consultas por faixa etária
        CREATE INDEX IF NOT EXISTS idx_usuario_idade ON Usuario (idade);

        -- Índice GIN para o campo 'endereco' caso tenha buscas por partes do texto
        CREATE INDEX IF NOT EXISTS idx_usuario_endereco ON Usuario USING GIN (endereco gin_trgm_ops);
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
            INSERT INTO Usuario (nome, email, endereco, genero, senha, idioma, numero_amigos, idade, salario, ponto_fidelidade, quantidade_compras)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
    return [(fake.name(), fake.email(), fake.address(), fake.random_element(elements=('M', 'F')), fake.password(), fake.language_code(), fake.random_int(0, 100), fake.random_int(18, 80), fake.random_int(1_000, 10_000), fake.random_int(0, 100), fake.random_int(1, 100))
             for _ in range(qtd)]

# Função para gerenciar a geração e inserção dos dados em paralelo


def inserir_infinitamente():
    """Insere dados infinitamente utilizando dois pools de threads."""
    with ThreadPoolExecutor(max_workers=num_threads_cpu) as executor_cpu, ThreadPoolExecutor(max_workers=num_threads_io) as executor_io:
        while True:
            # Gera os dados utilizando as threads CPU-bound
            futuros_dados = [executor_cpu.submit(gerar_dados, qtd_por_thread) for _ in range(num_threads_io)]
            dados = [futuro.result() for futuro in futuros_dados]

            # Envia os dados para o banco usando as threads I/O-bound
            futuros_insercao = [executor_io.submit(inserir_dados_pool, dados[i]) for i in range(num_threads_io)]
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
