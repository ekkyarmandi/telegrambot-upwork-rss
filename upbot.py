import logging

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from scripts.config import API
from scripts.sq import *
from datetime import datetime
import time

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
    msg = "*Command List*\n\n" + show_commands('./database/commands.txt')
    update.message.reply_text(msg,parse_mode=ParseMode.MARKDOWN_V2)

def show_commands(file_path):
    with open(file_path) as f:
        msg = []
        lines = f.readlines()
        for line in lines:
            line = line.replace("<","\<")
            line = line.replace(">","\>")
            line = line.replace("-","\-")
            msg.append("/"+line)
    return "\n".join(msg)

def subscribe(update: Update, context: CallbackContext) -> None:
    """Subscribe Upwork jobs feed for a specific job category"""
    userid = update.effective_user.id
    key = update.effective_message.text.strip("/")
    
    if key == "3d":
        key = "model_3d"

    status = query_one(userid,key)
    if status:
        update.message.reply_text(
            f"You have been subscribed to `{key}` job postings\. Type /status to see your subscription list\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        try:
            update_category(userid,key,1)
            update.message.reply_text(
                    f"You are now subscribed to `{key}` job postings\.",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        except:
            update.message.reply_text("You are not registered yet. Type /start for register.")

def unsubscribe(update: Update, context: CallbackContext) -> None:
    userid = update.effective_user.id
    key = update.effective_message.text.split()[-1]
    if key == "all":
        try: 
            for k in ["model_3d","scraping","music","illustration","nft","python"]:
                update_category(userid,k,0)
            text = show_status(userid)
            update.message.reply_text(text,parse_mode=ParseMode.MARKDOWN_V2)
        except:
            update.message.reply_text("You are not in the list. Type /start for register.")
    elif key == "3d":
        key = "model_3d"
        try:
            update_category(userid,key,0)
            text = show_status(userid)
            update.message.reply_text(text,parse_mode=ParseMode.MARKDOWN_V2)
        except: update.message.reply_text("You are not in the list. Type /start for register.")
    elif key in ["scraping","music","illustration","nft","python"]:
        try:
            update_category(userid,key,0)
            text = show_status(userid)
            update.message.reply_text(text,parse_mode=ParseMode.MARKDOWN_V2)
        except: update.message.reply_text("You are not registered yet. Type /start for register.")
    else:
        update.message.reply_text(
            "Please add \<keyword\> on the end of it \(i\.e\. `/unsubscribe all`\) for unsubscribe everything",
            parse_mode=ParseMode.MARKDOWN_V2
        )

def status(update: Update, context: CallbackContext) -> None:
    userid = update.effective_user.id
    text = show_status(userid)
    update.message.reply_text(text,parse_mode=ParseMode.MARKDOWN_V2)

def show_status(userid):
    values = query(userid)
    try:
        text = "*Subscription List*\n"
        l = max([len(k) for k in values.keys()])
        for k,v in values.items():
            if k == "model_3d":
                k = "3d"
            if v == 1:
                v = "Subscribed"
            else:
                v = "Not Subscribe"
            s = l - len(k)
            s = " "*s
            text += f'• `{k+s}: {v}`\n'
        return text
    except:
        return "You are not registered yet. Type /start for register."

def test(update: Update, context: CallbackContext):
    i = 0
    while True:
        i += 1
        update.message.reply_text(i)
        time.sleep(1)

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
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("test", test))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()