from typing import (
    Callable,
    List,
    Dict,
)
from telebot.types import (
    InlineKeyboardMarkup as inlineKb,
    InlineKeyboardButton as inlineButton,
    ReplyKeyboardMarkup  as replyKb,
    KeyboardButton       as KbButton,
    Message,
)
from telebot import TeleBot

def waitMsg(log, bot: TeleBot, tid: str|int, func: Callable, txt: str, mrkp=None, args=[]) -> None:
    """
    Replacement for register_next_step_handler.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ```
    #Example 1:
        __kwrgs = {
            'bot'   : bot,
            'tid'   : tid, 
            'func'  : _call_func,     #_call_func(data, info)  
            'mrkp'  : set_kb(['Hi']), 
            'txt'   : 'Hello World!,
            'args'  : [data, info],
            ...
            ...
        }
        wait_msg(**__kwrgs)  

    #Example 2: 
        wait_msg(bot, tid, _call_func, txt, set_kb(['Hi']), [data, info])
    ```
    @note Other info at __kwrgs that does not use will comment at this func
    """
    try:
        log.debug(f"Msg:'{txt}' Dest:{tid}")
        msg = bot.send_message(tid, txt, reply_markup=mrkp)
        bot.register_next_step_handler(msg, func, *args)
    except Exception as err:
        log.error(f'{err}')


def sendMsg(log, bot: TeleBot, tid: str|int, txt: str, mrkp=None) -> Message:
    """
    Replacement for send_message.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ```
    #Example 1:
        __kwrgs = {
            'bot'  : bot,
            'tid'  : tid, 
            'func' : _call_func,     #_call_func(data, info)  
            'mrkp' : set_kb(['Hi']), 
            'txt'  : 'Hello World!,
            'args' : [data, info]
            ...
            ...
        }
    
        send_msg(**__kwrgs)  
    
    #Example 2: 
        send_msg(bot, tid, txt, set_kb(['Hi'])

    #Example 3: 
        send_msg(bot, tid, txt)
    ```
    """
    try:
        log.debug(f"Msg:'{txt}' Dest:{tid}")
        return bot.send_message(tid, txt, reply_markup=mrkp)
    except Exception as err:
        log.error(f'{err}')
    return None

def delMsg(log, bot: TeleBot, cid: str|int, mid: int) -> bool:
    try:
        return bot.delete_message(cid, mid)
    except Exception as err:
        log.error(f'{err}')
    return False

                      
def getKb(log, btns: List[str]) -> replyKb:
    log.debug(f'Get KeyboardButtons:{btns}')
    key = replyKb(resize_keyboard=True)
    key.add(*(KbButton(txt) for txt in btns))
    return key

def getIKb(log, btns: Dict[str, str]) -> inlineKb:
    log.debug(f'Get InlineButtons:{btns}')
    key = inlineKb(row_width=2)
    key.add(*(inlineButton(txt, callback_data=btns[txt]) for txt in btns.keys()))
    return key
