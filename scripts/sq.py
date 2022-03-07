import sqlite3

global DATABASE

DATABASE = "./database/jobs.db"

def create_table():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cmd = f"""
    CREATE TABLE user (
        userid INTEGER UNIQUE,
        username TEXT,
        fullname TEXT,
        join_date TEXT,
        model_3d INTEGER DEFAULT 0,
        scraping INTEGER DEFAULT 0,
        music INTEGER DEFAULT 0,
        illustration INTEGER DEFAULT 0,
        nft INTEGER DEFAULT 0,
        python INTEGER DEFAULT 0
    )
    """
    cur.execute(cmd)
    con.commit()
    con.close()

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
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cmd = f"UPDATE user SET {key}={value} WHERE userid={userid}"
        cur.execute(cmd)
        con.commit()
    except: pass
    con.close()

if __name__ == "__main__":

    # test create table
    create_table("./database/jobs.db")