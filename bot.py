from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import os, logging
import psycopg2, redis

commands = {'/help': 'List of available commands',
            '/start': 'Command to initiate conversation with bot'}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

r = redis.from_url(os.environ.get("REDIS_URL"))

CATEGORY, LOCATION, TEXT = range(3)


def start(bot, update):
    r.set('username', update.message.from_user.first_name)
    update.message.reply_text('Hi, I will help you out, please, select a category:',
                              reply_markup={'keyboard': get_categories(), 'resize_keyboard': True,
                                            'one_time_keyboard': True})
    return CATEGORY


def category(bot, update):
    r.set('category', update.message.text)
    update.message.reply_text(f'So category is {update.message.text}, now please select location:',
                              reply_markup={'keyboard': get_locations(), 'resize_keyboard': True,
                                            'one_time_keyboard': True})
    return LOCATION


def location(bot, update):
    r.set('location', update.message.text)
    update.message.reply_text(f'So location is {update.message.text}, now you can send me some notes!',
                              reply_markup=ReplyKeyboardRemove())
    return TEXT


def text(bot, update):
    r.set('text', update.message.text)
    save_to_db(r.get('username'), r.get('category'), r.get('text'), r.get('location'))
    update.message.reply_text('Thanks, I\'ll write it down!')

    return TEXT


def cancel(bot, update):
    update.message.reply_text('Hope we talk again soon!',  reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def save_to_db(username, cat, txt, loc):
    try:
        conn = psycopg2.connect(get_db_url(), sslmode='require')
        c = conn.cursor()
        entry = (username, cat, txt, loc)
        logger.info(entry)
        c.execute('INSERT INTO users(usernames, category, text, location) VALUES (%s, %s, %s, %s)', entry)
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
    lst = [['Category 1', 'Category 2', 'Category 3', 'Category 4']]
    return lst


def get_locations():
    lst = [['Almaty', 'Astana', 'Shymkent', 'Taldykorgan']]
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