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

tweets = Blueprint('tweets', __name__)

@tweets.route('/tweetsPage', methods=['GET', 'POST'])
def efe_page():
    if 'add_tweet' in request.form:
        content = str(request.form['CONTENT'])

        if server.current_user != -1:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                cursor.execute("""INSERT INTO TWEETS (CONTENT, USER_ID) VALUES (%s, %s)""", [content, server.current_user])

                connection.commit()
        else:
            print('Current user not found')


    elif 'delete_tweet' in request.form:
        option = request.form['options']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""SELECT USER_ID FROM TWEETS WHERE ID=%s""", option)
            tweet_owner = cursor.fetchall()

            if (tweet_owner[0])[0] == server.current_user or server.current_user == 999999:
                cursor.execute("""DELETE FROM TWEETS WHERE ID=%s""", option)

                connection.commit()

    elif 'update_tweet' in request.form:
        option = request.form['options']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""SELECT USER_ID FROM TWEETS WHERE ID=%s""", option)
            tweet_owner = cursor.fetchall()

            if (tweet_owner[0])[0] == server.current_user or server.current_user == 999999:

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
