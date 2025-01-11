-- Pegar o tamanho da tabela
SELECT pg_size_pretty(pg_total_relation_size('my_table'));
SET enable_seqscan = off;
-- Consulta com index basico
SET enable_seqscan = on;

=======================================================================================================

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
CREATE INDEX IF NOT EXISTS idx_transacoes_data_brin ON my_table USING BRIN (data);

=======================================================================================================

-- Consulta com index avançado 2-3 tree == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table ORDER BY nome;

-- Consulta com index avançado GIN == OKAY

SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome LIKE '%Jo%';

-- Consulta com index avançado GIST == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table WHERE descricao_tsv @@ plainto_tsquery('João');

-- Consulta com index avançado SPGIST == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table WHERE texto LIKE 'Jo%';

-- Consulta com index avançado BRIN == OKAY
SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT * FROM my_table WHERE data BETWEEN '2024-01-01' AND '2024-12-31';

-- Pegar a quantidade de linhas da tabela
EXPLAIN ANALYZE SELECT COUNT(*) FROM my_table;