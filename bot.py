import threading
import schedule
from telebot import TeleBot
from command import Command
from config import TG_TOKEN
from user import set_bot, get_user, update_rates

bot = TeleBot(TG_TOKEN)
set_bot(bot)


@bot.message_handler(commands=[Command.START, Command.HELP])
def command_handler(message):
    user = get_user(message.chat.id)
    user.help_notify()


@bot.message_handler(commands=[Command.RATES, Command.STOP_LOSS, Command.TAKE_PROFIT])
def command_handler(message):
    user = get_user(message.chat.id)
    user.command_query(message.text[1:])


@bot.message_handler(content_types=['text'])
def message_handler(message):
    user = get_user(message.chat.id)
    user.text_query(message.text)


def run_bot():
    bot.polling()


def run_schedule():
    schedule.every(1).seconds.do(update_rates)
    while True:
        schedule.run_pending()


threading.Thread(target=run_bot).start()
threading.Thread(target=run_schedule).start()
