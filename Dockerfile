FROM alpine:latest
FROM python:latest

WORKDIR /app

ADD . /app/

RUN pip install -r requirements.txt

CMD python bot.py
# CMD ls && echo "\n\n" && cd cases/db/grpc_py_database_accessing && ls && echo "\n\n\n"