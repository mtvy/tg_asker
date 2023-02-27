from typing import (
    Callable,
    List,
)
from telebot.types import (
    ReplyKeyboardMarkup as replyKb,
    KeyboardButton as KbButton,
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
    return Message()

                      
def getKb(log, btns: List[str]) -> replyKb:
    log.debug(f'Get KeyboardButton:{btns}')
    key = replyKb(resize_keyboard=True)
    key.add(*(KbButton(txt) for txt in btns))
    return key