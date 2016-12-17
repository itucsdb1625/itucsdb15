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


userops = Blueprint('userops', __name__)

@userops.route('/page_login')
def home_page():
    return render_template('home.html')

@userops.route('/', methods = ['POST', 'GET'])
def page_login():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            mailentered = request.form['usermail']
            passentered = request.form['userpass']
            query = """SELECT EMAIL,NAME,LastNAME,ID FROM USERS WHERE email='%s' AND password='%s' """ % (mailentered, passentered)
            cursor.execute(query)
            allusers = cursor.fetchall()
            global current_user
            for user in allusers:
                current_user = user[3]

            connection.commit()
            rowcounter = cursor.rowcount
            if rowcounter > 0:

                return render_template('page_profile_temp.html',users = allusers)
            else:
                 return render_template('loginpage.html')
        elif request.method == 'GET':
            return render_template('loginpage.html')




@userops.route('/signup', methods = ['POST', 'GET'])
def page_signup():
    if request.method == 'POST':
       # if request.type['submit'] == 'register':
            
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

                 query = """INSERT INTO USERS (EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER)
                        VALUES
                        ('%s', '%s', '%s', '%s', '%s', '%s')""" % (eml,nm,lstnm,phnm,pssw,gndr)
                 cursor.execute(query)


                 connection.commit()

            return render_template('page_signup.html')

    elif request.method == 'GET':

        return render_template('page_signup.html')



@userops.route('/adminuser', methods = ['POST', 'GET'])
def page_adminuser():

    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'GET':
            cursor.execute("SELECT ID,EMAIL,NAME,LASTNAME,PHONENUMBER,GENDER FROM USERS")
            allusers = cursor.fetchall()
            connection.commit()
    return render_template('page_useradmin.html',users = allusers)

@userops.route('/adminuser/deleteuser', methods = ['POST', 'GET'])
def user_delete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtodelete = request.form['idtodelete']
            query = """DELETE FROM USERS WHERE ID=%s""" % (idtodelete)
            cursor.execute(query)

            cursor.execute("SELECT ID,EMAIL,NAME,LASTNAME,PHONENUMBER,GENDER FROM USERS")
            allusers = cursor.fetchall()
            connection.commit()
    return redirect(url_for('page_adminuser',users = allusers))



@userops.route('/adminuser/updateuser', methods = ['POST', 'GET'])
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
            cursor.execute("SELECT ID,EMAIL,NAME,LASTNAME,PHONENUMBER,GENDER FROM USERS")
            allusers = cursor.fetchall()
            connection.commit()
            return redirect(url_for('page_adminuser',users = allusers))

        elif request.method == 'GET':

            return render_template('page_updateuser.html')


@userops.route('/adminuser/selectuser', methods = ['POST', 'GET'])
def user_select():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        if request.method == 'POST':
            idtoselect = request.form['idtoselect']
            query = """SELECT ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER FROM USERS WHERE ID=%s""" % (idtoselect)
            cursor.execute(query)
            allusers = cursor.fetchall()
            connection.commit()
    return render_template('page_updateuser.html',users = allusers)


@userops.route('/myprofile')
def profile_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT USERS.NAME, USERS.LASTNAME, TYPE, TIME, STATUS, NOTIFICATIONS.ID FROM NOTIFICATIONS,USERS WHERE (FROMID = USERS.ID)")
        notifications_all = cursor.fetchall()
        connection.commit()
    return render_template('samplecommit4.html', notifications = notifications_all)