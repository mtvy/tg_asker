#/==================================================================\#
# utility.py                                          (c) Mtvy, 2022 #
#\==================================================================/#
#                                                                    #
# Copyright (c) 2022. Mtvy (Matvei Prudnikov, m.d.prudnik@gmail.com) #
#                                                                    #
#\==================================================================/#

#/-----------------------/ installed libs  \------------------------\#
from datetime      import datetime
from typing        import Callable, Dict, List, Tuple
from telebot       import TeleBot
from telebot.types import Message, KeyboardButton as KbButton, \
                          ReplyKeyboardRemove  as rmvKb    , \
                          ReplyKeyboardMarkup  as replyKb   , \
                          InlineKeyboardMarkup as inlineKb   , \
                          InlineKeyboardButton as inlineButton
#------------------------\ project modules /-------------------------#
from back import get_db
import exclog
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def set_kb(btns : List[str]) -> replyKb:
    """
    Making keyboard
    """
    key = replyKb(resize_keyboard=True)
    key.add(*(KbButton(txt) for txt in btns))

    return key
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def set_inline_kb(btns : Dict[str, str]) -> None:
    """
    Making inline keyboard
    """
    key = inlineKb(row_width=2)
    key.add(*(inlineButton(txt, callback_data=btns[txt]) for txt in btns.keys()))

    return key
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def get_ids(tb='groups_tb') -> Tuple[int]:
    return (it[3] for it in get_db(tb))
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def get_info(_id : str, tb='groups_tb') -> Tuple[str]:
    for it in get_db(tb):
        if it[3] == _id:
            return (it[1], it[2], it[3])
    return ()
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def get_date() -> str:
    now = datetime.now()
    return f'{now.year}-{now.month}-{now.day}'
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def del_msg(bot : TeleBot, sender_id : int, _msg_id : int) -> None:
    bot.delete_message(sender_id, _msg_id); return True
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def edit_msg(bot : TeleBot, sender_id : int, _msg_id : int, txt : str, mrkp) -> None:
    bot.edit_message_text(sender_id, _msg_id, txt, reply_markup=mrkp); return True
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def wait_msg(bot : TeleBot, _id : str | int, func : Callable, txt : str, mrkp : replyKb | inlineKb | rmvKb=None, args=[], **_) -> None:
    """
    Replacement for register_next_step_handler.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ```
    #Example 1:
        __kwrgs = {
            'bot'   : bot,
            '_id'   : _id, 
            'func'  : _call_func,     #_call_func(data, info)  
            'mrkp'  : set_kb(['Hi']), 
            'txt'   : 'Hello World!,
            'args'  : [data, info],
            ...
            ...
        }
    
        wait_msg(**__kwrgs)  
    
    #Example 2: 
        wait_msg(bot, _id, _call_func, txt, set_kb(['Hi']), [data, info])
    ```
    @note Other info at __kwrgs that does not use will comment at this func
    """
    msg = bot.send_message(_id, txt, reply_markup=mrkp)
    bot.register_next_step_handler(msg, func, *args)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging()
def send_msg(bot : TeleBot, _id : str | int, txt : str, mrkp : replyKb | inlineKb | rmvKb=None, *args, **_) -> Message:
    """
    Replacement for send_message.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ```
    #Example 1:
        __kwrgs = {
            'bot'  : bot,
            '_id'  : _id, 
            'func' : _call_func,     #_call_func(data, info)  
            'mrkp' : set_kb(['Hi']), 
            'txt'  : 'Hello World!,
            'args' : [data, info]
            ...
            ...
        }
    
        send_msg(**__kwrgs)  
    
    #Example 2: 
        send_msg(bot, _id, txt, set_kb(['Hi'])

    #Example 3: 
        send_msg(bot, _id, txt)
    ```
    """
    return bot.send_message(_id, txt, reply_markup=mrkp)
#\------------------------------------------------------------------/#
