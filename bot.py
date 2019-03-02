from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import os, logging

commands = {'/help': 'List of available commands',
            '/start': 'Command to initiate conversation with bot'}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CATEGORY, LOCATION, TEXT = range(3)


def start(bot, update):
    update.message.reply_text('Hi, I will help you out, please, select a category:',
                              reply_markup=ReplyKeyboardMarkup(get_categories(), one_time_keyboard=True))
    return CATEGORY


def category(bot, update):
    #user = update.message.from_user
    update.message.reply_text('So category is, now please select location:',
                              reply_markup={'keyboard': get_locations(), 'resize_keyboard': True, 'one_time_keyboard': True})
    return LOCATION


def location(bot, update):
    #user = update.message.from_user
    update.message.reply_text('So location is %s, now now you can send me some notes!', update.message.text,
                              reply_markup=ReplyKeyboardRemove())
    return TEXT


def text(bot, update):
    #user = update.message.from_user
    update.message.reply_text('Thanks, I\'ll write it down!')

    return TEXT


def cancel(bot, update):
    #user = update.message.from_user
    update.message.reply_text('Hope we talk again soon!',  reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def help_command(bot, update):
    update.message.reply_text(get_commands())


def get_commands():
    string = ''
    for key in commands:
        string += key+' - '+commands[key]+'\n'
    return string


def get_categories():
    lst = [['Category1', 'Category2']]
    return lst


def get_locations():
    lst = [['Almaty', 'Astana']]
    return lst


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

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