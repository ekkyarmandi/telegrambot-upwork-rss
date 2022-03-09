import sqlite3

global DATABASE

DATABASE = "./database/jobs.db"

def table_format(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    return ", ".join([line.strip() for line in lines])

def create_table(table_name,file_path):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cmd = f"CREATE TABLE {table_name} ({table_format(file_path)})"
    cur.execute(cmd)
    con.commit()
    con.close()
    print(f"New, {table_name} table created inside {DATABASE}")

def add_user(user):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cmd = f"INSERT or IGNORE INTO user (userid,username,fullname,join_date) VALUES (?,?,?,?)"
    cur.execute(cmd, (
        user['userid'],
        user['username'],
        user['fullname'],
        user['date']
    ))
    con.commit()
    con.close()

def update_category(userid,key,value):
    if key == "3d": key = "model_3d"
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cur.execute(f"UPDATE user SET {key}={value} WHERE userid={userid}")
        con.commit()
    except: pass
    con.close()

def query(userid):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cur.execute(f"SELECT model_3d,scraping,music,illustration,nft,python FROM user WHERE userid={userid}")
        results = cur.fetchall()
        values = {
            "model_3d": results[0][0],
            "scraping": results[0][1],
            "music": results[0][2],
            "illustration": results[0][3],
            "nft": results[0][4],
            "python": results[0][5]
        }
    except:
        values = None
    con.close()
    return values

def query_one(userid,key):
    if key == "3d": key = "model_3d"
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cur.execute(f"SELECT {key} FROM user WHERE userid={userid}")
        values = cur.fetchone()
    except:
        values = None
    con.close()
    return values[0]

def query_job():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cur.execute("SELECT title,description,link,budget,posted_on,category,skills,country FROM jobs")
        results = cur.fetchall()
        values = {
            "title": results[0][0],
            "description": results[0][1],
            "link": results[0][2],
            "budget": results[0][3],
            "posted_on": results[0][4],
            "category": results[0][5],
            "skills": results[0][6],
            "country": results[0][7]
        }
    except: values = None
    con.close()
    return values

if __name__ == "__main__":

    # test create table
    create_table('user','./database/user_table.txt')
    create_table('job','./database/job_table.txt')