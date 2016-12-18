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
from __main__ import app, current_user
from datetime import datetime
import random


messages = Blueprint('messages', __name__)


@messages.route('/messages')
def messages_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT messages.id,U1.NAME,U1.LASTNAME,U2.NAME, U2.LASTNAME, messages.message,messages.timestamp
        FROM messages
        INNER JOIN USERS AS U1
        ON messages.fromuser=U1.ID
        INNER JOIN USERS AS U2
        ON messages.touser=U2.ID"""
        )
        messages_all = cursor.fetchall()
        connection.commit()
    return render_template('messages.html', messages = messages_all)

@messages.route('/messages/new', methods = ['POST', 'GET'])
def new_message_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute("""SELECT ID, NAME, LASTNAME FROM users"""
            )
            to_send = cursor.fetchall()
            connection.commit()

        return render_template('new_message.html', tosend = to_send)
    else:


        frm = current_user;
        to = request.form['to']
        msg = request.form['message']
        timestamp = datetime.now();

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO MESSAGES (FROMUSER, TOUSER, MESSAGE, TIMESTAMP) VALUES ('%s', '%s', '%s', %s)""" % (frm, to, msg, 0)
            cursor.execute(query)
            connection.commit()
        return redirect('/messages')

@messages.route('/messages/update/<int:message_id>', methods = ['POST', 'GET'])
def update_message_page(message_id):
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT U1.NAME, U1.LASTNAME, U2.NAME, U2.LASTNAME, messages.message FROM MESSAGES, USERS AS U1, USERS AS U2 WHERE (MESSAGES.ID=%s) AND (U1.ID=MESSAGES.FROMUSER) AND (U2.ID=MESSAGES.TOUSER)""" % (message_id)
            cursor.execute(query)
            message = cursor.fetchall()
            connection.commit()

        return render_template('update_message.html', messages = message)
    else:
        msg = request.form['message']
        timestamp = datetime.now();

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE MESSAGES SET MESSAGE='%s', TIMESTAMP=%s WHERE ID=%s""" % (msg, 0, message_id)
            cursor.execute(query)
            connection.commit()
        return redirect('/messages')

@messages.route('/messages/delete/<int:message_id>')
def delete_message_page(message_id):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """DELETE FROM MESSAGES WHERE ID=%s""" % (message_id)
        cursor.execute(query)
        connection.commit()
    return redirect('/messages')