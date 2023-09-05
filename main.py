import telebot
from telebot import types

# Замените 'YOUR_BOT_TOKEN' на токен вашего Telegram бота
bot = telebot.TeleBot('6105834784:AAEYhTBRhpRFVo2oU3WW8C1VVaco5BK6YV0')

# Создаем словарь для хранения username пользователей
user_usernames = {}
user_locations = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Чтобы начать, отправьте мне список username, каждый с новой строки.")

    # Регистрируем следующее сообщение как обработчик для получения списка username
    bot.register_next_step_handler(message, get_usernames)


# Функция для получения списка username
def get_usernames(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Разбиваем полученный текст на строки и сохраняем в список
    usernames_text = message.text
    usernames_list = usernames_text.split('\n')

    # Сохраняем список username в словаре с ключом в виде user_id
    user_usernames[user_id] = usernames_list

    bot.send_message(chat_id, "Спасибо! Теперь отправьте мне свою геолокацию.")
    bot.register_next_step_handler(message, get_location)


# Функция для получения местоположения
def get_location(message):
    user_id = message.from_user.id
    usernames_list = user_usernames.get(user_id)

    if usernames_list:
        # Отправляем личные сообщения каждому username из списка
        for username in usernames_list:
            # Создаем клавиатуру с кнопкой для отправки геолокации
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            item = types.KeyboardButton("Отправить геолокацию", request_location=True)
            markup.add(item)

            # Отправляем личное сообщение с кнопкой геолокации
            bot.send_message(user_id, f"Привет, {username}! Пожалуйста, отправьте мне свою геолокацию.", reply_markup=markup)
    else:
        bot.send_message(user_id, "Пожалуйста, сначала отправьте список username с помощью команды /start.")


# Обработчик для получения местоположения
@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.from_user.id
    username = user_usernames.get(user_id)  # Получаем username из словаря

    if username:
        # Формируем строку с координатами пользователя
        location = f"{message.location.latitude}, {message.location.longitude}"

        # Записываем локацию пользователя в словарь
        user_locations[username] = location

        bot.send_message(user_id, f"Спасибо! Ваше местоположение ({location}) сохранено.")
    else:
        bot.send_message(user_id, "Пожалуйста, сначала отправьте список username с помощью команды /start.")

# Запуск бота
if __name__ == '__main__':
    bot.polling()