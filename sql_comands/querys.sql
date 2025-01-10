-- Pegar o tamanho da tabela
SELECT pg_size_pretty(pg_total_relation_size('usuario'));
SET enable_seqscan = off;
-- Consulta com index basico

EXPLAIN ANALYZE SELECT * FROM my_table WHERE email = 'sarahesparza@example.com';

-- Consulta com index avançado hash == OKAY
EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome = 'João';

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