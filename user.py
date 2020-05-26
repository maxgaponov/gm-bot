import time
import pickle
from enum import Enum
from message import Message
from command import Command
from rates import get_rates
from config import CURRENCIES, USERS_FILE

bot = None


def set_bot(new_bot):
    global bot
    bot = new_bot


class UState(Enum):
    start = 1
    inp_cur = 2
    inp_val = 3
    inp_dur = 4
    bad_cmd = 5


def cur_handler(user, text):
    text = text.upper()
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
    except ValueError:
        user.set_state(UState.inp_val)


def dur_handler(user, text):
    try:
        dur = int(text)
        user.storage['dur'] = dur
        user.set_state(UState.start)
        user.add_action()
    except ValueError:
        user.set_state(UState.inp_dur)


trans = {
    UState.start: (None, None),
    UState.bad_cmd: (Message.BAD_CMD, None),
    UState.inp_cur: (Message.INP_CUR, cur_handler),
    UState.inp_dur: (Message.INP_DUR, dur_handler),
    UState.inp_val: (Message.INP_VAL, val_handler)
}


class User:
    def __init__(self, user_id):
        self.id = user_id
        self.low_rate = {}
        self.high_rate = {}
        self.notification_time = None
        self.state = UState.start
        self.storage = {}
        self.handler = None

    def update_rates(self, rates):
        if self.notification_time and self.notification_time <= time.time():
            self.notification_time = None
            self.notify(Message.get_rate_message(rates))
        for cur in CURRENCIES:
            rate = rates[cur]
            lr = self.low_rate.get(cur, None)
            if lr and lr >= rate:
                self.notify(Message.get_stop_loss_message(rates, cur))
                self.low_rate[cur] = None
            hr = self.high_rate.get(cur, None)
            if hr and hr <= rate:
                self.notify(Message.get_take_profit_message(rates, cur))
                self.high_rate[cur] = None

    def notify(self, message):
        if message:
            bot.send_message(self.id, message, parse_mode='markdown')

    def help_notify(self):
        self.notify(Message.HELP)

    def set_state(self, state):
        (msg, self.handler) = trans[state]
        self.notify(msg)
        if not self.handler:
            self.state = UState.start
        else:
            self.state = state

    def command_query(self, command):
        self.storage['cmd'] = command
        if command == Command.STOP_LOSS or command == Command.TAKE_PROFIT:
            self.set_state(UState.inp_cur)
        elif command == Command.RATES:
            self.set_state(UState.inp_dur)
        else:
            self.set_state(UState.bad_cmd)

    def text_query(self, text):
        if self.handler:
            self.handler(self, text)

    def add_action(self):
        cmd = self.storage['cmd']
        if cmd == Command.RATES:
            dur = self.storage['dur']
            self.notification_time = time.time() + dur
        elif cmd == Command.STOP_LOSS:
            val = self.storage['val']
            cur = self.storage['cur']
            self.low_rate[cur] = val
        elif cmd == Command.TAKE_PROFIT:
            val = self.storage['val']
            cur = self.storage['cur']
            self.high_rate[cur] = val


def load_users():
    try:
        with open(USERS_FILE, 'rb') as f:
            return pickle.load(f)
    except IOError:
        return dict()


users = load_users()


def save_users():
    global users
    with open(USERS_FILE, 'wb') as f:
        pickle.dump(users, f)


def get_user(user_id):
    if user_id not in users:
        users[user_id] = User(user_id)
    return users[user_id]


def update_rates():
    rates = get_rates()
    for (user_id, user) in users.items():
        user.update_rates(rates)
