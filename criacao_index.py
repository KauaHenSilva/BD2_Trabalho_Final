import psycopg2

# Configurações do banco de dados
db_config = {
    'dbname': 'Database_BD2',
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

# Conectando ao banco de dados
conn = psycopg2.connect(**db_config)
cur = conn.cursor()

# Criar a extensão pg_trgm, caso não exista
# cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

# 1. Criar a tabela de exemplo
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
conn.commit()

# 2. Criar os índices de exemplo

# 2.1. Índice B-tree (padrão)
cur.execute("CREATE INDEX IF NOT EXISTS idx_nome_btree ON Usuario (nome)")

# 2.2. Índice Hash
cur.execute("CREATE INDEX IF NOT EXISTS idx_nome_hash ON Usuario USING hash (nome)")

# 2.3. Índice GiST (usando pg_trgm)
cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_nome_gist ON Usuario USING gist (nome gist_trgm_ops)
""")

# 2.4. Índice SP-GiST
# cur.execute("""
#     CREATE INDEX IF NOT EXISTS idx_nome_spgist ON Usuario USING spgist (nome spgist_ops)
# """)

# 2.5. Índice GIN (usado para busca de texto completo ou arrays)
cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_email_gin ON Usuario USING gin (email gin_trgm_ops)
""")

# 2.6. Índice BRIN
cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_id_brin ON Usuario USING brin (id)
""")

conn.commit()

# Fechando a conexão
cur.close()
conn.close()

print("Índices criados com sucesso.")
