import time
from enum import Enum
from rates import get_rates
from telebot import TeleBot
from config import RATES_CMD, STOP_LOSS_CMD, TAKE_PROFIT_CMD, \
                   BAD_CMD_MSG, INP_CUR_MSG, INP_DUR_MSG, INP_VAL_MSG, \
                   TG_TOKEN, CURRENCIES

bot = TeleBot(TG_TOKEN)
users = {}

def get_rate_message(rates):
    message = '  '.join(['{} {:.2f}'.format(name, rate) for (name, rate) in rates.items()])
    return message

def get_stop_loss_message(rates, cur):
    message = 'Stop loss {} {:.2f}'.format(cur, rates[cur])
    return message

def get_take_profit_message(rates, cur):
    message = 'Take profit {} {:.2f}'.format(cur, rates[cur])
    return message

class UState(Enum):
    start = 1
    inp_cur = 2
    inp_val = 3
    inp_dur = 4
    bad_cmd = 5

def cur_handler(user, text):
    if text in CURRENCIES:
        user.storage['cur'] = text
        user.set_state(UState.inp_val)
    else:
        user.set_state(UState.inp_cur)

def val_handler(user, text):
    try:
        val = float(text)
        user.storage['val'] = val
        user.set_state(UState.start)
        user.add_action()
    except Exception:
        user.set_state(UState.inp_val)

def dur_handler(user, text):
    try:
        dur = int(text)
        user.storage['dur'] = dur
        user.set_state(UState.start)
        user.add_action()
    except Exception:
        user.set_state(UState.inp_val)

trans = {}
trans[UState.start] = (None, None)
trans[UState.bad_cmd] = (BAD_CMD_MSG, None)
trans[UState.inp_cur] = (INP_CUR_MSG, cur_handler)
trans[UState.inp_dur] = (INP_DUR_MSG, dur_handler)
trans[UState.inp_val] = (INP_VAL_MSG, val_handler)


class User:
    def __init__(self, id):
        self.id = id
        self.low_rate = {}
        self.high_rate = {}
        self.notif_time = None
        self.state = UState.start
        self.storage = {}
        self.handler = None

    def update_rates(self, rates):
        if self.notif_time and self.notif_time >= time.time():
            self.notif_time = None
            self.notificate(get_rate_message(rates))
        for cur in CURRENCIES:
            rate = rates[cur]
            lr = self.low_rate.get(cur, None)
            if lr and lr >= rate:
                self.notificate(get_stop_loss_message(rates, cur))
            hr = self.high_rate.get(cur, None)
            if hr and hr <= rate:
                self.notificate(get_take_profit_message(rates, cur))

    def notificate(self, message):
        if message:
            bot.send_message(self.id, message)

    def set_state(self, state):
        (msg, self.handler) = trans[self.state]
        self.notificate(msg)
        if not self.handler:
            self.state = UState.start

    def query(self, text):
        if text[0] == '/':
            self.command_query(text[1:])
        else:
            self.text_query(text)

    def command_query(self, command):
        self.storage['cmd'] = command
        if command == STOP_LOSS_CMD or command == TAKE_PROFIT_CMD:
            self.set_state(UState.inp_cur)
        elif command == RATES_CMD:
            self.set_state(UState.inp_dur)
        else:
            self.set_state(UState.bad_cmd)

    def text_query(self, text):
        if self.handler:
            self.handler(self, text)

    def add_action(self):
        cmd = self.storage['cmd']
        if cmd == RATES_CMD:
            dur = self.storage['dur']
            self.notif_time = time.time() + dur
        elif cmd == STOP_LOSS_CMD:
            val = self.storage['val']
            cur = self.storage['cur']
            self.low_rate[cur] = val
        elif cmd == TAKE_PROFIT_CMD:
            val = self.storage['val']
            cur = self.storage['cur']
            self.high_rate[cur] = val

def get_user(id):
    return users.get(id, User(id))

@bot.message_handler(content_types=['text'], commands = [RATES_CMD, STOP_LOSS_CMD, TAKE_PROFIT_CMD])
def message_handler(message):
    user = get_user(message.chat.id)
    user.query(message.text)

bot.polling()
