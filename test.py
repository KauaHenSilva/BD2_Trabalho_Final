import psycopg2
from psycopg2.extras import DictCursor

# Cores para saída no terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

db_config = {
    'dbname': 'Database_BD2',
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

# Índices que serão testados
indices = [
    ("CREATE INDEX IF NOT EXISTS idx_tabela_hash ON my_table USING HASH(nome);", "HASH"),
    ("CREATE INDEX IF NOT EXISTS idx_tabela_nome_b_tree ON my_table(nome);", "B-Tree"),
    ("CREATE INDEX IF NOT EXISTS idx_tabela_nome_gin ON my_table USING GIN (nome gin_trgm_ops);", "GIN")
]

# Consultas que serão testadas
queries = [
    ("EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome = 'João';", "igual"),
    ("EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome < 'João';", "menor"),
    ("EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome > 'João';", "maior")
]

def connect_to_db(config):
    try:
        print(f"{Colors.OKBLUE}Conectando ao banco de dados...{Colors.ENDC}")
        return psycopg2.connect(**config)
    except psycopg2.Error as e:
        print(f"{Colors.FAIL}Erro ao conectar ao banco de dados: {e}{Colors.ENDC}")
        return None

def execute_query(cursor, query):
    cursor.execute(query)
    if cursor.description: 
        return cursor.fetchall()
    return None

def remove_todos_index(cursor, table_name):
    """Remove todos os índices de uma tabela, exceto os índices de restrições."""
    try:
        print(f"{Colors.OKBLUE}Removendo índices existentes na tabela {table_name}...{Colors.ENDC}")
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
            print(f"{Colors.WARNING}Removido índice: {index_name}{Colors.ENDC}")
    except psycopg2.Error as e:
        print(f"{Colors.FAIL}Erro ao remover índices: {e}{Colors.ENDC}")

def set_optimizer_settings(cursor, enable_seqscan, enable_indexscan):
    execute_query(cursor, f"SET enable_seqscan = {'on' if enable_seqscan else 'off'};")
    execute_query(cursor, f"SET enable_indexscan = {'on' if enable_indexscan else 'off'};")

def execute_test(cursor, query):
    return execute_query(cursor, query)

def display_results(title, results):
    print(f"{Colors.HEADER}\n{title}{Colors.ENDC}")
    for row in results:
        print(f"{Colors.OKGREEN}{row[0]}{Colors.ENDC}")

def test_by_index_type(cursor, indices, queries, table_name):
    set_optimizer_settings(cursor, enable_seqscan=False, enable_indexscan=True)
    for index_query, index_type in indices:
        print(f"{Colors.BOLD}\n{'=' * 50}\nTestando índices do tipo: {index_type}{Colors.ENDC}")
        cursor.execute(index_query)
        cursor.connection.commit()

        for query, condition in queries:
            if index_type == "HASH" and condition in ["menor", "maior"]:
                print(f"{Colors.WARNING}Índice {index_type} ignorado para condição '{condition}'.{Colors.ENDC}")
                continue

            print(f"{Colors.OKBLUE}\nExecutando consulta: {query}{Colors.ENDC}")
            results = execute_test(cursor, query)
            display_results(f"Resultados para índice {index_type} ({condition}):", results)
        
        # Remove índices após teste
        remove_todos_index(cursor, table_name)

    set_optimizer_settings(cursor, enable_seqscan=True, enable_indexscan=True)

def test_without_indices(cursor, queries, table_name):
    print(f"{Colors.BOLD}\n{'=' * 50}\nTestando consultas sem índices...{Colors.ENDC}")
    remove_todos_index(cursor, table_name)
    set_optimizer_settings(cursor, enable_seqscan=True, enable_indexscan=False)

    for query, condition in queries:
        print(f"{Colors.OKBLUE}\nExecutando consulta: {query}{Colors.ENDC}")
        results = execute_test(cursor, query)
        display_results(f"Resultados sem índice ({condition}):", results)

def main():
    connection = connect_to_db(db_config)
    if not connection:
        return

    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            table_name = 'my_table'
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            connection.commit()

            test_without_indices(cursor, queries, table_name)
            test_by_index_type(cursor, indices, queries, table_name)

    except psycopg2.Error as e:
        print(f"{Colors.FAIL}Erro ao acessar o banco de dados: {e}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Erro inesperado: {e}{Colors.ENDC}")
    finally:
        connection.close()
        print(f"{Colors.OKGREEN}\nConexão com o banco de dados encerrada.{Colors.ENDC}")

if __name__ == "__main__":
    main()
