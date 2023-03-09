from .utils import (
    sendPhoto,
    sendDoc,
    sendMsg,
    waitMsg,

    getKb,
    getIKb,
    
    saveTxt,
)
from .db import (
    db,
)
from telebot.types import (
    ReplyKeyboardRemove as rmvKb,
    Message,
)
from telethon import (
    TelegramClient,
)
from telebot import TeleBot
import asyncio, json, os

TGLINK = 'https://t.me/'
ADDKB = ['Канал/Чат', 'Опрос']
DEFALTKB = ['Отправить', 'Добавить', 'Удалить', 'Показать', 'Остановить']
SHOWKB = ['Опросы', 'Каналы/Чаты', 'Результаты']
DELKB = ['Удалить опросы', 'Удалить канал/чат']

DBERR = 'Ошибка.'
ASKER = 'ASKER'

RESFL = os.path.join('data', 'res.txt')

HEAD = "!З"
SUB = "!Т"
ASKEXAMPLE = f"""
{HEAD} Пример заголовка
{SUB} Тема1
{SUB} Тема2
"""

active_col = """
    active_tb.id as "Active Table ID",
    active_tb.aid as "Ask ID",
    active_tb.mid as "Message ID",
    active_tb.res as "Ask Result",
    active_tb.stat as "Is Active",
    chat_tb.tid as "Chat Telegram ID",
    chat_tb.chat as "Chat Name"
"""
active_tb = """
    active_tb join chat_tb on active_tb.cid = chat_tb.id
"""


def addBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'addBtn user:{tid}')
    sendMsg(log, bot, tid, 'Что добавить?', getKb(log, ADDKB))


def addAsk(log, bot: TeleBot, tid: str|int) -> None:
    def _add(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text.replace('\n', '')
        log.debug(f"Ask:'{txt}'.")
        head_ind = txt.find(HEAD)
        sub_ind = txt.find(SUB)
        log.debug(f'head_ind:{head_ind}, sub_ind:{sub_ind}')
        if -1 in (head_ind, sub_ind):
            log.debug(f"Wrong ask:'{txt}' format.")
            sendMsg(log, bot, tid, f'Неправильный формат опроса ({ASKEXAMPLE})', getKb(log, DEFALTKB))
            return
        
        req = f"('{txt[txt.find(HEAD)+3:txt.find(SUB)]}', array["
        for i in txt[txt.find(SUB):].split(SUB):
            if not i:
                continue
            req = f"{req}'{i[1:]}',"
        req = f'{req[:-1]}])'
        
        log.info(f"insert:'{req}'")

        # TODO: Exist check
        
        if (stat := db.insert('ask_tb', 'head, sub', req).status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, DBERR, rmvKb())
            return
        sendMsg(log, bot, tid, 'Сохранено.', getKb(log, DEFALTKB))
    
    log.debug(f'addAsk user:{tid}')
    waitMsg(log, bot, tid, _add, f'Введите заголовок и текст.\n{ASKEXAMPLE}', rmvKb(), [log, bot, tid])


def addChat(log, bot: TeleBot, tid: str|int, token: str, name, api_id, api_hash) -> None:
    async def _getEntity(link):
        log.info(f'Start cli as [{token}]')
        log.info("Get client")
        client = TelegramClient(name, api_id, api_hash)
        await client.start(bot_token=token)

        chat = await client.get_entity(link)
        await client.disconnect()
        return chat

    def _add(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text
        log.debug(f"Link:'{txt}'.")
        if TGLINK not in txt:
            log.debug(f"Wrong link:'{txt}' format.")
            sendMsg(log, bot, tid, f'Неправильный формат ссылки ({TGLINK})', getKb(log, DEFALTKB))
            return

        loop = asyncio.new_event_loop()
        task = loop.create_task(_getEntity(txt))

        loop.run_until_complete(task)

        chat = task.result()
        log.debug(chat)
        
        if not hasattr(chat, 'id'):
            log.debug(f'No id chat:{chat}')
            sendMsg(log, bot, tid, f'Ошибка получения данных о канале/чате.', getKb(log, DEFALTKB))
            return

        txt = txt.replace(TGLINK, '')

        if (stat := db.insert('chat_tb', 'tid, chat', f"({chat.id}, '{txt}')").status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, DBERR, rmvKb())
            return
        log.info(f'insert:{"chat_tb"},{"chat"},{txt}')
        sendMsg(log, bot, tid, 'Сохранено.', getKb(log, DEFALTKB))
    
    log.debug(f'addChat user:{tid}')
    waitMsg(log, bot, tid, _add, 'Введите ссылку.', rmvKb(), [log, bot, tid])

def showBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'showBtn user:{tid}')
    sendMsg(log, bot, tid, 'Что нужно открыть?', getKb(log, SHOWKB))

def formatAsk(data) -> str:
    """
    {'0': [
        1, 
        'Пример заголовка', 
        {
            'Elements': ['Тема1', 'Тема2'], 
            'Dimensions': [{'Length': 2, 'LowerBound': 1}], 
            'Status': 2
        }, 
        '2023-03-04T23:26:18.072489Z'
    ]}
    """
    asks = ''
    for ind, ask in data.items():
        asks = f"""{asks}
    {int(ind)+1})
        \tTable Id:{ask[0]}
        \tTitile:{ask[1]}
        \tSubjects:{ask[2]['Elements']}
        \tAdd Date:{ask[3]}\n
        """
    return asks
    

def showAsk(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'showAsk user:{tid}')
    data, stat = db.get('*', 'ask_tb', '')
    if stat != 'ok':
        log.error(f'stat:{stat} data:{data}')
        sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
        return
    asks = formatAsk(data)
    sendMsg(log, bot, tid, asks, getKb(log, DEFALTKB))

def formatChat(data) -> str:
    """
    {'0': [
        1, 
        {
            'Int': 1669169522, 
            'Exp': 0, 
            'Status': 2, 
            'NaN': False, 
            'InfinityModifier': 0
        }, 
        'bot_testing132', 
        '2023-03-04T23:26:10.07014Z'
    ]}
    """
    chats = ''
    for ind, chat in data.items():
        chats = f"""{chats}
{int(ind)+1})
        \tTable Id:{chat[0]}
        \tTG Id:{chat[1]['Int']}{'0'*chat[1]['Exp']}
        \tName:{chat[2]}
        \tAdd Date:{chat[3]}
        """
    return chats

def showChat(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'showChat user:{tid}')
    data, stat = db.get('*', 'chat_tb', '')
    if stat != 'ok':
        log.error(f'stat:{stat} data:{data}')
        sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
        return
    chats = formatChat(data)
    sendMsg(log, bot, tid, chats, getKb(log, DEFALTKB))

def delBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'delBtn user:{tid}')
    sendMsg(log, bot, tid, 'Что нужно удалить?', getKb(log, DELKB))

def delAsk(log, bot: TeleBot, tid: str|int) -> None:
    def _del(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text
        
        if not txt.isdigit():
            log.info(f"Wrong id:'{txt}' got.")
            sendMsg(log, bot, tid, 'Неправильный формат id. (нужно только число)', getKb(log, DEFALTKB))
            return
        
        log.info(f"id:'{txt}'.")
        aid = int(txt)
        
        if (stat := db.delete('ask_tb', f'where id={aid}').status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
            return
        
        sendMsg(log, bot, tid, f'Удалено id:{aid}', getKb(log, DEFALTKB))

    log.debug(f'delAsk user:{tid}')
    waitMsg(log, bot, tid, _del, f'Введите id опроса.', rmvKb(), [log, bot, tid])


def delChat(log, bot: TeleBot, tid: str|int) -> None:
    def _del(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text
        
        if not txt.isdigit():
            log.info(f"Wrong id:'{txt}' got.")
            sendMsg(log, bot, tid, 'Неправильный формат id. (нужно только число)', getKb(log, DEFALTKB))
            return
        
        log.info(f"id:'{txt}'.")
        aid = int(txt)
        
        if (stat := db.delete('chat_tb', f'where id={aid}').status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
            return
        
        sendMsg(log, bot, tid, f'Удалено id:{aid}', getKb(log, DEFALTKB))

    log.debug(f'delChat user:{tid}')
    waitMsg(log, bot, tid, _del, f'Введите id канала/чата.', rmvKb(), [log, bot, tid])


def sendBtnAsk(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'sendBtnAsk user:{tid}')
    data, stat = db.get('*', 'ask_tb', '')
    if stat != 'ok':
        log.error(stat)
        sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('Empty asks')
        sendMsg(log, bot, tid, 'Добавьте опрос.', getKb(log, DEFALTKB))
        return
    log.debug(data)
    asks = formatAsk(data)
    sendMsg(log, bot, tid, asks, getKb(log, [f'Опрос {i[0]}' for i in data.values()]))

def sendBtnChat(log, bot: TeleBot, tid: str|int, aid: str|int, photo: bytes) -> None:
    def _send(msg: Message, log, bot: TeleBot, tid: str|int, aid: str|int) -> None:
        cid = msg.text.replace('Канал ', '')
        if not cid.isdigit():
            log.warning(f'Empty aid:{cid}')
            sendMsg(log, bot, tid, 'Ошибка.', getKb(log, DEFALTKB))
            return
       
        adata, stat = db.get('*', 'ask_tb', f'where id={aid}')
        if stat != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
            return
        log.debug(adata)
        if not len(adata) or not len(adata['0']):
            log.debug(f'Empty or wrong adata:{adata}')
            sendMsg(log, bot, tid, 'Не найден id.', getKb(log, DEFALTKB))
            return
        
        cdata, stat = db.get('*', 'chat_tb', f'where id={cid}')
        if stat != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
            return
        log.debug(cdata)
        if not len(cdata) or not len(cdata['0']):
            log.debug(f'Empty or wrong cdata:{cdata}')
            sendMsg(log, bot, tid, 'Не найден id.', getKb(log, DEFALTKB))
            return
        cid = f"{cdata['0'][1]['Int']}{'0'*cdata['0'][1]['Exp']}"
        log.debug(cid)
        atitle = adata['0'][1]
        log.debug(atitle)
        abtns, jsonb = dict(), dict()
        for i in adata['0'][2]['Elements']:
            abtns[i] = f"{cdata['0'][0]}{ASKER}{i}"
            jsonb[i] = [0, []]
        log.debug(abtns)
        jsonb = json.dumps(jsonb)
        log.debug(jsonb)
        asks = formatAsk(adata)
        chats = formatChat(cdata)
        sendMsg(log, bot, tid, f'{asks}\n\n{chats}\n\n{atitle}\n{abtns}', getKb(log, DEFALTKB))
        msg = sendPhoto(log, bot, f'-100{cid}', atitle, photo, getIKb(log, abtns))
        
        log.debug(msg)
        if msg is None or not hasattr(msg, 'message_id'):
            log.error(f'Wrong msg:{msg}')
            sendMsg(log, bot, tid, 'Ошибка отправки. К опросу нет доступа!', getKb(log, DEFALTKB))
            return
        
        mid = msg.message_id
        
        if (stat := db.insert('active_tb', 'cid, aid, mid, res, stat', f"({cdata['0'][0]}, {adata['0'][0]}, {mid}, '{jsonb}', TRUE)").status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, 'Ошибка сохранения. К опросу нет доступа!', getKb(log, DEFALTKB))
            return
        

    log.debug(f'sendBtnChat user:{tid}')
    data, stat = db.get('*', 'chat_tb', '')
    if stat != 'ok':
        log.error(stat)
        sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('Empty chats')
        sendMsg(log, bot, tid, 'Добавьте канал/чат.', getKb(log, DEFALTKB))
        return
    log.debug(data)
    chats = formatChat(data)
    waitMsg(log, bot, tid, _send, chats, getKb(log, [f'Канал {i[0]}' for i in data.values()]), [log, bot, tid, aid])

def formatRes(data) -> str:
    """
    {'0': 
        [
            4, 
            1, 
            39, 
            {
                'Тема1': [2, [281321076, 5472647497]], 
                'Тема2': [0, []]
            }, 
            True, 
            {
                'Int': 1669169522, 
                'Exp': 0, 
                'Status': 2, 
                'NaN': False, 
                'InfinityModifier': 0
            }, 
            'bot_testing132'
    ]}
    """
    chats = ''
    for ind, chat in data.items():
        res = ''
        for k, v in chat[3].items():
            res = f"""{res}
                    Subject: {k}
                    Number of votes:{v[0]}
                    Peoples Id:{v[1]}
            """
        chats = f"""{chats}
{int(ind)+1})
        Table Id:{chat[0]}
        Ask Id:{chat[1]}
        Message Id:{chat[2]}
        Ask Result:{res}
        Is Active:{chat[4]}
        Chat TG Id:{chat[5]['Int']}{'0'*chat[5]['Exp']}
        Chat Name:{chat[6]}
        """
    return chats

def resBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'resBtn user:{tid}')
    data, stat = db.get('count(id)', 'active_tb', '')
    if stat != 'ok':
        log.error(stat)
        sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('No askers')
        sendMsg(log, bot, tid, 'Нет отправленных опросов.', getKb(log, DEFALTKB))
        return

    data, stat = db.get(active_col, active_tb, '')
    if stat != 'ok':
        log.error(stat)
        sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('No askers')
        sendMsg(log, bot, tid, 'Нет отправленных опросов.', getKb(log, DEFALTKB))
        return
    data = formatRes(data)
    saveTxt(data, RESFL, 'w')
    sendDoc(log, bot, tid, 'Результаты по опросам.', RESFL, getKb(log, DEFALTKB))
    
def stopBtn(log, bot: TeleBot, tid: str|int) -> None:
    def _stop(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        actid = msg.text
        if not actid.isdigit():
            log.debug(f'actid:{actid}')
            sendMsg(log, bot, tid, 'Неправильный формат id.', getKb(log, DEFALTKB))
            return
        if (stat := db.update('active_tb', 'stat=false', f"where id={actid}").status) != 'ok':
            log.error(stat)
            sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
            return
        sendMsg(log, bot, tid, f'Остоновка прошла успешно.', getKb(log, DEFALTKB))


    log.debug(f'stopBtn user:{tid}')
    data, stat = db.get(active_col, active_tb, 'where stat=True')
    if stat != 'ok':
        log.error(stat)
        sendMsg(log, bot, tid, DBERR, getKb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('No askers')
        sendMsg(log, bot, tid, 'Нет отправленных опросов.', getKb(log, DEFALTKB))
        return
    txt = formatRes(data)
    waitMsg(log, bot, tid, _stop, txt, getKb(log, [i[0] for i in data.values()]), [log, bot, tid])
