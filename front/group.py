

import exclog

from back.database import delete_db, get_db, insert_db, update_db
from front.utility import send_msg, set_kb, wait_msg
from telebot       import TeleBot
from telebot.types import Message, ReplyKeyboardRemove  as rmvKb

from front.vars import *


@exclog.logging()
def add_group(bot : TeleBot, _id : str | int) -> None:

    @exclog.logging()
    def __get_group(gid : str | int):
        return bot.get_chat(gid).title


    @exclog.logging()
    def __get_len_mems(gid : str | int):
        return bot.get_chat_members_count(gid)


    @exclog.logging()
    def __add_group(msg : Message, bot : TeleBot, _id : str | int, gid : str) -> None:
        name = __get_group(gid)
        if (name and insert_db(f"INSERT INTO groups_tb (name, msg, tid, mems) VALUES ('{name}', '{msg.text}', '{gid}', '{__get_len_mems(gid)}')", 'groups_tb')):
            send_msg(bot, _id, f'Добавлена группа {gid} с текстом:\n{msg.text}', set_kb(BOT_KB))
        else:
            send_msg(bot, _id, f'Не добавлена группа {gid} с текстом:\n{msg.text}', set_kb(BOT_KB))


    @exclog.logging()
    def __add_msg(msg : Message, bot : TeleBot, _id : str | int) -> None:
        wait_msg(bot, _id, __add_group, ADD_GROUP_MSG, rmvKb(), [bot, _id, msg.text])


    wait_msg(bot, _id, __add_msg, ADD_GROUP, rmvKb(), [bot, _id])


@exclog.logging()
def edit_group(bot : TeleBot, _id : str | int) -> None:


    @exclog.logging()
    def __edit_group(msg : Message, bot : TeleBot, _id : str | int, name : str) -> None:
        if (update_db(f"UPDATE groups_tb SET msg='{msg.text}' WHERE tid='{name}'", 'groups_tb')):
            send_msg(bot, _id, f'Группа {name} обновлена с текстом:\n{msg.text}', set_kb(BOT_KB))
        else:
            send_msg(bot, _id, f'Не обновлена группа {name} с текстом:\n{msg.text}.', set_kb(BOT_KB))


    @exclog.logging()
    def __edit_msg(msg : Message, bot : TeleBot, _id : str | int) -> None:
        wait_msg(bot, _id, __edit_group, EDIT_GROUP_MSG, rmvKb(), [bot, _id, msg.text])

    groups_kb = [it[3] for it in get_db('groups_tb')]
    if groups_kb:
        wait_msg(bot, _id, __edit_msg, EDIT_GROUP, set_kb(groups_kb), [bot, _id])
    else:
        send_msg(bot, _id, f'Нет добавленных каналов.')


@exclog.logging()
def del_group(bot : TeleBot, _id : str | int) -> None:


    @exclog.logging()
    def __del_group(msg : Message, bot : TeleBot, _id : str | int) -> None:
        if (delete_db(f"tid='{msg.text}'", 'groups_tb')):
            send_msg(bot, _id, f'Группа {msg.text} удалена.', set_kb(BOT_KB))
        else:
            send_msg(bot, _id, f'Группа {msg.text} не удалена.', set_kb(BOT_KB))

    groups = get_db('groups_tb')
    if groups:
        groups_kb = [it[3] for it in groups]
        if groups_kb:
            wait_msg(bot, _id, __del_group, DELETE_GROUP, set_kb(groups_kb), [bot, _id])
    else:
        send_msg(bot, _id, f'Нет добавленных каналов.')


@exclog.logging()
def show_group(bot : TeleBot, _id : str | int) -> None:

    groups = {}; grps = get_db('groups_tb')
    for it in grps if grps else []:
        groups |= {it[3] : (it[2], it[1])}

    send_msg(bot, _id, f'Добавлено: {len(groups)}')

    for it in groups.keys():
        send_msg(bot, _id, f'id: {it}\nНазвание: {groups[it][1]}\nТекст: {groups[it][0]}')
