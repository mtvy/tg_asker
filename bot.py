from typing  import Tuple
from telebot import TeleBot

from telebot.types import (
    ReplyKeyboardRemove as rmvKb,
    CallbackQuery, 
    Message, 
)

import cases

import dotenv, os, json
import logger, traceback as tb

dotenv.load_dotenv('.env')

log = logger.newLogger(__name__, logger.DEBUG)

token = os.getenv('TOKEN')
admins = os.getenv('ADMINS')
dev = os.getenv('DEV')

photo = open(os.path.join('img', 'ask.png'), 'rb').read()

log.info(f'Token:{token}')
log.info(f'Admins:{admins}')

bot = TeleBot(token)


name = 'scanner'
api_id = 23454228
api_hash = 'dbf6fe8944ccfb1686e64fc51e12f19d'

menuFuncs = {
    'Добавить'  : cases.addBtn,
    'Удалить'   : cases.delBtn, 
    'Показать'  : cases.showBtn,
    'Отправить' : cases.sendBtnAsk,
    'Остановить': cases.stopBtn,
}

addFuncs = {
    'Опрос'    : cases.addAsk,
}

showFuncs = {
    'Опросы'     : cases.showAsk,
    'Каналы/Чаты': cases.showChat,
    'Результаты' : cases.resBtn,
}

delFuncs = {
    'Удалить опросы'   : cases.delAsk,
    'Удалить канал/чат': cases.delChat,
}

def noAccess(bot: TeleBot, tid: str | int) -> None:
    cases.send_msg(log, bot, tid, 'Нет доступа.', rmvKb())

@bot.message_handler(commands=['start'])
def start(msg: Message) -> None:
    tid = str(msg.chat.id)
    if tid in admins:
        log.info(f'Bot starting by user:{tid}.')
        cases.send_msg(log, bot, tid, 'Бот опросник.', cases.get_kb(log, cases.DEFALTKB))
        return
    log.warning(f'Bot starting by user:{tid} without access.')
    noAccess(bot, tid)


@bot.message_handler(content_types=['text'])
def menu(msg: Message) -> None:
    
    tid = str(msg.chat.id)
    txt = msg.text

    if tid in admins:
        if txt in menuFuncs.keys():
            log.info(f'func:{menuFuncs[txt]} by user:{tid}.')
            menuFuncs[txt](log, bot, tid)
        elif 'Канал/Чат' in txt:
            cases.addChat(log, bot, tid, token, name, api_id, api_hash)
        elif txt in addFuncs.keys():
            log.info(f'func:{addFuncs[txt]} by user:{tid}.')
            addFuncs[txt](log, bot, tid)
        elif txt in showFuncs.keys():
            log.info(f'func:{showFuncs[txt]} by user:{tid}.')
            showFuncs[txt](log, bot, tid)
        elif txt in delFuncs.keys():
            log.info(f'func:{delFuncs[txt]} by user:{tid}.')
            delFuncs[txt](log, bot, tid)
        elif 'Опрос ' in txt:
            txt = txt.replace('Опрос ', '')
            if not txt.isdigit():
                log.warning(f'Empty aid:{txt}')
                cases.send_msg(log, bot, tid, 'Ошибка.', cases.get_kb(log, cases.DEFALTKB))
                return
            cases.sendBtnChat(log, bot, tid, txt, photo)
        else:
            log.warning(f"Wrong txt:'{txt}'.")
            cases.send_msg(log, bot, tid, 'Функция не найдена!', cases.get_kb(log, cases.DEFALTKB))
    else:
        log.warning(f'Msg from user:{tid} without access.')
        noAccess(bot, tid)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: CallbackQuery):

    cid = call.message.chat.id
    uid = call.from_user.id
    mid = call.message.message_id
    
    data = call.data

    if cases.ASKER not in data:
        log.debug(f'Wrong format data:{data}')
        return
    
    chat_id, sub = data.split(cases.ASKER)

    log.debug(f'tid:{cid} uid:{uid} mid:{mid} data:{data} chart_id:{chat_id} sub:{sub}')

    # tid = str(cid).replace('-100', '')

    col = 'active_tb.id as actid, active_tb.cid, active_tb.aid, active_tb.mid, active_tb.res, active_tb.stat, chat_tb.tid, chat_tb.chat'
    cond = f'where active_tb.mid={mid} and active_tb.cid={chat_id} and active_tb.stat=true'
    data, stat = cases.db.get(col, 'active_tb join chat_tb on active_tb.cid = chat_tb.id', cond)
    if stat != 'ok':
        log.error(stat)
        cases.send_msg(log, bot, dev, cases.DBERR)
        return
    log.debug(data)
    if not len(data) or not len(data['0']):
        log.warning(f'Asker is not at the table. Delete:{cases.del_msg(log, bot, cid, mid)}')
        return

    jsonb = data['0'][4]
    log.debug(jsonb)
    if sub not in jsonb.keys():
        log.info(f'sub:{sub} not in jsonb:{jsonb}')
        return
    
    val = jsonb[sub]

    log.debug(val)

    if not len(val) or not isinstance(val[1], list):
        log.warning(f'Wrong val:{val}')
        return

    for i in jsonb.keys():
        if uid in jsonb[i][1]:
            log.info(f'uid:{uid} was at sub:{i} val:{jsonb[i][1]}')
            return

    val[0] += 1
    val[1].append(uid)
    if (stat := cases.db.update('active_tb', f"res['{sub}']='{json.dumps(val)}'", cond).status) != 'ok':
        log.error(stat)
        return
    log.debug(f'votes:{val[0]} at sub:{sub}')
    

if __name__ == "__main__":
    try:
        log.info('Starting...')
        bot.polling(allowed_updates="chat_member")
    except Exception as err:
        log.error(f'Get polling error.\n\n{err}\n\n{tb.format_exc()}')
