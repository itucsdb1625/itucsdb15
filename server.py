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


def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/messages')
def messages_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM MESSAGES")
        messages_all = cursor.fetchall()
        connection.commit()
    return render_template('messages.html', messages = messages_all)

@app.route('/messages/new', methods = ['POST', 'GET'])
def new_message_page():
    if request.method == 'GET':
        return render_template('new_message.html')
    else:
        frm = request.form['from']
        to = request.form['to']
        msg = request.form['message']
        timestamp = datetime.now();

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO MESSAGES (FROMUSER, TOUSER, MESSAGE, TIMESTAMP) VALUES ('%s', '%s', '%s', %s)""" % (frm, to, msg, 0)
            cursor.execute(query)
            connection.commit()
        return redirect('/messages')


@app.route('/signup', methods = ['POST', 'GET'])
def page_signup():

    if request.method == 'POST':
       # if request.type['submit'] == 'register':
            idr = random.randint(1,1000000)
            eml = request.form['email']
            nm = request.form['firstname']
            lstnm = request.form['lastname']
            phnm =  request.form['phonenumber']
            pssw = request.form['password']
            gndr = request.form['gender']

            with dbapi2.connect(app.config['dsn']) as connection:
                 cursor = connection.cursor()

                 #query = "UPDATE COUNTER SET N = N + 1"
                 #cursor.execute(query)

                 query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER)
                        VALUES
                        (%s,'%s', '%s', '%s', '%s', '%s', '%s')""" % (idr,eml,nm,lstnm,phnm,pssw,gndr)
                 cursor.execute(query)


                 connection.commit()

            return render_template('page_signup.html')

    elif request.method == 'GET':

        return render_template('page_signup.html')



@app.route('/adminuser', methods = ['POST', 'GET'])
def page_adminuser():
 
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor() 
        if request.method == 'GET':    
            cursor.execute("SELECT * FROM USERS")
            allusers = cursor.fetchall()
            connection.commit()
    return render_template('page_useradmin.html',users = allusers)

@app.route('/adminuser/deleteuser', methods = ['POST', 'GET'])
def user_delete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtodelete = request.form['idtodelete']
            query = """DELETE FROM USERS WHERE ID=%s""" % (idtodelete)
            cursor.execute(query)
          
            cursor.execute("SELECT * FROM USERS")
            allusers = cursor.fetchall()
            connection.commit()
    return redirect(url_for('page_adminuser',users = allusers))



@app.route('/adminuser/updateuser', methods = ['POST', 'GET'])
def page_updateuser():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
           
            idr = request.form['id']
            eml = request.form['email']
            nm = request.form['firstname']
            lstnm = request.form['lastname']
            phnm =  request.form['phonenumber']
            pssw = request.form['password']
            gndr = request.form['gender']
            
            
            query = """UPDATE USERS SET id=%s,email='%s',name='%s',lastname='%s',phonenumber='%s',password='%s',gender='%s'
            WHERE id=%s;
            """ % (idr,eml,nm,lstnm,phnm,pssw,gndr,idr)
            cursor.execute(query)
            connection.commit()        
            cursor.execute("SELECT * FROM USERS")
            allusers = cursor.fetchall()
            connection.commit()
            return redirect(url_for('page_adminuser',users = allusers))

        elif request.method == 'GET':

            return render_template('page_updateuser.html')


@app.route('/adminuser/selectuser', methods = ['POST', 'GET'])
def user_select():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtoselect = request.form['idtoselect']
            query = """SELECT * FROM USERS WHERE ID=%s""" % (idtoselect)
            cursor.execute(query)
            allusers = cursor.fetchall()
            connection.commit()
    return render_template('page_updateuser.html',users = allusers)


@app.route('/myprofile')
def profile_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM NOTIFICATIONS")
        notifications_all = cursor.fetchall()
        connection.commit()
    return render_template('samplecommit4.html', notifications = notifications_all)

@app.route('/myprofile/deletenotification', methods = ['POST', 'GET'])
def notification_delete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            query = """DELETE FROM NOTIFICATIONS""" 
            cursor.execute(query)
          
            cursor.execute("SELECT * FROM NOTIFICATIONS")
            notifications_all = cursor.fetchall()
            connection.commit()
    return redirect(url_for('profile_page', notifications = notifications_all))
    
@app.route('/myprofile/updatenotification', methods = ['POST', 'GET'])
def notification_update():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtoupdate = request.form['idtoupdate']
            query = """UPDATE NOTIFICATIONS SET STATUS='SEEN' WHERE ID=%s;"""%(idtoupdate)
            cursor.execute(query)
         
            cursor.execute("SELECT * FROM NOTIFICATIONS")
            notifications_all = cursor.fetchall()
            connection.commit()
    return redirect(url_for('profile_page', notifications = notifications_all))

@app.route('/tweetsPage', methods=['GET', 'POST'])
def efe_page():
    if 'add_tweet' in request.form:
        content = str(request.form['CONTENT'])

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""INSERT INTO TWEETS (CONTENT) VALUES (%s)""", [content])

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

@app.route('/samplecommit5')
def kursat_page():
    return render_template('samplecommit5.html')

def get_allTweets():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM TWEETS")
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

        query = """DROP TABLE IF EXISTS MESSAGES"""
        cursor.execute(query)

        query = """CREATE TABLE MESSAGES (
        FROMUSER VARCHAR(80),
        TOUSER VARCHAR(80),
        MESSAGE TEXT,
        TIMESTAMP INTEGER)"""
        cursor.execute(query)
        
        query = """INSERT INTO MESSAGES (FROMUSER, TOUSER, MESSAGE, TIMESTAMP) VALUES ('Biri', 'Birine', 'Merhaba', 0)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS USERS"""
        cursor.execute(query)

        query = """CREATE TABLE USERS (
        ID SERIAL PRIMARY KEY,
        EMAIL VARCHAR(80),
        NAME VARCHAR(80),
        LASTNAME VARCHAR(80),
        PHONENUMBER VARCHAR(20),
        PASSWORD VARCHAR(80),
        GENDER VARCHAR(10)
          )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS TWEETS"""
        cursor.execute(query)

        query = """CREATE TABLE TWEETS (
        ID SERIAL NOT NULL,
        CONTENT VARCHAR(140),
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)

        query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER) VALUES (631212,'koksalb@itu.edu.tr','Berkay','Koksal','05385653858','parola123','Male')"""
        cursor.execute(query)

        query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER) VALUES (631378,'helvacie@itu.edu.tr','Efe','Helvaci','05442609613','efeparola','Male')"""
        cursor.execute(query)

        query = """INSERT INTO TWEETS (CONTENT) VALUES ('Hello, twitter!')"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS NOTIFICATIONS"""
        cursor.execute(query)

        query = """CREATE TABLE NOTIFICATIONS (
        ID SERIAL PRIMARY KEY,
        RECEIVERID SERIAL,
        FROMID SERIAL,
        TWEETID SERIAL,
        TYPE VARCHAR(40),
        TIME VARCHAR (80),
        STATUS VARCHAR(80)
         )
        """
        cursor.execute(query)

        query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (1000, 6312, 6213, 3455, 'LIKE', '30.10.2016, 01:12', 'UNSEEN')"""
        cursor.execute(query)

        query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (1001, 1234, 6213, 3406, 'LIKE', '1.11.2016, 01:03', 'UNSEEN')"""
        cursor.execute(query)
        
        query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (1002, 6312, 6213, 3434, 'LIKE', '1.11.2016, 01:04', 'UNSEEN')"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS FOLLOWERS"""
        cursor.execute(query)

        query = """CREATE TABLE FOLLOWERS (
        ID SERIAL PRIMARY KEY,
        FRIENDID SERIAL,
        FOLLOWBACK BOOLEAN)"""
        cursor.execute(query)

        query = """INSERT INTO FOLLOWERS (ID, FRIENDID,FOLLOWBACK) VALUES (6312, 6213,TRUE)"""
        cursor.execute(query)
        
        query = """DROP TABLE IF EXISTS FOLLOWING"""
        cursor.execute(query)
        query = """CREATE TABLE FOLLOWING (
        ID SERIAL PRIMARY KEY,
        FRIENDID SERIAL,
        FOLLOWING BOOLEAN)"""
        cursor.execute(query)

        query = """INSERT INTO FOLLOWING (ID, FRIENDID,FOLLOWBACK) VALUES (6312, 6213,TRUE)"""
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

    app.run(host='0.0.0.0', port=port, debug=debug)

