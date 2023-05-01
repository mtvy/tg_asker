from telebot import TeleBot

from telebot.types import (
    ReplyKeyboardRemove as rmvKb,
    CallbackQuery, 
    Message,
)
from datetime import (
    datetime,
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
    if not msg.chat.type == "private":
        return
    tid = str(msg.chat.id)
    if tid in admins:
        log.info(f'Bot starting by user:{tid}.')
        cases.send_msg(log, bot, tid, data.FAQ, cases.get_kb(log, cases.DEFALTKB))
        return
    log.warning(f'Bot starting by user:{tid} without access.')
    noAccess(bot, tid)


@bot.message_handler(content_types=['text'])
def menu(msg: Message) -> None:

    if not msg.chat.type == "private":
        return
    
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
    unid = call.from_user.username
    mid = call.message.message_id
    
    data = call.data

    log.debug(f'tid:{cid} uid:{uid} mid:{mid} data:{data}')

    if cases.SENDFLAG in data:
        data = data.replace(cases.SENDFLAG, '')
        log.debug(data)
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
        # log.debug(data)
        if not len(data) or not len(data['0']):
            log.warning(f'Asker is not at the table. Delete:{cases.del_msg(log, bot, cid, mid)}')
            return

        now = datetime.now()

        log.debug(f"now:{now} deadline:{data['0'][8]}:{data['0'][9]}")
        if data['0'][8] and now > datetime.strptime(data['0'][9], '%Y-%m-%dT%H:%M:%SZ'):
            bot.edit_message_caption(f"Опрос закончен: {data['0'][9]}", cid, mid, reply_markup=None)
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
            if uid in jsonb[i][1] and i != 'Результаты':
                if sub != 'Результаты':
                    try:
                        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Вы уже голосовали!")
                    except Exception as err:
                        log.error(err)
                log.info(f'uid:{uid} was at sub:{i} val:{jsonb[i][1]}')
                break
        else:
            val[0] += 1
            val[1].append(uid)
            val[2].append(unid)
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
                for k, r in adata['0'][4].items():
                    if k == 'Результаты':
                        continue
                    svotes += r[0]
                    votes.append(r[0])
                log.debug(f'votes:{votes} svotes:{svotes}')
                v = 0
                for k, r in adata['0'][4].items():
                    if k == 'Результаты':
                        continue
                    log.debug(f"votes[{v}]:{votes[v]} svotes:{svotes}  %:{0 if not svotes else (votes[v]/svotes) * 100}")
                    atitle = f"""{atitle}\n\n{k}\n{emoji.emojize(":white_small_square:")} {0 if not svotes else round((votes[v]/svotes) * 100, 1)}%
                    """
                    v+=1
                
            abtns, jsonb = dict(), dict()
            for i in adata['0'][2]['Elements']:
                abtns[i] = f"{adata['0'][0]}{cases.ASKER}{i}"
                jsonb[i] = [0, []]
            
            log.debug(f'abtns:{abtns} atitle:{atitle}')
            if sub != 'Результаты':
                try:
                    bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Вы проголосовали!")
                except Exception as err:
                    log.error(err)
            if sub != 'Результаты' and adata['0'][7]:
                bot.edit_message_caption(atitle, cid, mid, reply_markup=cases.get_ikb(log, abtns))
        except Exception as err:
            log.error(err)

        if sub == 'Результаты':

            log.debug(f"results: {cases.results}")
            
            if mid not in cases.results.keys():
                log.error(f"mid:{mid} not at results")
                cases.results[mid] = cases.Result(mid)
                cases.send_msg(log, bot, cid, f"Результаты недоступны.")
                return
            
            if cases.results[mid].is_active:
                # delta_time = now - cases.results[mid].init_time
                # if delta_time > timedelta(seconds=10):
                #     log.debug(f'Delta of res time > 10s del_res:{cases.del_msg(log, bot, cid, cases.results[mid].rid)}')
                #     msg = cases.send_msg(log, bot, cid, f"Результаты опроса:\n{adata['0'][1]}\n{cases.format_listed_res(adata['0'])}")
                #     cases.results[mid].set_result(msg.message_id, True, datetime.now())
                #     log.debug(f"init new res: mid:{mid} rid:{msg.message_id}")
                #     return

                if cases.results[mid].rid is None:
                    log.error(f"mid:{mid} cases.results[mid].rid: {cases.results[mid].rid} is None")
                    cases.send_msg(log, bot, cid, f"Результаты недоступны.")
                    return
                
                try:
                    abtns, jsonb = dict(), dict()
                    for i in adata['0'][2]['Elements']:
                        abtns[i] = f"{adata['0'][0]}{cases.ASKER}{i}"
                        jsonb[i] = [0, []]
                    
                    log.debug(f'abtns:{abtns} atitle:{atitle}')
                    log.debug(f"edit_message_caption cid:{cid} res.rid:{cases.results[mid].rid}")
                    vals, subs = cases.get_vals_n_subs(log, adata['0'])
                    log.debug(f'Delta of res time > 10s del_res:{cases.del_msg(log, bot, cid, cases.results[mid].rid)}')
                    msg = cases.send_photo(log, bot, cid, f"Результаты опроса:\n{adata['0'][1]}", cases.get_base64_graph(log, "", vals, subs))
                    cases.results[mid].set_result(msg.message_id, True, datetime.now())
                    log.debug(f"init new res: mid:{mid} rid:{msg.message_id}")
                    
                    log.debug(f"Init handler: cid:{cid} rid:{msg.message_id}")
                    proc = cases.init_proc(cases.handle, [log, bot, cid, mid, msg.message_id])
                    cases.start_proc(proc)
                except Exception as err:
                    log.error(err)
                return

            vals, subs = cases.get_vals_n_subs(log, adata['0'])
            msg = cases.send_photo(log, bot, cid, f"Результаты опроса:\n{adata['0'][1]}", cases.get_base64_graph(log, "", vals, subs))
            
            cases.results[mid].set_result(msg.message_id, True, datetime.now())
            log.debug(f"init new res: mid:{mid} rid:{msg.message_id}")

            log.debug(f"Init handler: cid:{cid} rid:{msg.message_id}")
            proc = cases.init_proc(cases.handle, [log, bot, cid, mid, msg.message_id])
            cases.start_proc(proc)

        return
    

if __name__ == "__main__":
    try:
        log.info('Starting...')
        bot.polling(allowed_updates="chat_member")
    except Exception as err:
        log.error(f'Get polling error.\n\n{err}\n\n{tb.format_exc()}')
