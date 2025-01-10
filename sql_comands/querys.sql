-- Pegar o tamanho da tabela
SELECT pg_size_pretty(pg_total_relation_size('usuario'));

-- Consulta com index basico

EXPLAIN SELECT * FROM Usuario WHERE email = 'sarahesparza@example.com';

EXPLAIN SELECT * FROM Usuario WHERE nome = 'Kim Evans';

EXPLAIN SELECT * FROM Usuario WHERE nome LIKE 'Kim%';

EXPLAIN SELECT * FROM Usuario WHERE idade BETWEEN 18 AND 18;

EXPLAIN SELECT * FROM Usuario WHERE endereco ILIKE '%South%' ;

EXPLAIN SELECT * FROM Usuario WHERE email  ILIKE  '%example%' AND idade > 25;

-- Pegar a quantidade de linhas da tabela
EXPLAIN SELECT COUNT(*) FROM usuario;