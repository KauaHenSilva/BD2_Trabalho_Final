-- Pegar o tamanho da tabela
SELECT pg_size_pretty(pg_total_relation_size('my_table'));
SET enable_seqscan = off;
SET enable_seqscan = on;
-- Consulta com index basico



-- Consulta com index avançado 2-3 tree == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table ORDER BY nome;

-- Consulta com index avançado GIN == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome LIKE '%Jo%';

-- Consulta com index avançado GIST == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table WHERE descricao_tsv @@ plainto_tsquery('João');

-- Consulta com index avançado SPGIST == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table WHERE texto LIKE 'Jo%';

-- Consulta com index avançado BRIN == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table WHERE data BETWEEN '2024-01-01' AND '2024-12-31';

-- Pegar a quantidade de linhas da tabela
EXPLAIN ANALYZE SELECT COUNT(*) FROM my_table;