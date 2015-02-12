CREATE KEYSPACE IF NOT EXISTS mykeyspace
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE mykeyspace;

CREATE TABLE IF NOT EXISTS superdupertable (
  uid UUID PRIMARY KEY,
  name text,
  body text,
  insert_time timestamp
);
