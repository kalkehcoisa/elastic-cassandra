CREATE KEYSPACE IF NOT EXISTS mykeyspace
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE mykeyspace;

CREATE TABLE IF NOT EXISTS users (
  uid UUID PRIMARY KEY,
  fname text,
  lname text
);
