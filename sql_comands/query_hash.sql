-- Verificar o tamanho da tabela
SELECT pg_size_pretty(pg_total_relation_size('my_table'));

-- Desativar varredura sequencial
SET enable_seqscan = off;

-- Desativar o uso de índices hash
SET enable_indexscan = off;''

-- Executar consulta
EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome = 'João';

-- Reativar varredura sequencial
SET enable_seqscan = on;

-- Reativar o uso de índices
SET enable_indexscan = on;

-- Executar consulta novamente com índices habilitados
EXPLAIN ANALYZE SELECT * FROM my_table WHERE nome = 'João';
