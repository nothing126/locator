import telebot
from telebot import types

# Замените 'YOUR_BOT_TOKEN' на токен вашего Telegram бота
bot = telebot.TeleBot('6105834784:AAEYhTBRhpRFVo2oU3WW8C1VVaco5BK6YV0')

user_locations = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Отправляем сообщение с кнопкой для отправки геолокации
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item = types.KeyboardButton("Отправить геолокацию", request_location=True)
    markup.add(item)

    # Получаем информацию о чате
    chat_info = bot.get_chat(chat_id)

    # Получаем список участников группы
    members = bot.get_chat_members(chat_id)

    # Отправляем сообщение с кнопкой каждому участнику в группе
    for member in members:
        user_id = member.user.id
        if user_id != bot.get_me().id:
            bot.send_message(user_id, "Привет! Для начала, нажми кнопку 'Отправить геолокацию' ниже:", reply_markup=markup)

# Обработчик для получения местоположения
@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.from_user.id
    username = message.from_user.username
    location = (message.location.latitude, message.location.longitude)

    user_locations[username] = location

    bot.send_message(user_id, "Спасибо! Твое местоположение сохранено.")

# Запуск бота
bot.polling()