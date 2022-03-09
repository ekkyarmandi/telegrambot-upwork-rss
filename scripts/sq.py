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
    try:
        cmd = f"CREATE TABLE {table_name} ({table_format(file_path)})"
        cur.execute(cmd)
        con.commit()
        print(f"New, {table_name} table created inside {DATABASE}")
    except:
        print(f"{table_name} table exists!")        
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
    if key == "3d": key = "model_3d"
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cur.execute(f"UPDATE user SET {key}={value} WHERE userid={userid}")
        con.commit()
    except: pass
    con.close()

def query_subscription(userid):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        keys = ["model_3d","scraping","music","illustration","nft","python"]
        select = ",".join(keys)
        cur.execute(f"SELECT {select} FROM user WHERE userid={userid}")
        results = cur.fetchall()
        values = {k:v for k,v in zip(keys,results[0])}
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
        keys = ["hash","title","description","link","budget","posted_on","category","tags","country","label"]
        select = ",".join(keys)
        cur.execute(f"SELECT {select} FROM job ORDER BY posted_on,label")
        results = cur.fetchall()
        values = [{k:v for k,v in zip(keys,result)} for result in results]
    except: values = None
    con.close()
    return values

def query_users():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT userid FROM user")
    data = cur.fetchall()
    con.close()
    return [u[0] for u in data]

def update_stream(**kwargs):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        keys = ",".join([str(k) for k in kwargs.keys()])
        values = [v for v in kwargs.values()]
        cur.execute(f"INSERT or IGNORE INTO stream({keys}) VALUES(?,?,?)",(values[0],values[1],values[2]))
        con.commit()
    except: pass
    con.close()

def query_stream(user_id,job_hash):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cur.execute(f"SELECT message_id FROM stream WHERE user_id='{user_id}' AND hash='{job_hash}'")
        data = cur.fetchone()
    except:
        data = None
    con.close()
    if data != None: return data[0]
    else: return data

def reset_stream():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("DELETE FROM stream")
    con.commit()
    con.close()

def delete_job(job_hash):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute(f"DELETE FROM job WHERE hash='{job_hash}'")
    con.commit()
    con.close()
    
if __name__ == "__main__":

    # test create table
    create_table('user','./database/user_table.txt')
    create_table('job','./database/job_table.txt')
    create_table('stream','./database/stream_table.txt')