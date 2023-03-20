from .utils import (
    send_photo,
    send_doc,
    send_msg,
    wait_msg,

    get_kb,
    get_ikb,
    
    save_txt,
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
    send_msg(log, bot, tid, 'Что добавить?', get_kb(log, ADDKB))


def addAsk(log, bot: TeleBot, tid: str|int) -> None:
    def _add(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text.replace('\n', '')
        log.debug(f"Ask:'{txt}'.")
        head_ind = txt.find(HEAD)
        sub_ind = txt.find(SUB)
        log.debug(f'head_ind:{head_ind}, sub_ind:{sub_ind}')
        if -1 in (head_ind, sub_ind):
            log.debug(f"Wrong ask:'{txt}' format.")
            send_msg(log, bot, tid, f'Неправильный формат опроса ({ASKEXAMPLE})', get_kb(log, DEFALTKB))
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
            send_msg(log, bot, tid, DBERR, rmvKb())
            return
        send_msg(log, bot, tid, 'Сохранено.', get_kb(log, DEFALTKB))
    
    log.debug(f'addAsk user:{tid}')
    wait_msg(log, bot, tid, _add, f'Введите заголовок и текст.\n{ASKEXAMPLE}', rmvKb(), [log, bot, tid])


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
            send_msg(log, bot, tid, f'Неправильный формат ссылки ({TGLINK})', get_kb(log, DEFALTKB))
            return

        loop = asyncio.new_event_loop()
        task = loop.create_task(_getEntity(txt))

        loop.run_until_complete(task)

        chat = task.result()
        log.debug(chat)
        
        if not hasattr(chat, 'id'):
            log.debug(f'No id chat:{chat}')
            send_msg(log, bot, tid, f'Ошибка получения данных о канале/чате.', get_kb(log, DEFALTKB))
            return

        txt = txt.replace(TGLINK, '')

        if (stat := db.insert('chat_tb', 'tid, chat', f"({chat.id}, '{txt}')").status) != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, DBERR, rmvKb())
            return
        log.info(f'insert:{"chat_tb"},{"chat"},{txt}')
        send_msg(log, bot, tid, 'Сохранено.', get_kb(log, DEFALTKB))
    
    log.debug(f'addChat user:{tid}')
    wait_msg(log, bot, tid, _add, 'Введите ссылку.', rmvKb(), [log, bot, tid])

def showBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'showBtn user:{tid}')
    send_msg(log, bot, tid, 'Что нужно открыть?', get_kb(log, SHOWKB))

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
        \tId таблицы:{ask[0]}
        \tЗаглавие:{ask[1]}
        \tТемы:{ask[2]['Elements']}
        \tДата добавления:{ask[3]}\n
        """
    return asks
    

def showAsk(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'showAsk user:{tid}')
    data, stat = db.get('*', 'ask_tb', '')
    if stat != 'ok':
        log.error(f'stat:{stat} data:{data}')
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    asks = 'Нет данных' if not len(data) else formatAsk(data)
    send_msg(log, bot, tid, asks, get_kb(log, DEFALTKB))

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
        \tId в таблице:{chat[0]}
        \tId в телеграмме:{chat[1]['Int']}{'0'*chat[1]['Exp']}
        \tИмя:{chat[2]}
        \tДата добавления:{chat[3]}
        """
    return chats

def showChat(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'showChat user:{tid}')
    data, stat = db.get('*', 'chat_tb', '')
    if stat != 'ok':
        log.error(f'stat:{stat} data:{data}')
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    chats = 'Нет данных по каналам' if not len(data) else formatChat(data)
    send_msg(log, bot, tid, chats, get_kb(log, DEFALTKB))

def delBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'delBtn user:{tid}')
    send_msg(log, bot, tid, 'Что нужно удалить?', get_kb(log, DELKB))

def delAsk(log, bot: TeleBot, tid: str|int) -> None:
    def _del(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text
        
        if not txt.isdigit():
            log.info(f"Wrong id:'{txt}' got.")
            send_msg(log, bot, tid, 'Неправильный формат id. (нужно только число)', get_kb(log, DEFALTKB))
            return
        
        log.info(f"id:'{txt}'.")
        aid = int(txt)
        
        if (stat := db.delete('ask_tb', f'where id={aid}').status) != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
            return
        
        send_msg(log, bot, tid, f'Удалено id:{aid}', get_kb(log, DEFALTKB))

    log.debug(f'delAsk user:{tid}')
    wait_msg(log, bot, tid, _del, f'Введите id опроса.', rmvKb(), [log, bot, tid])


def delChat(log, bot: TeleBot, tid: str|int) -> None:
    def _del(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        txt = msg.text
        
        if not txt.isdigit():
            log.info(f"Wrong id:'{txt}' got.")
            send_msg(log, bot, tid, 'Неправильный формат id. (нужно только число)', get_kb(log, DEFALTKB))
            return
        
        log.info(f"id:'{txt}'.")
        aid = int(txt)
        
        if (stat := db.delete('chat_tb', f'where id={aid}').status) != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
            return
        
        send_msg(log, bot, tid, f'Удалено id:{aid}', get_kb(log, DEFALTKB))

    log.debug(f'delChat user:{tid}')
    wait_msg(log, bot, tid, _del, f'Введите id канала/чата.', rmvKb(), [log, bot, tid])


def sendBtnAsk(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'sendBtnAsk user:{tid}')
    data, stat = db.get('*', 'ask_tb', '')
    if stat != 'ok':
        log.error(stat)
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('Empty asks')
        send_msg(log, bot, tid, 'Добавьте опрос.', get_kb(log, DEFALTKB))
        return
    log.debug(data)
    asks = 'Нет данных' if not len(data) else formatAsk(data)
    send_msg(log, bot, tid, asks, get_kb(log, [f'Опрос {i[0]}' for i in data.values()]))

def sendBtnChat(log, bot: TeleBot, tid: str|int, aid: str|int, photo: bytes) -> None:
    def _send(msg: Message, log, bot: TeleBot, tid: str|int, aid: str|int) -> None:
        cid = msg.text.replace('Канал ', '')
        if not cid.isdigit():
            log.warning(f'Empty aid:{cid}')
            send_msg(log, bot, tid, 'Ошибка.', get_kb(log, DEFALTKB))
            return
       
        adata, stat = db.get('*', 'ask_tb', f'where id={aid}')
        if stat != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
            return
        log.debug(adata)
        if not len(adata) or not len(adata['0']):
            log.debug(f'Empty or wrong adata:{adata}')
            send_msg(log, bot, tid, 'Не найден id.', get_kb(log, DEFALTKB))
            return
        
        cdata, stat = db.get('*', 'chat_tb', f'where id={cid}')
        if stat != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
            return
        log.debug(cdata)
        if not len(cdata) or not len(cdata['0']):
            log.debug(f'Empty or wrong cdata:{cdata}')
            send_msg(log, bot, tid, 'Не найден id.', get_kb(log, DEFALTKB))
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
        asks = 'Нет данных по опросам' if not len(adata) else formatAsk(adata)
        chats = 'Нет данных по каналам' if not len(cdata) else formatChat(cdata)
        send_msg(log, bot, tid, f'{asks}\n\n{chats}\n\n{atitle}\n{abtns}', get_kb(log, DEFALTKB))
        msg = send_photo(log, bot, f'-100{cid}', atitle, photo, get_ikb(log, abtns))
        
        log.debug(msg)
        if msg is None or not hasattr(msg, 'message_id'):
            log.error(f'Wrong msg:{msg}')
            send_msg(log, bot, tid, 'Ошибка отправки. К опросу нет доступа!', get_kb(log, DEFALTKB))
            return
        
        mid = msg.message_id
        
        if (stat := db.insert('active_tb', 'cid, aid, mid, res, stat', f"({cdata['0'][0]}, {adata['0'][0]}, {mid}, '{jsonb}', TRUE)").status) != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, 'Ошибка сохранения. К опросу нет доступа!', get_kb(log, DEFALTKB))
            return
        

    log.debug(f'sendBtnChat user:{tid}')
    data, stat = db.get('*', 'chat_tb', '')
    if stat != 'ok':
        log.error(stat)
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('Empty chats')
        send_msg(log, bot, tid, 'Добавьте канал/чат.', get_kb(log, DEFALTKB))
        return
    log.debug(data)
    chats = 'Нет данных по каналам' if not len(data) else formatChat(data)
    wait_msg(log, bot, tid, _send, chats, get_kb(log, [f'Канал {i[0]}' for i in data.values()]), [log, bot, tid, aid])

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
    max_votes = 0; max_votes_ask = ''; sum_votes = 0

    for ind, chat in data.items():
        res = ''
        for k, v in chat[3].items():
            res = f"""{res}
                    Опрос: {k}
                    Количество голосов:{v[0]}
                    Id Голосовавшего:{v[1]}
            """
            if v[0] > max_votes:
                max_votes = v[0]
                max_votes_ask = k
            sum_votes += v[0]
        res = f"""
            Всего голосов: {sum_votes}
            Больше всего голосов:
                Число голосов: {max_votes}
                Тема: {max_votes_ask}
                Процент относительно всех голосов: {'-' if not (max_votes and sum_votes) else (100*max_votes)/sum_votes}
        {res}
        """
        chats = f"""{chats}
{int(ind)+1})
        Id в таблице результатов:{chat[0]}
        Id опроса:{chat[1]}
        Id сообщения в чате:{chat[2]}
        Результаты опроса:{res}
        Статус опроса:{'Включен' if chat[4] else 'Отключен'}
        Id Канала/Чата:{chat[5]['Int']}{'0'*chat[5]['Exp']}
        Название Канала/Чата:{chat[6]}
        """
    return chats

def resBtn(log, bot: TeleBot, tid: str|int) -> None:
    log.debug(f'resBtn user:{tid}')
    data, stat = db.get('count(id)', 'active_tb', '')
    if stat != 'ok':
        log.error(stat)
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('No askers')
        send_msg(log, bot, tid, 'Нет отправленных опросов.', get_kb(log, DEFALTKB))
        return

    data, stat = db.get(active_col, active_tb, '')
    if stat != 'ok':
        log.error(stat)
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('No askers')
        send_msg(log, bot, tid, 'Нет отправленных опросов.', get_kb(log, DEFALTKB))
        return
    data = formatRes(data)
    save_txt(data, RESFL, 'w')
    send_doc(log, bot, tid, 'Результаты по опросам.', RESFL, get_kb(log, DEFALTKB))
    
def stopBtn(log, bot: TeleBot, tid: str|int) -> None:
    def _stop(msg: Message, log, bot: TeleBot, tid: str|int) -> None:
        actid = msg.text
        if not actid.isdigit():
            log.debug(f'actid:{actid}')
            send_msg(log, bot, tid, 'Неправильный формат id.', get_kb(log, DEFALTKB))
            return
        if (stat := db.update('active_tb', 'stat=false', f"where id={actid}").status) != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
            return
        send_msg(log, bot, tid, f'Остоновка прошла успешно.', get_kb(log, DEFALTKB))


    log.debug(f'stopBtn user:{tid}')
    data, stat = db.get(active_col, active_tb, 'where stat=True')
    if stat != 'ok':
        log.error(stat)
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        log.debug('No askers')
        send_msg(log, bot, tid, 'Нет отправленных опросов.', get_kb(log, DEFALTKB))
        return
    txt = formatRes(data)
    wait_msg(log, bot, tid, _stop, txt, get_kb(log, [i[0] for i in data.values()]), [log, bot, tid])
