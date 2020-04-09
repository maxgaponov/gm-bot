import telebot

TG_TOKEN = '1107041634:AAHZuH_dDE5LEzxIB07zijuMeN6W7O4Ovhw'

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(content_types=['text'])
def send_text(message):
	bot.send_message(message.chat.id, "Test")

bot.polling()
