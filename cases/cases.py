from .utils import (
    sendMsg,
    waitMsg,
    getKb,
)

from .db import (
    db,
)

from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardRemove as rmvKb,
    Message,
)

TGLINK = 'https://t.me/'
ADDKB = ['Канал/Чат', 'Опрос']
DEFALTKB = ['Отправить', 'Добавить', 'Удалить', 'Показать']

HEAD = "!Заголовок"
SUB = "!Тема"
ASKEXAMPLE = f"""
{HEAD}: Пример заголовка
{SUB}:Тема1
{SUB}:Тема2
"""


def addBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'addBtn user:{tid}')
    sendMsg(log, bot, tid, 'Что добавить?', getKb(log, ADDKB))


def addAsk(log, bot: TeleBot, tid: str|int) -> None:
    def _add(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text
        log.debug(f"Ask:'{txt}'.")
        if HEAD not in txt or SUB not in txt:
            log.debug(f"Wrong ask:'{txt}' format.")
            sendMsg(log, bot, tid, f'Неправильный формат опроса ({ASKEXAMPLE})', getKb(log, DEFALTKB))
            return
        if (stat := db.insert('ask_tb', '...', txt).status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, 'Ошибка.', rmvKb())
            return
        log.info(f'insert:{"ask_tb"},{"..."},{txt}')
        sendMsg(log, bot, tid, 'Сохранено.', getKb(log, DEFALTKB))
    
    log.debug(f'addAsk user:{tid}')
    waitMsg(log, bot, tid, _add, f'Введите заголовок и текст.\n{ASKEXAMPLE}', rmvKb(), [log, bot, tid])


def addChat(log, bot: TeleBot, tid: str|int) -> None:
    def _add(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text
        log.debug(f"Link:'{txt}'.")
        if TGLINK not in txt:
            log.debug(f"Wrong link:'{txt}' format.")
            sendMsg(log, bot, tid, f'Неправильный формат ссылки ({TGLINK})', getKb(log, DEFALTKB))
            return
        txt = txt.replace(TGLINK, '')
        if (stat := db.insert('chat_tb', 'chat', txt).status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, 'Ошибка.', rmvKb())
            return
        log.info(f'insert:{"chat_tb"},{"chat"},{txt}')
        sendMsg(log, bot, tid, 'Сохранено.', getKb(log, DEFALTKB))
    
    log.debug(f'addChat user:{tid}')
    waitMsg(log, bot, tid, _add, 'Введите ссылку.', rmvKb(), [log, bot, tid])