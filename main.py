import datetime
import threading
from telebot import types
import telebot
from telebot.apihelper import ApiTelegramException

# Замените 'YOUR_BOT_TOKEN' на токен вашего Telegram бота
TOKEN = '6105834784:AAEYhTBRhpRFVo2oU3WW8C1VVaco5BK6YV0'


class MeetingBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.sessions = {}  # Словарь для хранения сеансов по chat_id
        self.session_timeout = 3600  # 1 час в секундах
        self.locationOfUser = {}  # Словарь для хранения местоположения пользователей

    def start(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id
            self.bot.send_message(chat_id, "Здравствуйте, этот бот поможет выбрать вам и вашим друзьям место встречи "
                                           "исходя "
                                           "из выбранной вами категории и вашего местоположения. Для начала перейдите в"
                                           "личные "
                                           "сообщения с ботом и запустите его, далее администратор должен ввести "
                                           "команду(важно это сделать)"
                                           "'/meet' для "
                                           "начала выбора места встречи. Далее следуйте просьбам бота")

        # функция для инициализации команды для начала сеанса
        @self.bot.message_handler(func=lambda message: message.text.lower() == '/meet')
        def meet(message):
            chat_id = message.chat.id
            if chat_id < 0:  # Проверка, что это групповой чат
                print(f"Bot initiated /meet command in group chat with id: {chat_id}")

            user_id = message.from_user.id
            chat_members = self.bot.get_chat_members_count(chat_id)
            chat_member = self.bot.get_chat_member(chat_id, user_id)

            # проверка на нужное кол-во участников и на права инициатора встречи
            if chat_members <= 2:
                self.bot.send_message(chat_id, "Вам нужно более двух участников для создания встречи.")
            elif chat_member.status == "administrator" or chat_member.status == "creator":

                if chat_id not in self.sessions:
                    self.sessions[chat_id] = {'organizer': user_id,
                                              'participants': [],
                                              'last_interaction': datetime.datetime.now()
                                              }
                    print(f"Bot started in group chat with id: {chat_id}")

                # Создаем клавиатуру с кнопкой "Подтвердить"
                markup = types.InlineKeyboardMarkup()
                confirm_button = types.InlineKeyboardButton("Подтвердить", callback_data="confirm_meet")
                markup.add(confirm_button)

                self.sessions[chat_id]['button_interactions'] = {}



                # Отправляем сообщение с кнопкой
                self.bot.send_message(chat_id, "Организатор ввел команду /meet. Ожидаю ваше подтверждение.",
                                      reply_markup=markup)
            else:
                self.bot.send_message(chat_id, "Доступ к команде /meet имеет только создатель/владелец")

        @self.bot.callback_query_handler(func=lambda call: call.data == "confirm_meet")
        def confirm_meet_callback(call):
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            username = call.message.from_user.username

            try:
                # Записываем информацию о взаимодействии пользователя с кнопкой
                if chat_id in self.sessions:
                    self.sessions[chat_id]['button_interactions'][user_id] = True
                self.bot.answer_callback_query(call.id)  # Ответ на нажатие кнопки

                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                send_location_button = types.KeyboardButton("Отправить геолокацию", request_location=True)
                markup.add(send_location_button)

                self.bot.send_message(user_id, "Пожалуйста, отправьте свою геолокацию.", reply_markup=markup)

            except ApiTelegramException as e:

                if e.error_code == 403:
                    self.bot.send_message(chat_id, f"{username} пожалуйста, активируйте бота, начав диалог в "
                                                   f"личных сообщениях с ним.")

        @self.bot.message_handler(content_types=['location'])
        def location(message):
            lat = message.location.latitude
            long = message.location.longitude
            loc = f"{lat},{long}"
            user_id = message.from_user.id

            # Обновляем информацию о местоположении пользователя в словаре locationOfUser
            self.locationOfUser[user_id] = loc
            print(self.locationOfUser)

        # функция для инициализации команды для завершения сеанса
        @self.bot.message_handler(func=lambda message: message.text.lower() == '/stop_meet')
        def stop_meet(message):
            chat_id = message.chat.id
            if chat_id in self.sessions:
                del self.sessions[chat_id]
                self.bot.send_message(chat_id, "Сеанс завершен.")

        # проверка активных сессий и закрытие ненужных для оптимизации
        def check_session_timeout():
            current_time = datetime.datetime.now()
            sessions_to_remove = []

            for chat_id, session in self.sessions.items():
                last_interaction = session.get('last_interaction')
                if last_interaction and (current_time - last_interaction).seconds >= self.session_timeout:
                    sessions_to_remove.append(chat_id)
            # удаление сессии добавленные в список ненужных
            for chat_id in sessions_to_remove:
                del self.sessions[chat_id]
                print(f"Session in group chat with id {chat_id} timed out and was removed.")

        # Запускаем функцию проверки сессий через интервал времени (например, каждую минуту)
        threading.Timer(60, check_session_timeout).start()

        self.bot.polling()

    # получение текущей сессии
    def get_session(self, chat_id):
        return self.sessions.get(chat_id)

    def add_participant(self, chat_id, user_id):
        session = self.get_session(chat_id)
        if session:
            session['participants'].append(user_id)
        session['last_interaction'] = datetime.datetime.now()  # Обновляем время последнего взаимодействия


# запуск бота
if __name__ == '__main__':
    bot = MeetingBot(TOKEN)
    bot.start()
