import json
import os
#import ibm_db
import re
import psycopg2 as dbapi2
from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for
from flask import Flask, render_template, request
import random
from datetime import datetime
app = Flask(__name__)

current_user = -1

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

def create_app():
    global app
    from messages import messages
    from userops import userops

    app.register_blueprint(messages)
    app.register_blueprint(userops)
    
    return app











@app.route('/myprofile/deletenotification', methods = ['POST', 'GET'])
def notification_delete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtodelete = request.form['idtodelete']
            query = """DELETE FROM NOTIFICATIONS WHERE ID=%s"""%idtodelete
            cursor.execute(query)

            cursor.execute("SELECT USERS.NAME, USERS.LASTNAME, TYPE, TIME, STATUS, NOTIFICATIONS.ID FROM NOTIFICATIONS,USERS WHERE (FROMID = USERS.ID)")
            notifications_all = cursor.fetchall()
            connection.commit()
    return redirect(url_for('profile_page', notifications = notifications_all))

@app.route('/myprofile/likenotification', methods = ['POST', 'GET'])
def notification_like():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            time = datetime.now()
            time = time.replace(microsecond=0)
            idtoinsert = request.form['idtoinsert']
            cursor.execute(query)
            query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (%s, 631212, 631212, %s, 'LIKE', '%s', 'UNSEEN')"""%(random.randint(1,1000000), idtoinsert, time)
            cursor.execute("""SELECT * FROM TWEETS""")
            connection.commit()

    allTweets = get_allTweets()

    return render_template('tweetsPage.html', tweets = allTweets)


@app.route('/myprofile/retweetnotification', methods = ['POST', 'GET'])
def notification_retweet():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            time = datetime.now()
            time = time.replace(microsecond=0)
            idtoinsert = request.form['idtoinsert']
            query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (%s, 631212, 631212, %s, 'RETWEET', '%s', 'UNSEEN')"""%(random.randint(1,1000000), idtoinsert, time)
            cursor.execute(query)

            cursor.execute("""SELECT * FROM TWEETS""")
            connection.commit()

    allTweets = get_allTweets()

    return render_template('tweetsPage.html', tweets = allTweets)
@app.route('/myprofile/updatenotification', methods = ['POST', 'GET'])
def notification_update():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtoupdate = request.form['idtoupdate']
            query = """UPDATE NOTIFICATIONS SET STATUS='SEEN' WHERE ID=%s"""%idtoupdate
            cursor.execute(query)

            cursor.execute("SELECT USERS.NAME, USERS.LASTNAME, TYPE, TIME, STATUS, NOTIFICATIONS.ID FROM NOTIFICATIONS,USERS WHERE (FROMID = USERS.ID)")
            notifications_all = cursor.fetchall()
            connection.commit()
    return redirect(url_for('profile_page', notifications = notifications_all))

@app.route('/tweetsPage', methods=['GET', 'POST'])
def efe_page():
    if 'add_tweet' in request.form:
        content = str(request.form['CONTENT'])

        if current_user != -1:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                cursor.execute("""INSERT INTO TWEETS (CONTENT, USER_ID) VALUES (%s, %s)""", [content, current_user])

                connection.commit()

    elif 'delete_tweet' in request.form:
        option = request.form['options']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""DELETE FROM TWEETS WHERE ID=%s""", option)

            connection.commit()

    elif 'update_tweet' in request.form:
        option = request.form['options']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""SELECT * FROM TWEETS WHERE ID=%s""", option)
            selectedTweets = cursor.fetchall()
            connection.commit()

            return render_template('update_tweet.html', tweets = selectedTweets)

    elif 'selected_update_tweet' in request.form:
        tweetID = request.form['id']
        newContent = request.form['content']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""UPDATE TWEETS SET CONTENT=%s WHERE id=%s""", (newContent, tweetID))
            connection.commit()

    allTweets = get_allTweets()

    return render_template('tweetsPage.html', tweets = allTweets)

@app.route('/followers', methods=['GET', 'POST'])
def followers_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        cursor.execute("""

        SELECT  USERS.NAME,USERS.LASTNAME
        FROM USERS
        WHERE 631212=USERS.ID """)
        followed = cursor.fetchall()
        cursor = connection.cursor()
        cursor.execute("""

        SELECT USERS.ID,USERS.NAME,USERS.LASTNAME
        FROM FOLLOWERS
        INNER JOIN USERS
        ON FOLLOWERS.FRIENDID=USERS.ID """)
        followers_all = cursor.fetchall()
        connection.commit()
    return render_template('followers.html', followers = followers_all,follow=followed)

@app.route('/followers/delete', methods = ['POST', 'GET'])
def followers_delete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtodelete = request.form['idtodelete']
            query = """DELETE FROM FOLLOWERS WHERE FRIENDID=%s""" % (idtodelete)
            cursor.execute(query)

            cursor.execute("""

        SELECT  USERS.NAME,USERS.LASTNAME
        FROM USERS

        WHERE 631212=USERS.ID """)
        followed = cursor.fetchall()
        cursor = connection.cursor()
        cursor.execute("""

        SELECT USERS.ID,USERS.NAME,USERS.LASTNAME
        FROM FOLLOWERS
        INNER JOIN USERS
        ON FOLLOWERS.FRIENDID=USERS.ID """)
        followers_all = cursor.fetchall()
        connection.commit()
    return redirect(url_for('followers_page', followers = followers_all,follow=followed))


@app.route('/followers/insert', methods = ['POST', 'GET'])
def followers_insert():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtoinsert= request.form['idtoinsert']
            query = """INSERT INTO FOLLOWERS VALUES(631212,%s) """ % (idtoinsert)
            cursor.execute(query)

            cursor.execute("""

        SELECT  USERS.NAME,USERS.LASTNAME
        FROM USERS

        WHERE 631212=USERS.ID """)
        followed = cursor.fetchall()
        cursor = connection.cursor()
        cursor.execute("""

        SELECT USERS.ID,USERS.NAME,USERS.LASTNAME
        FROM FOLLOWERS
        INNER JOIN USERS
        ON FOLLOWERS.FRIENDID=USERS.ID """)
        followers_all = cursor.fetchall()
        connection.commit()
    return redirect(url_for('followers_page', followers = followers_all,follow=followed))

@app.route('/following', methods=['GET', 'POST'])
def following_page():
    return render_template('following.html')

@app.route('/samplecommit5')
def kursat_page():
    return render_template('samplecommit5.html')

def get_allTweets():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        cursor.execute("(SELECT NAME, LASTNAME, CONTENT, TWEET_DATE, TWEETS.ID FROM TWEETS JOIN USERS ON (TWEETS.USER_ID = USERS.ID))")
        tweets = cursor.fetchall()

        connection.commit()

        return tweets

@app.route('/count')
def counter_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "UPDATE COUNTER SET N = N + 1"
        cursor.execute(query)
        connection.commit()

        query = "SELECT N FROM COUNTER"
        cursor.execute(query)
        count = cursor.fetchone()[0]
    return "This page was accessed %d times." % count


@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS COUNTER"""
        cursor.execute(query)

        query = """CREATE TABLE COUNTER (N INTEGER)"""
        cursor.execute(query)

        query = """INSERT INTO COUNTER (N) VALUES (0)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS MESSAGES CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE MESSAGES (
        ID SERIAL,
        FROMUSER SERIAL,
        TOUSER SERIAL,
        MESSAGE TEXT,
        TIMESTAMP INTEGER,
        FOREIGN KEY(FROMUSER) REFERENCES USERS(ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        FOREIGN KEY(TOUSER) REFERENCES USERS(ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE USERS (
        ID SERIAL PRIMARY KEY,
        EMAIL VARCHAR(80) UNIQUE,
        NAME VARCHAR(80),
        LASTNAME VARCHAR(80),
        PHONENUMBER VARCHAR(20),
        PASSWORD VARCHAR(80),
        GENDER VARCHAR(10)
          )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS TWEETS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE TWEETS (
        ID SERIAL NOT NULL,
        CONTENT VARCHAR(140),
        USER_ID SERIAL,
        TWEET_DATE DATE NOT NULL DEFAULT current_date,
        PRIMARY KEY(ID),
        FOREIGN KEY(USER_ID) REFERENCES USERS(ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )"""
        cursor.execute(query)

        query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER) VALUES (631212,'koksalb@itu.edu.tr','Berkay','Koksal','05385653858','parola123','Male')"""
        cursor.execute(query)

        query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER) VALUES (631378,'helvacie@itu.edu.tr','Efe','Helvaci','05442609613','efeparola','Male')"""
        cursor.execute(query)

        query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER) VALUES (631375,'yasarku@itu.edu.tr','kursat','yasar','05442609613','efeparola','Male')"""
        cursor.execute(query)

        query = """INSERT INTO TWEETS (CONTENT, USER_ID) VALUES ('Hello, twitter!', 631378)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS NOTIFICATIONS"""
        cursor.execute(query)

        query = """CREATE TABLE NOTIFICATIONS (
        ID SERIAL PRIMARY KEY,
        RECEIVERID SERIAL,
        FROMID SERIAL,
        TWEETID SERIAL,
        TYPE VARCHAR(40),
        TIME TEXT,
        STATUS VARCHAR(80),
        FOREIGN KEY (FROMID) REFERENCES USERS(ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE
         )
        """
        cursor.execute(query)
        time = datetime.now()
        time = time.replace(microsecond=0)
        query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (1000, 6312, 631212, 3455, 'LIKE', '%s', 'UNSEEN')"""%time
        cursor.execute(query)

        query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (1001, 1234, 631212, 3406, 'LIKE', '%s', 'UNSEEN')"""%time
        cursor.execute(query)

        query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (1002, 6312, 631212, 3434, 'LIKE', '%s', 'UNSEEN')"""%time
        cursor.execute(query)


        query = """DROP TABLE IF EXISTS FOLLOWERS"""
        cursor.execute(query)

        query = """CREATE TABLE FOLLOWERS (
        ID SERIAL,
        FRIENDID SERIAL)"""
        cursor.execute(query)

        query = """INSERT INTO FOLLOWERS (ID, FRIENDID) VALUES (631212, 631378)"""
        cursor.execute(query)
        query = """INSERT INTO FOLLOWERS (ID, FRIENDID) VALUES (631212, 631375)"""
        cursor.execute(query)
        query = """INSERT INTO FOLLOWERS (ID, FRIENDID) VALUES (6314, 6224)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS FOLLOWING"""
        cursor.execute(query)
        query = """CREATE TABLE FOLLOWING (
        ID SERIAL,
        FRIENDID SERIAL,
        FOLLOWBACK BOOLEAN,
        FOREIGN KEY(ID) REFERENCES USERS(ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE
            )
            """
        cursor.execute(query)

        query = """INSERT INTO FOLLOWING (ID, FRIENDID,FOLLOWBACK) VALUES (631212, 6213,TRUE)"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))

if __name__ == '__main__':

    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='hknbgryr' password='Yte_gcTO9oEeCFVM7dKv53djw8VnaJwP'
                               host='jumbo.db.elephantsql.com' port=5432 dbname='hknbgryr'"""

    apps = create_app()
    apps.run(host='0.0.0.0', port=port, debug=debug)

