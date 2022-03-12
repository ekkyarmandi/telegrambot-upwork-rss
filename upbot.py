# import python-telegram-bot libraries
import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler

# import working scripts
from scripts.config import API
from scripts.cmd import *
from scripts.sql import *
from datetime import datetime
import time, re, os

# clear the terminal
os.system('cls')

# define global variable
global WORKING

WORKING = []

# Reset stream table from database
# reset_stream()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and context.
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
    msg = "*Command List*\n" + show_commands('./database/commands.txt')
    update.message.reply_text(msg,parse_mode=ParseMode.MARKDOWN)

def show_commands(file_path):
    with open(file_path) as f:
        msg = []
        lines = f.readlines()
        for line in lines:
            line = line.replace("_","\_")
            msg.append("/"+line.strip())
    return "\n".join(msg)

def show_status(userid):
    values = query_subscription(userid)
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

def subscribe(update: Update, context: CallbackContext) -> None:
    """Subscribe Upwork jobs feed for a specific job category"""
    userid = update.effective_user.id
    key = update.effective_message.text.strip("/")
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
    try:
        key = context.args[0]
        if key in ["3d","scraping","music","illustration","nft","python"]:
            update_category(userid,key,0)
            update.message.reply_text(
                f"You unsubscribe `{key}`. Type /status to see your subscription list.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            update.message.reply_text("You are not registered yet. Type /start for register.")
    except:
        update.message.reply_text(
            "Please add \<keyword\> on the end of /unsubscribe \<keyword\> \(i\.e\. `/unsubscribe python`\) for unsubscribe getting python job postings notification\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
def unsubscribe_all(update: Update, context: CallbackContext) -> None:
    userid = update.effective_user.id
    try: 
        for k in ["3d","scraping","music","illustration","nft","python"]:
            update_category(userid,k,0)
        update.message.reply_text(
            show_status(userid),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except:
        update.message.reply_text("You are not in the list. Type /start for register.")

def status(update: Update, context: CallbackContext) -> None:
    userid = update.effective_user.id
    update.message.reply_text(
        show_status(userid),
        parse_mode=ParseMode.MARKDOWN_V2
    )

# Define the working functions.
def send_job(update: Update, context: CallbackContext) -> None:

    # make sure user can not execute the callback/command more than once
    if "Server is Now Online" in update.message.text:
    
        # get the user_id
        user_id = update.effective_user.id
        
        if user_id not in WORKING:
            WORKING.append(user_id)

            # loop entry point
            while True:

                now = time.time()
                
                # get the user subscribtion
                profile = query_subscription(user_id)
                profile = [k for k,v in profile.items() if v]
                
                # get all the job
                jobs = query_job()

                for job in jobs:

                    # get job passing time and label
                    timeleaps = now - job['posted_on']
                    label = job['label']
                    job_hash = job['hash']
                    message_id = query_stream(user_id,job_hash)

                    # get filter the job based on subscription and time pass
                    if timeleaps <= (2*3600) and label in profile and message_id == None:
                        
                        # send the jobs
                        msg = job_posting(job)
                        msg_out = context.bot.send_message(
                            text=msg,
                            chat_id=user_id,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True
                        )
                        
                        # put some delay
                        time.sleep(1)

                        # update the sent jobs database
                        update_stream(
                            user_id=user_id,
                            hash=job_hash,
                            message_id=msg_out.message_id
                        )

                    # filter two: if the job has been sent, then update it's time by editing the message
                    elif message_id != None:
                        if timeleaps <= (2*3600):
                            msg = job_posting(job)
                        else:
                            msg = f"<a href='{job['link']}'><b>{job['title']}</b></a>\n<i>Description Archived</i>"
                            delete_job(job_hash)
                        
                        # edit the existings message
                        try:
                            context.bot.edit_message_text(
                                text=msg,
                                chat_id=user_id,
                                message_id=message_id,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=True
                            )

                            # put some delay
                            time.sleep(1)
                            
                        except: pass

                    elif timeleaps > (2*3600):
                        delete_job(job_hash)

                # wait for a minute
                time.sleep(1*60)

def job_posting(job):
    now = time.time()
    title = f"<a href='{job['link']}'>{job['title']}</a>"
    category = job['category']
    tags = job['tags']
    description = re.sub("\s+"," ",job['description']).strip()
    if len(description) > 360:
        description = description[:360].strip().strip(".") + "..."
    budget = job['budget']
    if budget == None:
        budget = "🤔 <i>Budget Unknown</i>"
    else:
        budget = f"🤑 <i>{budget}</i>"
    if tags != None:
        tags = tags.replace(" ","_")
        tags = tags.replace("&","and")
        tags = tags.replace(",_",", ")
    else:
        tags = '~'
    country = job['country']
    posted = sec2pass(now-job['posted_on'])
    msg = f"<b>{title}</b>\n---\n💼 {category}, 📍{country}\n---\n<i>{description}</i>\n---\n{budget}\n⏰ <i>{posted}</i>\n---\n{tags}"
    return msg

def main() -> None:
    """Start the bot."""
    
    # Create the Updater and pass it your bot's token.
    updater = Updater(API)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Broad cast to all users
    users = query_users()
    for user_id in users:
        msg = dispatcher.bot.send_message(
            chat_id=user_id,
            text="🚨 _Server is Now Online_",
            parse_mode=ParseMode.MARKDOWN
        )

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("find_job", send_job, run_async=True))
    dispatcher.add_handler(CommandHandler("3d", subscribe))
    dispatcher.add_handler(CommandHandler("scraping", subscribe))
    dispatcher.add_handler(CommandHandler("music", subscribe))
    dispatcher.add_handler(CommandHandler("illustration", subscribe))
    dispatcher.add_handler(CommandHandler("nft", subscribe))
    dispatcher.add_handler(CommandHandler("python", subscribe))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe_all", unsubscribe_all))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_job, run_async=True))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()