/*
Código para criar/atualizar o banco de dados Cassandra para utilizar o script task.py.
*/

CREATE KEYSPACE IF NOT EXISTS mykeyspace
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE mykeyspace;

DROP TABLE IF EXISTS superdupertable;

CREATE TABLE IF NOT EXISTS superdupertable (
  uid UUID,
  name text,
  body text,
  last_change timestamp,
  PRIMARY KEY (uid, last_change)
);