from .utils import (
    send_photo,
    send_msg,
    wait_msg,

    get_kb,
    get_ikb,

    Result,
    results,
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
from typing import List
from telebot import TeleBot
from datetime import datetime
import asyncio, json, os, emoji, base64

TGLINK = 'https://t.me/'
ADDKB = ['Канал/Чат', 'Опрос']
# DEFALTKB = ['Отправить', 'Добавить', 'Удалить', 'Показать', 'Остановить']
DEFALTKB = ['Отправить', 'Опросы']
SHOWKB = ['Опросы', 'Каналы/Чаты', 'Результаты']
DELKB = ['Удалить опросы', 'Удалить канал/чат']
ASKTYPEKB = ['Публичный', 'Анонимный', 'Без результата']

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

SENDFLAG = "SENDF"
STOPFLAG = "STOPF"
DELFLAG = "DELF"
RESFLAG = "RESF"

def get_asks(log, bot: TeleBot, tid: str|int) -> None:
    data, stat = db.get('*', 'ask_tb', '')
    if stat != 'ok':
        log.error(f'stat:{stat} data:{data}')
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        send_msg(log, bot, tid, 'Нет опросов для отправки.', get_kb(log, DEFALTKB))
        # create_ask(log, bot, tid)
        return
    
    send_msg(log, bot, tid, f'Всего опросов: {len(data)}', rmvKb())
    asks = formatListedAsk(data)
    for key, ask in zip(data.keys(), asks):
        if data[key][5]:
            send_msg(log, bot, tid, ask, get_ikb(log, 
                {
                    'Отправить': f'{SENDFLAG}{data[key][0]}',
                    # 'Остановить': f'{STOPFLAG}{data[key][0]}',
                    'Удалить': f'{DELFLAG}{data[key][0]}',
                    # 'Результаты': f'{RESFLAG}{data[key][0]}',
                }
            ))
        else:
            send_msg(log, bot, tid, ask, get_ikb(log, 
                {
                    'Отправить': f'{SENDFLAG}{data[key][0]}',
                    'Удалить': f'{DELFLAG}{data[key][0]}',
                    # 'Результаты': f'{RESFLAG}{data[key][0]}',
                }
            ))
    
    send_msg(log, bot, tid, f'Все опросы', get_kb(log, DEFALTKB))

def push(log, bot: TeleBot, tid: str|int, cid, adata, photo: bytes, chat) -> None:
    log.debug(adata)
    log.debug(cid)
    if not len(adata) or not len(adata['0']):
        log.debug(f'Empty or wrong adata:{adata}')
        send_msg(log, bot, tid, 'Не найден id.', get_kb(log, DEFALTKB))
        return
        
    atitle = adata['0'][1]
    log.debug(atitle)
    abtns, jsonb = dict(), dict()
    for i in adata['0'][2]['Elements']:
        abtns[i] = f"{adata['0'][0]}{ASKER}{i}"
        jsonb[i] = [0, [], []]
    
    log.debug(abtns)
    jsonb = json.dumps(jsonb)
    log.debug(jsonb)
    asks = 'Нет данных по опросам' if not len(adata) else formatAsk(adata)
    chats = chat.username

    votes = []; svotes = 0

    if adata['0'][4]:
        for _, r in adata['0'][4].items():
            svotes += r[0]
            votes.append(r[0])
        
        v = 0
        for k, r in adata['0'][4].items():
            log.debug(f"votes[{v}]:{votes[v]} svotes:{svotes}  %:{0 if not svotes else (votes[v]/svotes) * 100}")
            atitle = f"""{atitle}\n\n{k}\n{emoji.emojize(":white_small_square:")} {0 if not svotes else (votes[v]/svotes) * 100}%
            """
            v+=1
    send_msg(log, bot, tid, f'Отправленный опрос:\n{asks}\n\nКанал/чат: {chats}\n\nВопрос: {atitle}\nОтветы:\n{list(abtns.keys())}', get_kb(log, DEFALTKB))
    log.warning(f"{type(adata['0'][10])} {adata['0'][10][:20]} **** {adata['0'][10][2:20]} **** {adata['0'][10][-20:]}")
    photo = adata['0'][10].encode('utf-8')
    photobase = base64.b64decode(photo)
    msg = send_photo(log, bot, f'-100{cid}', atitle, photobase, get_ikb(log, abtns))
    log.debug(msg)
    if msg is None or not hasattr(msg, 'message_id'):
        log.error(f'Wrong msg:{msg}')
        send_msg(log, bot, tid, 'Ошибка отправки. К опросу нет доступа!', get_kb(log, DEFALTKB))
        return
        
    mid = msg.message_id

    if not adata['0'][3]:
        if (stat := db.update('ask_tb', f"cid=array[{cid}], res='{jsonb}', stat=TRUE", f"where id={adata['0'][0]}").status) != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, 'Ошибка сохранения. К опросу нет доступа!', get_kb(log, DEFALTKB))
            return
    else:
        req = 'array['
        for i in adata['0'][3]['Elements']:
            req = f"{req}{i}, "
        req = f'{req}{cid}]'
        log.debug(req)
        if (stat := db.update('ask_tb', f"cid={req}", f"where id={adata['0'][0]}").status) != 'ok':
            log.error(stat)
            send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
            return
    results[mid] = Result(mid)
    log.debug(results)
        
RES_T=", 'Результаты'"

def create_ask(log, bot: TeleBot, tid: str|int) -> None:
    def _loop_create(msg: Message, title: str, isPub: bool, asks: List[str], hasAccessToShow: bool, deadline: str|datetime, photo: bytes) -> None:
        log.debug(f'txt:{msg.text} title:{title} asks:{asks} isPub:{isPub}')
        if msg.text == 'Назад':
            send_msg(log, bot, tid, 'Отмена создания опроса', get_kb(log, DEFALTKB))
            return
        if msg.text == 'Завершить':
            send_msg(log, bot, tid, 'Опрос создан', get_kb(log, DEFALTKB))
            req = f"('{title}', {'TRUE' if isPub else 'FALSE'}, array["
            for i in asks:
                req = f"{req}'{i}',"
            req = f"""{req[:-1]}{RES_T if hasAccessToShow else ''}], 
                {hasAccessToShow}, 
                {True if deadline else False},
                to_timestamp('{deadline if deadline else '20.12.2023/12:00'}', 'DD.MM.YYYY/HH24:MI'),
                '\\x{photo.hex()}'
            )"""
            
            log.info(f"insert:'{req[:100]}'")
            if (stat := db.insert('ask_tb', 'head, is_pub, sub, access_to_show, has_deadline, deadline, photo', req).status) != 'ok':
                log.error(stat)
                send_msg(log, bot, tid, DBERR, rmvKb())
                return
            send(log, bot, tid)
            return

        asks.append(msg.text)
        wait_msg(log, bot, tid, _loop_create, 'Введите вариант ответа', 
                 get_kb(log, ['Назад', 'Завершить']), [title, isPub, asks, hasAccessToShow, deadline, photo])

    def _create(msg: Message, isPub: bool, hasAccessToShow: bool, deadline: str|datetime, photo: bytes) -> None:
        log.debug(msg.text)
        if msg.text == 'Назад':
            send_msg(log, bot, tid, 'Отмена создания опроса', get_kb(log, DEFALTKB))
            return
        
        wait_msg(log, bot, tid, _loop_create, 'Введите вариант ответа', 
                 get_kb(log, ['Назад']), [msg.text, isPub, [], hasAccessToShow, deadline, photo])

    def _image(msg: Message, isPub: bool, hasAccessToShow: bool, deadline) -> None:
        log.debug(f"deadline:'{deadline}' isPub:{isPub} hasAccessToShow:{hasAccessToShow}")
        if msg.text == 'Назад':
            send_msg(log, bot, tid, 'Отмена создания опроса', get_kb(log, DEFALTKB))
            return
        try:
            file_info = bot.get_file(msg.photo[-1].file_id)
            photo = bot.download_file(file_info.file_path)
            log.debug("Got photo")
            wait_msg(log, bot, tid, _create, 'Введите вопрос', 
                     get_kb(log, ['Назад']), [isPub, hasAccessToShow, deadline, photo])
        except Exception as err:
            log.error(err)
            wait_msg(log, bot, tid, _image, 'Ошибка загрузки изображения. Отправьте логотип/картинку для опроса ещё раз', 
                     get_kb(log, ['Назад']), [isPub, hasAccessToShow, deadline])

    def _set_time(msg: Message, isPub: bool, hasAccessToShow: bool) -> None:
        log.debug(f"time:'{msg.text}' isPub:{isPub} hasAccessToShow:{hasAccessToShow}")
        if msg.text == 'Назад':
            send_msg(log, bot, tid, 'Отмена создания опроса', get_kb(log, DEFALTKB))
            return
        try:
            deadline = datetime.strptime(msg.text, '%d.%m.%Y/%H:%M')
            log.debug(deadline.isoformat())
            wait_msg(log, bot, tid, _image, 'Отправьте логотип/картинку для опроса', 
                     get_kb(log, ['Назад']), [isPub, hasAccessToShow, msg.text])
        except Exception as err:
            log.error(err)
            wait_msg(log, bot, tid, _set_time, 'Не верный введенный формат',
                     get_kb(log, ['Назад']), [isPub, hasAccessToShow])

    def _time(msg: Message, isPub: bool, hasAccessToShow: bool) -> None:
        if msg.text == 'Да':
            wait_msg(log, bot, tid, _set_time, 'укажите дату окончания опроса в формате (20.12.2023/12:00)',
                     get_kb(log, ['Назад']), [isPub, hasAccessToShow])
        else:
            wait_msg(log, bot, tid, _image, 'Отправьте логотип/картинку для опроса', 
                     get_kb(log, ['Назад']), [isPub, hasAccessToShow, ''])
            
    def _type(msg: Message) -> None:
        if msg.text in ('Публичный', 'Анонимный', 'Без результата'):
            wait_msg(log, bot, tid, _time, 'Добавить время существования опроса?', 
                get_kb(log, ['Да', 'Нет']), 
                [
                    True if msg.text == 'Публичный' else False,
                    False if msg.text == 'Без результата' else True,
                ])
        else:
            send_msg(log, bot, tid, 'Неправильный тип опроса. Отмена.', get_kb(log, DEFALTKB))

    wait_msg(log, bot, tid, _type, 'Какой тип опроса?', get_kb(log, ASKTYPEKB), [])

def send(log, bot: TeleBot, tid: str|int) -> None:
    data, stat = db.get('*', 'ask_tb', '')
    if stat != 'ok':
        log.error(f'stat:{stat} data:{data}')
        send_msg(log, bot, tid, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        send_msg(log, bot, tid, 'Нет опросов для отправки. Переходим к созданию.', get_kb(log, ['Назад']))
        create_ask(log, bot, tid)
        return
    
    send_msg(log, bot, tid, f'Всего опросов: {len(data)}', rmvKb())
    asks = formatListedAsk(data)
    for key, ask in zip(data.keys(), asks):
        send_msg(log, bot, tid, ask, get_ikb(log, {'Отправить': f'{SENDFLAG}{data[key][0]}'}))
    
    send_msg(log, bot, tid, f'Какой отправить?', get_kb(log, ['Создать новый опрос', 'Назад']))
    
def redirect(log, bot: TeleBot, tid: str|int, dev: str|int, aid: str, cid: str|int, name, api_id, api_hash, photo) -> None:
    
    async def _getEntity(link):
        try:
            log.info(f'Start cli as [{bot.token}]')
            log.info("Get client")
            client = TelegramClient(name, api_id, api_hash)
            await client.start(bot_token=bot.token)
            chat = await client.get_entity(link)
            await client.disconnect()
            return chat
        except Exception as err:
            log.error(err)
        return None
    
    def _redirect(msg: Message, log, bot: TeleBot, tid: str|int, cid: str, data: str) -> None:
        txt = msg.text
        log.info(f'Redirecting by tid:{tid} with data:{data} link:{txt} to cid:{cid}')
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

        push(log, bot, tid, chat.id, data, photo, chat)


    data, stat = db.get('*', 'ask_tb', f'where id={aid}')
    if stat != 'ok':
        log.error(f'stat:{stat} data:{data}')
        send_msg(log, bot, dev, DBERR, get_kb(log, DEFALTKB))
        return
    if not len(data):
        log.info(f'data len:0')
        send_msg(log, bot, tid, 'Ошибка получения опроса.', rmvKb())
        return

    wait_msg(log, bot, tid, _redirect, 'Введите ссылку на канал/чат.', rmvKb(), [log, bot, tid, cid, data])



def format_listed_res(ask) -> List[str]:
    """  
        id serial primary key,
        head text, 
        sub varchar(64)[], 
        cid integer[],
        res jsonb,
        stat boolean,
        add_date timestamp not null default now()
    """
    max_votes = 0; max_votes_ask = '?'; sum_votes = 0
    res = ''
    if ask[4]:
        for k, r in ask[4].items():
            if k == 'Результаты':
                continue
            sum_votes += r[0]
            if r[0] > max_votes:
                max_votes = r[0]
                max_votes_ask = k
            res = f"""{res}
    Ответ:{k} 
    Всего голосов:{r[0]}
    {'' if not ask[6] else 'Проголосовали:'+str(r[2])}

            """
        res = f"""{res}Всего голосов: {sum_votes}
Больше всего голосов: {max_votes_ask} -> {max_votes}
В процентах: {0 if not sum_votes else max_votes/sum_votes * 100}%
        """
    return res if res else 'Нет результатов'

def formatListedAsk(data) -> List[str]:
    """  
        id serial primary key,
        head text, 
        sub varchar(64)[], 
        cid integer[],
        res jsonb,
        stat boolean,
        add_date timestamp not null default now()
    """
    asks = []
    for ind, ask in data.items():
        max_votes = 0; max_votes_ask = '?'; sum_votes = 0
        res = ''
        if ask[4]:
            for k, r in ask[4].items():
                sum_votes += r[0]
                if r[0] > max_votes:
                    max_votes = r[0]
                    max_votes_ask = k
                res = f"""{res}
                Ответ:{k} 
                    Всего голосов:{r[0]}
                    Проголосовали:{r[2]}

                """
            res = f"""{res}
            Всего голосов: {sum_votes}
            Больше всего голосов: {max_votes_ask} -> {max_votes}
            В процентах: {0 if not sum_votes else max_votes/sum_votes * 100}%
            """
        asks.append(f"""
    {int(ind)+1})
        \tId таблицы:{ask[0]}
        \tВопрос:{ask[1]}
        \tОтветы:{ask[2]['Elements']}
        \tГруппы:{ask[3] if not ask[3] else ask[3]['Elements']}
        \tРезультат:{res}
        \tСтатус:{ask[5]}
        \tПубличный:{'Да' if ask[6] else 'Нет'}
        \tМожно посмотреть результаты:{'Да' if ask[7] else 'Нет'}
        \tЕсть дедлайн опроса:{'Да' if ask[8] else 'Нет'}
        \tДата дедлайна:{ask[9]}\n
        \tРhoto:-\n
        \tДата добавления:{ask[11]}\n
        """)
    return asks

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
    max_votes = 0; max_votes_ask = ''; sum_votes = 0

    for ind, ask in data.items():
        res = ''
        if ask[4]:
            for k, r in ask[4].items():
                sum_votes += r[0]
                if r[0] > max_votes:
                    max_votes = r[0]
                    max_votes_ask = k
                res = f"""{res}
                Ответ:{k} Количество голосований:{r[0]}
                    Проголосовали:{r[1]}

                """
            res = f"""{res}
            Всего голосов: {sum_votes}
            Больше всего голосов: {max_votes} у {max_votes_ask}
            В процентах: {max_votes/sum_votes * 100}
            """
        asks = f"""{asks}
    {int(ind)+1})
        \tId таблицы:{ask[0]}
        \tВопрос:{ask[1]}
        \tОтветы:{ask[2]['Elements']}
        \tГруппы:{ask[3] if not ask[3] else ask[3]['Elements']}
        \tРезультат:{res}
        \tСтатус:{ask[5]}
        \tПубличный:{'Да' if ask[6] else 'Нет'}
        \tМожно посмотреть результаты:{'Да' if ask[7] else 'Нет'}
        \tЕсть дедлайн опроса:{'Да' if ask[8] else 'Нет'}
        \tДата дедлайна:{ask[9]}\n
        \tРhoto:-\n
        \tДата добавления:{ask[11]}\n
        """
    return asks
    
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

