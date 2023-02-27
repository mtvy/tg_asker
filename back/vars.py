
CONN_ADRGS = {
    'database' : 'groups' ,
    'password' : 'groups' ,
    'user'     : 'groups' ,
    'host'     : 'postgres',
    'port'     : '5434'     
}

DBRESP = 'SELECT COUNT(1) FROM'

CR_GROUPS_TB = f'CREATE TABLE groups_tb(id serial primary key, name VARCHAR(64), msg TEXT, tid VARCHAR(64), mems VARCHAR(64)); {DBRESP} groups_tb;'

INS_TB = 'INSERT INTO _tb () VALUES '
