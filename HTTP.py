#!/usr/bin/env python
from flask import Flask
from flask import render_template, session, redirect, url_for, escape, request, make_response
from GoogleManagement import GoogleContacts
from Settings import Settings, Secret
from API import APIFunctions
from Config import Config
import logging
from logging.handlers import RotatingFileHandler
import gdata
import json
import os


class HTTPServer(object):
    def __init__(self):
        config = Config()
        section = config.GetOptionsFor("web")
        handler = RotatingFileHandler(section['logfile'], maxBytes=section['logfile_size'], backupCount=section['logfile_count'])
        handler.setLevel(logging.INFO)
        handler.setLevel(logging.WARNING)
        handler.setLevel(logging.CRITICAL)
        handler.setLevel(logging.DEBUG)
        self.app = Flask(__name__)
        # URL Rules
        self.app.add_url_rule('/', 'index', self.__indexPage__)
        self.app.add_url_rule('/api', 'api', methods=['POST'], view_func=self.__apiPage__)
        self.app.add_url_rule('/login', 'login', methods=['POST', 'GET'], view_func=self.__loginPage__)
        self.app.add_url_rule('/google', 'google', methods=['GET'], view_func=self.__googlePage__)
        self.app.add_url_rule('/settings', 'settings', methods=['GET'], view_func=self.__settingsPage__)
        self.app.add_url_rule('/logout', 'logout', methods=['GET'], view_func=self.__logoutPage__)
        # Global func for templates
        self.app.context_processor(self.__utilityProcessor__)
        # set the secret key.  keep this really secret:
        self.app.secret_key = '' # 32-bit
        self.GlobalSet = Settings(self.app.secret_key)
        self.app.logger.addHandler(handler)
        self.app.logger.warning('A warning occurred (%d apples)', 42)
        self.app.logger.error('An error occurred')
        self.app.logger.info('Info')
        self.app.debug = section['debug'] 
        self.app.testing = section['testing'] 
        self.app.run(host=section['host'], port=section['port'], threaded=True)


    def __indexPage__(self):
        if 'username' in session:
            return make_response(render_template('index.html'))
        return redirect(url_for('login'))

    def __apiPage__(self):
        if 'username' not in session:
            return "BadAuthentication", 401 #Unauthorized
        if request.json and request.json['ajax']:
            api = APIFunctions(self.GlobalSet)
            res = api.execute(request.json)
            if not res:
                return "Service error", 406 #Not Acceptable
            return res, 200

        return "Query isn't correct", 400 #Bad Request

    def __loginPage__(self):
        if request.method == 'POST':
            if (self.GlobalSet.CheckInternalAuth(request.form['username'], request.form['password'])):
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))
        return make_response(render_template('auth/login.html'))

    def __logoutPage__(self):
        session.pop('username', None)
        return redirect(url_for('index'))
    
    def __googlePage__(self):
        if 'username' in session:
            crypto = Secret(self.app.secret_key)
            try:
                client = GoogleContacts(crypto.GetEnCryptedSecret(self.GlobalSet.google_user), crypto.GetEnCryptedSecret(self.GlobalSet.google_password))
            except gdata.client.BadAuthentication:
                return redirect(url_for('Settings'))
            data = client.GetAllProfiles()
            return make_response(render_template('services/google/users.html', data=data))
        return redirect(url_for('login'))

    def __settingsPage__(self):
        if 'username' not in session:
            return redirect(url_for('login'))
        settings_type = request.args.get('type', '')
        if request.method == 'POST' and settings_type == 'google':
            google_user = request.form['googleadmin']
            google_password = request.form['googlepassword']

            if google_user == '' or google_password == '':
                return make_response(render_template('/settings', settings_type = settings_type, error = "Input isn't correct"))
            else:
                try:
                    client = GoogleContacts(google_user, google_password)
                except gdata.client.BadAuthentication:
                    return make_response(render_template('settings.html', settings_type = settings_type, error = "Invalid user credentials given."))
        
                crypto = Secret(app.secret_key)
                self.GlobalSet.SaveGoogleSettings(crypto.GetCryptedSecret(google_user), crypto.GetCryptedSecret(google_password));
                return redirect(url_for('Settings'))
        return make_response(render_template('settings.html', settings_type = settings_type, users=self.GlobalSet.InternalUsers, settings=self.GlobalSet))

    def __utilityProcessor__(self):
    # Google get photo profile callback
        def googleGetProfilePhoto(href):
            crypto = Secret(self.app.secret_key)
            client = GoogleContacts(crypto.GetEnCryptedSecret(self.GlobalSet.google_user), crypto.GetEnCryptedSecret(self.GlobalSet.google_password))
            link = client.GetProfilePhoto(href)
            if link == '404':
                return '/static/img/anonimous.jpg'
            return link
        return dict(googleGetProfilePhoto=googleGetProfilePhoto)
