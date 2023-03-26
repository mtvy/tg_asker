from telebot import TeleBot

from telebot.types import (
    ReplyKeyboardRemove as rmvKb,
    CallbackQuery, 
    Message,
    ForceReply,
)

import cases, data

import dotenv, os, json, emoji
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


defaultFunc = {
    'Отправить': cases.send,
    'Создать новый опрос': cases.create_ask,
    'Опросы': cases.get_asks,
}

def noAccess(bot: TeleBot, tid: str | int) -> None:
    cases.send_msg(log, bot, tid, 'Нет доступа.', rmvKb())

@bot.message_handler(commands=['start'])
def start(msg: Message) -> None:
    tid = str(msg.chat.id)
    if tid in admins:
        log.info(f'Bot starting by user:{tid}.')
        cases.send_msg(log, bot, tid, data.FAQ, cases.get_kb(log, cases.DEFALTKB))
        return
    log.warning(f'Bot starting by user:{tid} without access.')
    noAccess(bot, tid)


@bot.message_handler(content_types=['text'])
def menu(msg: Message) -> None:
    
    tid = str(msg.chat.id)
    txt = msg.text

    if tid in admins:
        if txt in defaultFunc.keys():
            log.info(f'func:{defaultFunc[txt]} by user:{tid}.')
            defaultFunc[txt](log, bot, tid)
        elif txt == 'Назад':
            start(msg)
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

    log.debug(f'tid:{cid} uid:{uid} mid:{mid} data:{data}')

    if cases.SENDFLAG in data:
        data = data.replace(cases.SENDFLAG, '')
        cases.redirect(log, bot, uid, dev, data, cid, name, api_id, api_hash, photo)
        return
    
    if cases.DELFLAG in data:
        aid = data.replace(cases.DELFLAG, '')
        if (stat := cases.db.delete('ask_tb', f'where id={aid}').status) != 'ok':
            log.error(stat)
            cases.send_msg(log, bot, uid, cases.DBERR, cases.get_kb(log, cases.DEFALTKB))
            return
        cases.send_msg(log, bot, uid, 'Удалено.', cases.get_kb(log, cases.DEFALTKB))
        return

    if cases.ASKER in data:        
        aid, sub = data.split(cases.ASKER)

        log.debug(f'tid:{cid} uid:{uid} mid:{mid} data:{data} chart_id:{aid} sub:{sub}')

        data, stat = cases.db.get('*', 'ask_tb', f'where id={aid}')
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
                break
        else:
            val[0] += 1
            val[1].append(uid)
            if (stat := cases.db.update('ask_tb', f"res['{sub}']='{json.dumps(val)}'", f'where id={aid}').status) != 'ok':
                log.error(stat)
                return
            log.debug(f'votes:{val[0]} at sub:{sub}')

        try:
            adata, stat = cases.db.get('*', 'ask_tb', f'where id={aid}')
            if stat != 'ok':
                log.error(f'stat:{stat} data:{data}')
                cases.send_msg(log, bot, dev, cases.DBERR, cases.get_kb(log, cases.DEFALTKB))
                return
            if not len(data):
                log.info(f'data len:0')
                cases.send_msg(log, bot, uid, 'Ошибка получения опроса.', rmvKb())
                return
            atitle = adata['0'][1]
            votes = []; svotes = 0
            if adata['0'][4]:
                for _, r in adata['0'][4].items():
                    svotes += r[0]
                    votes.append(r[0])
                log.debug(f'votes:{votes} svotes:{svotes}')
                v = 0
                for k, r in adata['0'][4].items():
                    log.debug(f"votes[{v}]:{votes[v]} svotes:{svotes}  %:{0 if not svotes else (votes[v]/svotes) * 100}")
                    atitle = f"""{atitle}\n\n{k}\n{emoji.emojize(":white_small_square:")} {0 if not svotes else (votes[v]/svotes) * 100}%
                    """
                    v+=1
                
            abtns, jsonb = dict(), dict()
            for i in adata['0'][2]['Elements']:
                abtns[i] = f"{adata['0'][0]}{cases.ASKER}{i}"
                jsonb[i] = [0, []]
            
            log.debug(f'abtns:{abtns} atitle:{atitle}')
            bot.edit_message_caption(atitle, cid, mid, reply_markup=cases.get_ikb(log, abtns))
        except Exception as err:
            log.error(err)
        return



    # if cases.ASKER not in data:
    #     log.debug(f'Wrong format data:{data}')
    #     return
    
    

if __name__ == "__main__":
    try:
        log.info('Starting...')
        bot.polling(allowed_updates="chat_member")
    except Exception as err:
        log.error(f'Get polling error.\n\n{err}\n\n{tb.format_exc()}')
