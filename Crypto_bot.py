from config import TOKEN
from telebot import types
from Exeptions import CryptoConverter, ConvertionException
import telebot
from config import keys
import cryptocompare


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("/values")
    button2 = types.KeyboardButton("/price")
    button3 = types.KeyboardButton("/help")
    markup.add(button1, button2, button3)
    text = f'Привет, {message.chat.username}!' \
           ' Меня зовут CryptoBot. \nЯ могу отслеживать актуальный курс и делать перевод любых доступных валют.' \
           '\nЧтобы узнать доступные валюты, введите /values . ' \
           '\nЧтобы узнать актуальный курс валют в долларах, введите /price .' \
           '\nЧтобы сделать перевод валют, введите /комманду в следующем формате: \n <Имя валюты для перевода> ' \
           '<В какую валюту перевести> <Количество валюты для перевода>' \
           '\nЕсли возникли вопросы по работе бота, введите /help '
    bot.reply_to(message, text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_command(message: telebot.types.Message):
    text = f'Для перевода валют, рекомендую ознакомиться с доступными валютами по команде /values .' \
           f'\nВводите названия валюты на русском языке в формате:' \
           f'\n<имя валюты, цену которой хотите узнать> \n<имя валюты, в которой нужно узнать цену первой валюты> ' \
           f'\n<количество первой валюты> ' \
           f'\nНапример: ' \
           f'\nдоллар биткоин 350' \
           f'\nТеперь все получится,  {message.chat.username}!'

    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values_command(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key.capitalize(), ))
    bot.reply_to(message, text)

@bot.message_handler(commands=['price'])
def price_command(message: telebot.types.Message):
    for i in keys.values():
        if i != 'USD':
            all_price = cryptocompare.get_price(i, currency='USD', full=True).get('RAW').get(i).get('USD').get('PRICE')
            text = f'1 {i} : {all_price} USD'
            bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        values = message.text.lower().split(' ')

        if len(values) != 3:
            raise ConvertionException('Слишком много параметров')

        quote, base, amount = values
        total_base = CryptoConverter.convert(quote, base, amount)
    except ConvertionException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду \n{e}')
    else:
        result = total_base * float(amount)
        text = f'Цена {amount} {keys[quote]} = {result} {keys[base]}'
        bot.send_message(message.chat.id, text)


bot.polling()