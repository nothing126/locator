from meeting_bot import MeetingBot

# апи токен телеграмм
TOKEN = ''

# запуск бота
if __name__ == '__main__':
    bot = MeetingBot(TOKEN)  # создание экземпляра класса с аргументом токен
    bot.start()  # вызов функции из класса
