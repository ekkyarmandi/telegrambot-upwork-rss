import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from scripts.config import API
from scripts.sq import *
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    # get the user information and add it to the table
    tele_user = update.effective_user
    date = datetime.now().strftime('%a, %d %B %Y %H:%M:%S')
    user = {
        "userid": tele_user.id,
        "username": tele_user.username,
        "fullname": tele_user.full_name,
        "date": date
    }
    add_user(user)
    
    # send the list of the command
    msg = "Command List:\n" + show_commands('./database/commands.txt')
    update.message.reply_text(msg)

def show_commands(file_path):
    with open(file_path) as f:
        msg = []
        lines = f.readlines()
        for line in lines:
            msg.append("/"+line.strip())
    return "\n".join(msg)

def subscribe(update: Update, context: CallbackContext) -> None:
    """Subscribe Upwork jobs feed for a specific job category"""
    userid = update.effective_user.id
    key = update.effective_message.text.strip("/")
    if key == "3d": key = "model_3d"
    try: update_category(userid,key,1)
    except: update.message.reply_text("Kamu belum terdaftar. Tekan /start untuk mendaftar.")

def unsubscribe(update: Update, context: CallbackContext) -> None:
    pass

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("3d", subscribe))
    dispatcher.add_handler(CommandHandler("scraping", subscribe))
    dispatcher.add_handler(CommandHandler("music", subscribe))
    dispatcher.add_handler(CommandHandler("illustration", subscribe))
    dispatcher.add_handler(CommandHandler("nft", subscribe))
    dispatcher.add_handler(CommandHandler("python", subscribe))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("stop", unsubscribe))
    dispatcher.add_handler(CommandHandler("help", start))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()