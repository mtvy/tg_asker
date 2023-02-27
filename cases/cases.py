from .utils import (
    sendMsg,
    waitMsg,
    getKb,
)
from telebot import TeleBot
from telebot.types import Message

TGLINK = 'https://t.me/'
ADDKB = ['Канал/Чат', 'Опрос']
DEFALTKB = ['Отправить', 'Добавить', 'Удалить', 'Показать']

def addBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'addBtn user:{tid}')
    sendMsg(log, bot, tid, 'Что добавить?', getKb(log, ADDKB))

def addChat(log, bot: TeleBot, tid: str|int) -> None:
    def _add(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text

        if TGLINK in txt:
            log.debug(f"Link:'{txt}'.")
            
        else:
            log.debug(f"Wrong link:'{txt}' format.")
            sendMsg(log, bot, tid, f'Неправильный формат ссылки ({TGLINK})', getKb(DEFALTKB))
    
    log.debug(f'addChat user:{tid}')
    waitMsg(log, bot, tid, _add, 'Введите ссылку.', getKb(DEFALTKB), [log, bot, tid])