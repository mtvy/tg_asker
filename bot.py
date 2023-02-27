from typing  import Tuple
from telebot import TeleBot

from telebot.types import (
    ReplyKeyboardRemove as rmvKb,
    CallbackQuery, 
    Message, 
)

from front import *
from setup import *

import cases

import dotenv, os
import exclog, logger, traceback as tb

dotenv.load_dotenv('.env')

log = logger.newLogger(__name__, logger.DEBUG)

token = os.getenv('TOKEN')
admins = os.getenv('ADMINS')

log.info(f'Token:{token}')
log.info(f'Admins:{admins}')

bot = TeleBot(token)

menuFuncs = {
    'Добавить'     : cases.addBtn,
    'Редактировать': ...,
    'Удалить'      : ..., 
    'Показать'     : ...,
    'Остановить'   : ...,
}

addFuncs = {
    'Канал/Чат': cases.addChat,
    'Опрос'    : cases.addAsk,
}

def noAccess(bot: TeleBot, tid: str | int) -> None:
    cases.sendMsg(log, bot, tid, 'Нет доступа.', rmvKb())

@bot.message_handler(commands=['start'])
def start(msg: Message) -> None:
    tid = str(msg.chat.id)
    if tid in admins:
        log.info(f'Bot starting by user:{tid}.')
        cases.sendMsg(log, bot, tid, 'Бот опросник.', set_kb(cases.DEFALTKB))
        return
    log.warning(f'Bot starting by user:{tid} without access.')
    noAccess(bot, tid)


@bot.message_handler(content_types=['text'])
def menu(msg : Message) -> None:
    tid = str(msg.chat.id)
    # u_id = str(msg.from_user.id)
    
    txt = msg.text

    if tid in admins:
        if txt in menuFuncs.keys():
            log.info(f'func:{menuFuncs[txt]} by user:{tid}.')
            menuFuncs[txt](log, bot, tid)
        elif txt in addFuncs.keys():
            log.info(f'func:{addFuncs[txt]} by user:{tid}.')
            addFuncs[txt](log, bot, tid)
        else:
            log.warning(f"Wrong txt:'{txt}'.")
    else:
        log.warning(f'Msg from user:{tid} without access.')
        noAccess(bot, tid)

    # if tid in admins and txt in menuFuncs.keys():
    #     menuFuncs[txt](bot, tid)
    # elif tid in users_sub.keys() and \
    #         u_id in users_sub[tid].keys() and not users_sub[tid][u_id][0]:
    #     del_msg(bot, tid, msg.message_id)

# @bot.message_handler(content_types=["new_chat_members"])
# def new_group_user(msg: Message):
#     tid = str(msg.chat.id)

    # group: Tuple = get_info(_id)

    # if group:
    #     u_id = str(msg.from_user.id)
        
    #     txt: str = group[1] 
    #     f_name: str = msg.from_user.first_name
    #     l_name: str = msg.from_user.last_name
    #     u_name: str = msg.from_user.username

    #     if '@user' in txt:
    #         txt = txt.replace('@user', f_name if f_name else l_name \
    #                 if l_name else u_name if u_name else '')
        
    #     msg = cases.sendMsg(log, bot, _id, txt, set_inline_kb({'Подтвердить' : u_id}))
    #     users_sub[_id] = {u_id : [False, msg.message_id, False]}

# @bot.callback_query_handler(func=lambda call: True)
# @exclog.logging()
# def callback_inline(call : CallbackQuery):
#     global users_sub

#     _id  = str(call.message.chat.id)
#     u_id = str(call.from_user.id)

#     if _id in users_sub.keys() and \
#             u_id in users_sub[_id].keys() and not users_sub[_id][u_id][0]:
#         users_sub[_id][u_id][0] = True
#         users_sub[_id][u_id][2] = True
#         if del_msg(bot, _id, users_sub[_id][u_id][1]):
#             users_sub[_id][u_id][1] = None


if __name__ == "__main__":
    try:
        log.info('Starting...')
        bot.polling(allowed_updates="chat_member")
    except Exception as err:
        log.error(f'Get polling error.\n\n{err}\n\n{tb.format_exc()}')
