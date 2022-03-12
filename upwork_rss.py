import feedparser
import hashlib
import sqlite3
import json
import re
import os
import time
import schedule
from datetime import datetime

class UpWorkRSS:

    def reformat(self,text):
        '''
        Replace some character into readable sign.
        :param/return text: str -> target text
        '''
        signs = json.load(open("./database/signs.json"))
        while any([True if s in text else False for s in signs]):
            for key,value in signs.items():
                text = text.replace(key,value)
        return text

    def gather(self,entry,label):
        '''
        Gather job entry.
        :param entry: dict -> job feed entry
        :return job: dict -> formated dictionary as the output
        '''
        # find job title and hashing it
        job_title = entry['title'].replace("- Upwork","").strip()
        encoded_str = bytes(job_title,'utf-8')

        # assign initial value
        job = {
            "hash": hashlib.sha256(encoded_str).hexdigest(),
            "title": self.reformat(job_title),
            "link": entry['link'].strip("?source=rss"),
            "label": label,
            "budget": None,
            "skills": None
        }
        
        # find text with bold
        rm = []
        details = self.reformat(entry['content'][0]['value'])
        for b in re.finditer("(?<=\<b\>)(.*?)(?=\<\/b\>)",details):
            rm.append(b.start())
            title = details[b.start():b.end()]
            if "Posted On" not in title:
                text = details[b.start():]
                x = re.search("\<br \/\>",text)
                text = text[:x.end()].replace("<br />","")
                text = text.replace(f"{title}</b>:","").strip()
                if title == "Skills":
                    title = title.lower().replace(" ","_")
                    text = ", ".join(["#"+s.strip() for s in text.split(",")])
                    job.update({title:text})
                elif "Budget" in title or "Hourly" in title:
                    title = title.lower().replace(" ","_")
                    job.update({"budget":text})
                else:
                    title = title.lower().replace(" ","_")
                    job.update({title:text})

        # clean the description
        new_details = details[:min(rm)].replace("<b>","")
        new_details = new_details.replace("<br />","\n")
        new_details = re.sub("\n+","\n",new_details).strip()        
        job.update({"description": new_details})

        # modifying posted on date value
        job.update({"posted_on": int(time.mktime(entry['published_parsed']))+(7*3600)}) # UTC+0 to GMT+7

        # returning job
        self.job = job

    def insert(self):

        def checker(dict):
            for k,v in dict.items():
                if v == None:
                    dict[k] = "null"
            return dict

        dict = self.job
        blacklist = json.load(open("./database/blacklist-category.json"))
        con = sqlite3.connect("./database/jobs.db")
        cur = con.cursor()
        cur.execute(f"SELECT title FROM job WHERE hash = '{dict['hash']}'")
        existing = cur.fetchone()
        if dict['category'] not in blacklist and existing is None:
            dict = checker(dict)
            cmd = """INSERT or IGNORE INTO job VALUES (?,?,?,?,?,?,?,?,?,?)"""
            cur.execute(cmd, (
                dict['hash'],
                dict['title'],
                dict['description'],
                dict['link'],
                dict['budget'],
                dict['posted_on'],
                dict['category'],
                dict['skills'],
                dict['country'],
                dict['label']
            ))
            cur.execute("UPDATE job SET budget = NULL where budget = 'null'")
            cur.execute("UPDATE job SET tags = NULL where tags = 'null'")
            con.commit()
        con.close()

    def rss_url(self,query=None,title=None,ontology_skill_uid=None,category=None,country="exclude-pbsi"):
        '''
        Create Upwork RSS URL based on query, category, and country code input.
        :param query: str -> query value for specific word
        :param category: str -> filtering the job based on it's category code
        :param country: str -> filtering job based on "all" or "exclude-pbsi" keyword
        :return url: str -> combined/joined paramater as the url
        '''
        config = json.load(open("./database/config.json"))
        ref = "https://www.upwork.com/ab/feed/jobs/rss"
        if country == "all":
            location = None
        elif country == "exclude-pbsi":
            location = "%2C".join(json.load(open("./database/countries.json"))).replace(" ","+")
        config.update({
            "q": query,
            "title": title,
            "ontology_skill_uid": ontology_skill_uid,
            "subcategory2_uid": category,
            "location": location,
        })
        param = [f"{k}={v}" for k,v in config.items() if v != None]
        return ref + "?" + "&".join(param)

    def run(self):
        '''
        Run the RSS requests.
        :param sleep: int or float -> pause query for every <sleep> minute
        '''

        # printout fetching timestamp
        print(datetime.now(),'fetching UpWork RSS')

        # define the search queries
        search_job = {
            "scraping": [
                {
                    "query":"scraping",
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":"extracting",
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"scrapy",
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":"1031626778132070400"
                },
                {
                    "query":None,
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":"1225465931507142656"
                },
                {
                    "query":None,
                    "title":None,
                    "category":"531770282589057028%2C531770282589057038%2C531770282593251331",
                    "ontology_skill_uid":None
                }
            ],
            "python": [
                {
                    "query":"python",
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"python",
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"python",
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"python",
                    "category":"531770282589057028%2C531770282589057025%2C531770282589057027",
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":"996364628025274386"
                }
            ],
            "nft": [
                {
                    "query":"nft",
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"nft",
                    "category":None,
                    "ontology_skill_uid":None
                }
            ],
            "illustration": [
                {
                    "query":"illustration",
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"2d",
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":"1052162208852398098"
                },
                {
                    "query":None,
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":"1052162208864981006"
                },
                {
                    "query":None,
                    "title":None,
                    "category":"531770282593251334%2C531770282593251335%2C1356688560628174848",
                    "ontology_skill_uid":None
                }
            ],
            "music": [
                {
                    "query":"music",
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":None,
                    "category":"531770282593251341",
                    "ontology_skill_uid":None
                }
            ],
            "3d": [
                {
                    "query":"3d",
                    "title":None,
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"3d",
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"modeling",
                    "category":None,
                    "ontology_skill_uid":None
                },
                {
                    "query":None,
                    "title":"modeling",
                    "category":None,
                    "ontology_skill_uid":"1052162208781094919"
                },
                {
                    "query":None,
                    "title":"modeling",
                    "category":None,
                    "ontology_skill_uid":"1031626781625925632"
                },
                {
                    "query":None,
                    "title":None,
                    "category":"531770282601639948%2C531770282601639953%2C1356688560628174848",
                    "ontology_skill_uid":None
                }
            ]
        }
        
        # gather existings jobs via RSS
        for label in search_job:
            for search in search_job[label]:
                
                url = self.rss_url(
                    query=search['query'],
                    title=search['title'],
                    ontology_skill_uid=search['ontology_skill_uid'],
                    category=search['category']
                )

                # parse the rss url
                results = feedparser.parse(url)

                # insert new job data into database
                for entry in results['entries']:
                    self.gather(entry,label)
                    self.insert()

if __name__ == "__main__":

    # define the upwork rss object
    fetch_time = 1
    rss = UpWorkRSS()
    rss.run()
    
    # assign a job into scheduler
    schedule.every(fetch_time).minutes.do(rss.run)
    
    # program start timestamp
    print(datetime.now(),'program starting..')

    # run the schedule
    while True:
        schedule.run_pending()
        time.sleep(1)