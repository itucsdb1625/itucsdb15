from flask import Blueprint, render_template
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
from __main__ import app, get_allTweets
from datetime import datetime
import server
import random

notifications = Blueprint('notifications', __name__)



@notifications.route('/myprofile/deletenotification', methods = ['POST', 'GET'])
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

@notifications.route('/myprofile/likenotification', methods = ['POST', 'GET'])
def notification_like():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            time = datetime.now()
            time = time.replace(microsecond=0)
            idtoinsert = request.form['idtoinsert']
            query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (%s, %s, %s, %s, 'LIKE', '%s', 'UNSEEN')"""%(random.randint(1,1000000), server.current_user, server.current_user, idtoinsert, time)
            cursor.execute(query)

            cursor.execute("""SELECT * FROM TWEETS""")
            connection.commit()

    allTweets = get_allTweets()

    return render_template('tweetsPage.html', tweets = allTweets)


@notifications.route('/myprofile/retweetnotification', methods = ['POST', 'GET'])
def notification_retweet():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            time = datetime.now()
            time = time.replace(microsecond=0)
            idtoinsert = request.form['idtoinsert']
            query = """INSERT INTO NOTIFICATIONS (ID, RECEIVERID, FROMID, TWEETID, TYPE, TIME, STATUS) VALUES (%s, %s, %s, %s, 'RETWEET', '%s', 'UNSEEN')"""%(random.randint(1,1000000), server.current_user, server.current_user, idtoinsert, time)
            cursor.execute(query)

            cursor.execute("""SELECT * FROM TWEETS""")
            connection.commit()

    allTweets = get_allTweets()

    return render_template('tweetsPage.html', tweets = allTweets)


@notifications.route('/myprofile/updatenotification', methods = ['POST', 'GET'])
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