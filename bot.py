from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import os, logging
import psycopg2, redis, datetime

commands = {'/help': 'List of available commands',
            '/start': 'Command to initiate conversation with bot'}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

r = redis.from_url(os.environ.get("REDIS_URL"))

CATEGORY, LOCATION, TEXT = range(3)


def start(bot, update):
    r.set('username', update.message.from_user.username)
    update.message.reply_text('Greetings, I will help you out with reports, first, select a category: \n'
                              'If you made something wrong type /cancel.',
                              reply_markup={'keyboard': get_categories(), 'resize_keyboard': True,
                                            'one_time_keyboard': True})
    return CATEGORY


def category(bot, update):
    r.set('category', update.message.text)
    update.message.reply_text(f'You selected \"{update.message.text}\", now please select location of your report:',
                              reply_markup={'keyboard': get_locations(), 'resize_keyboard': True,
                                            'one_time_keyboard': True})
    return LOCATION


def location(bot, update):
    r.set('location', update.message.text)
    update.message.reply_text(f'You selected {update.message.text}, now you can send your report',
                              reply_markup=ReplyKeyboardRemove())
    return TEXT


def text(bot, update):
    r.set('text', update.message.text)
    save_to_db(r.get('username'), r.get('category'), r.get('text'), r.get('location'))
    update.message.reply_text('Report saved! you may continue sending me reports or type /cancel to exit')

    return TEXT


def cancel(bot, update):
    update.message.reply_text('Hope we talk again soon! Press /start to begin',  reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

#get number() phone nummber - to db

def save_to_db(username, cat, txt, loc): #//add timestamp
    try:
        conn = psycopg2.connect(get_db_url(), sslmode='require')
        conn.set_client_encoding('UTF8')
        c = conn.cursor()
        entry = ("@"+username.decode("utf-8"), cat.decode("utf-8"), txt.decode("utf-8"), loc.decode("utf-8"), datetime.datetime.now())
        logger.info(entry)
        c.execute('INSERT INTO users(usernames, category, text, location, timestamp) VALUES (%s, %s, %s, %s, %s)', entry)
        conn.commit()
    finally:
        c.close()
        conn.close()


def help_command(bot, update):
    update.message.reply_text(get_commands())


def get_commands():
    string = ''
    for key in commands:
        string += key+' - '+commands[key]+'\n'
    return string


def get_categories():
    lst = [['Все проблемы', 'Безопасность'],
            ['Бизнес', 'Государственное управление'],
            ['ЖКХ', 'Здравоохранение'],
            ['Инфраструктура', 'Коррупция'],
           ['Трудовые отношения',
            'Судебно-правовая система'],
           ['Межэтнические и религиозные отношения',
            'Образование'],
           ['Общественный транспорт',
            'Транспорт и автомобильные дороги'],
           ['Экология', 'Другое']]
    return lst


def get_locations():
    lst = [['Республика Казахстан', 'г. Астана'],
            ['г. Алматы', 'г. Шымкент'],
           ['Акмолинская область', 'Актюбинская область'],
           ['Алматинская область',
            'Атырауская область'],
           ['Западно-Казахстанская область', 'Жамбылская область'],
            ['Карагандинская область', 'Костанайская область'],
           ['Кызылординская область',
            'Мангистауская область'],
           ['Южно-Казахстанская область', 'Павлодарская область'],
            ['Северо-Казахстанская область', 'Восточно-Казахстанская область']]
    return lst


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def get_db_url():
    return os.environ['DATABASE_URL']


def main():
    TOKEN = os.environ['TELEGRAM_TOKEN']
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CATEGORY: [MessageHandler(Filters.text, category),
                       CommandHandler('help', help_command)],
            LOCATION: [MessageHandler(Filters.text, location)],
            TEXT: [MessageHandler(Filters.text, text)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://alemresearchbot.herokuapp.com/" + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()