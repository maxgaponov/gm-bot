from rates import get_rates
import telebot
import config

bot = telebot.TeleBot(config.TG_TOKEN)

def get_rate_message():
	message = '  '.join(['{} {:.2f}'.format(name, rate) for (name, rate) in get_rates().items()])
	return message

@bot.message_handler(commands=['rates'])
def send_rates(message):
	bot.send_message(message.chat.id, get_rate_message())

bot.polling()
