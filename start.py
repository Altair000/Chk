import telebot
import time
from cc_gen import main
from autokey import chk

TOKEN = '7698270668:AAGjt05ZFiz14-HCUBNn9xQ9JvoKAFqvJ8A'
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Usa /chk para comenzar")

# Variables para almacenar datos de entrada del usuario
bin_format = None
month = None
year = None
n = None
chat_id = None

@bot.message_handler(commands=['chk'])
def start_collecting_data(message):
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, "Por favor, ingresa el **BIN**:")
    bot.register_next_step_handler(message, get_bin)

def get_bin(message):
    global bin_format  # Usar variable global
    bin_format = message.text
    bot.reply_to(message, "Ahora ingresa el **Mes** (como un número, por ejemplo, 10):")
    bot.register_next_step_handler(message, get_month)

def get_month(message):
    global month  # Usar variable global
    try:
        month = int(message.text)
        bot.reply_to(message, "Ingresa el **Año** (por ejemplo, 2025):")
        bot.register_next_step_handler(message, get_year)
    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un mes válido. Intenta de nuevo.")
        bot.register_next_step_handler(message, get_month)

def get_year(message):
    global year  # Usar variable global
    try:
        year = int(message.text)
        bot.reply_to(message, "Ingresa la **Cantidad** de tarjetas a generar:")
        bot.register_next_step_handler(message, get_quantity)
    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un año válido. Intenta de nuevo.")
        bot.register_next_step_handler(message, get_year)

def get_quantity(message):
    global n  # Usar variable global
    try:
        n = int(message.text)

        # Llamar a la función principal con los datos recopilados
        main(bin_format, month, year, n)
        chk(chat_id, bot)
   
        # Reiniciar variables para el próximo uso
        reset_variables()
    except ValueError:
        bot.reply_to(message, "Por favor, ingresa una cantidad válida. Intenta de nuevo.")
        bot.register_next_step_handler(message, get_quantity)

def reset_variables():
    global bin_format, month, year, n
    bin_format = None
    month = None
    year = None
    n = None
    chat_id = None

if __name__ == '__main__':
    print("Bot iniciado")
    bot.polling()








