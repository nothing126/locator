from meeting_bot import MeetingBot

# апи токен телеграмм
TOKEN = '6105834784:AAEYhTBRhpRFVo2oU3WW8C1VVaco5BK6YV0'

# запуск бота
if __name__ == '__main__':
    bot = MeetingBot(TOKEN)  # создание экземпляра класса с аргументом токен
    bot.start()  # вызов функции из класса
