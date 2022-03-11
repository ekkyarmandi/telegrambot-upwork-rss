# Running Telegram Bot Server and UpWork RSS Updater

# import working libraries
import schedule
import upwork_rss
import upbot
import time

# assign UpWork RSS object
rss = upwork_rss.UpWorkRSS()

# assign the job
fetch_time = 1 # minute
schedule.every(fetch_time).minutes.do(rss.run)
schedule.every().day.at("08:00").do(upbot.main)

# run the schedule
while True:
    schedule.run_pending()
    time.sleep(1)