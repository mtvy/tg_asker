
HOST = 'localhost:8080'
DB_HOST = 'postgres://postgres:postgres@postgres:5433/postgres'

import dotenv, os
import cases, logger
from telebot import TeleBot

dotenv.load_dotenv('.env')

log = logger.newLogger(__name__, logger.DEBUG)

token = os.getenv('TOKEN')
admins = os.getenv('ADMINS')
dev = os.getenv('DEV')

def db_test():
    import cases.db.grpc_py_database_accessing.client as cli
    db = cli.Database(HOST, DB_HOST)
    log.info(db.get(columns="*", table='chat_tb', condition=""))

# def addAsk_test():
#     cases.addAsk(log, TeleBot(token), dev)


if __name__ == "__main__":
    db_test()
    # addAsk_test()