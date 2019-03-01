from telegram.ext import (Updater, CommandHandler)
import os

commands = {'/help': 'List of available commands',
            '/start': 'Command to initiate conversation with bot'}


def start(bot, update):
    update.message.reply_text('Hello')


def help_command(bot, update):
    update.message.reply_text(get_commands())


def get_commands():
    string = ''
    for key in commands:
        string += key+' - '+commands[key]+'\n'
    return string


def main():
    TOKEN = os.environ['TELEGRAM_TOKEN']
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_command))

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://alemresearchbot.herokuapp.com/" + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()