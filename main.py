import telebot
from telebot import types
import datetime
import threading

# Замените 'YOUR_BOT_TOKEN' на токен вашего Telegram бота
TOKEN = ''

class MeetingBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.sessions = {}  # Словарь для хранения сеансов по chat_id
        self.session_timeout = 3600  # 1 час в секундах

    def start(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            chat_id = message.chat.id
            if chat_id < 0:  # Проверка, что это групповой чат
                print(f"Bot started in group chat with id: {chat_id}")
            self.bot.send_message(chat_id, "Здравствуйте, этот бот поможет выбрать вам и вашим друзьям место встречи исходя "
                                      "из выбранной вами категории и вашего местоположения. Для начала перейдите в личные "
                                      "сообщения с ботом и запустите его, далее администратор должен ввести команду '/meet' для "
                                      "начала выбора места встречи. Далее следуйте просьбам бота")

        @self.bot.message_handler(func=lambda message: message.text.lower() == '/meet')
        def meet(message):
            chat_id = message.chat.id
            if chat_id < 0:  # Проверка, что это групповой чат
                print(f"Bot initiated /meet command in group chat with id: {chat_id}")
            user_id = message.from_user.id
            chat_members = self.bot.get_chat_members_count(chat_id)
            chat_member = self.bot.get_chat_member(chat_id, user_id)

            if chat_members <= 2:
                self.bot.send_message(chat_id, "Вам нужно более двух участников для создания встречи.")
            elif chat_member.status == "administrator" or chat_member.status == "creator":
                if chat_id not in self.sessions:
                    self.sessions[chat_id] = {'organizer': user_id, 'participants': [], 'last_interaction': datetime.datetime.now()}
                self.bot.send_message(chat_id, "Организатор ввел команду /meet. Ожидаю список username.")
            else:
                self.bot.send_message(chat_id,
                                      "Доступ к команде /meet имеет только создатель/владелец")

        @self.bot.message_handler(func=lambda message: message.text.lower() == '/stop_meet')
        def stop_meet(message):
            chat_id = message.chat.id
            if chat_id in self.sessions:
                del self.sessions[chat_id]
                self.bot.send_message(chat_id, "Сеанс завершен.")

        def check_session_timeout():
            current_time = datetime.datetime.now()
            sessions_to_remove = []

            for chat_id, session in self.sessions.items():
                last_interaction = session.get('last_interaction')
                if last_interaction and (current_time - last_interaction).seconds >= self.session_timeout:
                    sessions_to_remove.append(chat_id)

            for chat_id in sessions_to_remove:
                del self.sessions[chat_id]
                print(f"Session in group chat with id {chat_id} timed out and was removed.")

        # Запускаем функцию проверки сессий через интервал времени (например, каждую минуту)
        threading.Timer(60, check_session_timeout).start()

        self.bot.polling()

    def get_session(self, chat_id):
        return self.sessions.get(chat_id)

    def add_participant(self, chat_id, user_id):
        session = self.get_session(chat_id)
        if session:
            session['participants'].append(user_id)
        session['last_interaction'] = datetime.datetime.now()  # Обновляем время последнего взаимодействия

if __name__ == '__main__':
    bot = MeetingBot(TOKEN)
    bot.start()
