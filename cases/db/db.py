from .grpc_py_database_accessing.client import Database

DBHOST = 'postgres://postgres:postgres@postgres:5433/postgres'
HOST = 'localhost:8080'

db = Database(HOST, DBHOST)
