import psycopg2
from psycopg2.extras import DictCursor

db_config = {
    'dbname': 'Database_BD2',
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

# Esses são os índices que serão testados
indices = [
    "CREATE INDEX IF NOT EXISTS idx_tabela_hash ON my_table USING HASH(nome);",
    "CREATE INDEX IF NOT EXISTS idx_tabela_nome_b_tree ON my_table(nome);",
    "CREATE INDEX IF NOT EXISTS idx_tabela_nome_gin ON my_table USING GIN (nome gin_trgm_ops);"
]

# Consulta que será testada
query = "EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome = 'João';"

def connect_to_db(config):
    try:
        return psycopg2.connect(**config)
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def execute_query(cursor, query):
    cursor.execute(query)
    if cursor.description: 
        return cursor.fetchall()
    return None

def criador_de_indices(cursor, indices):
    for index in indices:
        try:
            cursor.execute(index)
        except psycopg2.Error as e:
            print(f"Erro ao criar índice: {index}\n{e}")

def remove_todos_index(cursor, table_name):
    """Remove todos os índices de uma tabela, exceto os índices de restrições."""
    try:
        cursor.execute(f"""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = '{table_name}'
              AND indexname NOT LIKE '%pkey%'   -- Exclui índices de chave primária
              AND indexname NOT LIKE '%unique%' -- Exclui índices de restrições únicas
        """)
        index_names = [row[0] for row in cursor.fetchall()]
        
        for index_name in index_names:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
            print(f"Removido índice: {index_name}")
    except psycopg2.Error as e:
        print(f"Erro ao remover índices: {e}")


def tirar_ou_colocar_aquele_bagulho(cursor, enable_seqscan, enable_indexscan):
    execute_query(cursor, f"SET enable_seqscan = {'on' if enable_seqscan else 'off'};")
    execute_query(cursor, f"SET enable_indexscan = {'on' if enable_indexscan else 'off'};")

def execultar_teste(cursor, query):
    return execute_query(cursor, query)

def exibir_resultados(title, results):
    print(f"\n{title}")
    for row in results:
        print(row[0])

def test_para_cada_index(cursor, query, indices, table_name):
    tirar_ou_colocar_aquele_bagulho(cursor, enable_seqscan=False, enable_indexscan=True)
    print("\nTestando consulta com cada índice individualmente:")
    
    for index in indices:
        # Extrai o nome do índice, Pode ser dificil de entender, mas se você quiser entender, eu posso explicar
        index_name = index.split("ON")[0].split("IF NOT EXISTS")[-1].strip()
        
        try:
            # Remove todos os índices antes de criar o próximo
            remove_todos_index(cursor, table_name)
            cursor.execute(index)  # Cria o índice atual
            cursor.connection.commit() # Commit para garantir que o índice foi criado

            print(f"\nTestando com índice: {index_name}")
            results = execultar_teste(cursor, query)
            exibir_resultados(f"Resultados com índice {index_name}:", results)
        except psycopg2.Error as e:
            print(f"Erro ao testar com índice {index_name}: {e}")

    tirar_ou_colocar_aquele_bagulho(cursor, enable_seqscan=True, enable_indexscan=True)

def test_sem_index(cursor, query, table_name):
    """Testa a consulta sem nenhum índice."""
    remove_todos_index(cursor, table_name)  # Remove todos os índices
    tirar_ou_colocar_aquele_bagulho(cursor, enable_seqscan=True, enable_indexscan=False)
    print("\nTestando consulta sem nenhum índice:")
    results = execultar_teste(cursor, query)
    exibir_resultados("Resultados sem índice:", results)

def main():
    connection = connect_to_db(db_config)
    if not connection:
        return

    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            table_name = 'my_table'
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            connection.commit()

            test_sem_index(cursor, query, table_name)
            test_para_cada_index(cursor, query, indices, table_name)

    except psycopg2.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
