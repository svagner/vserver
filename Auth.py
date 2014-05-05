import sqlite3
import hashlib
import base64
from Crypto.Cipher import AES
from Settings import Settings

class InternalAuth(object):
    def __init__(self, config):
        self.authTable = config.IntAuthTable
        self.secret = config.secret
        self.dbConnector = self.__GetConnectorToDB__(config.dbname); 
        self.UsersCache = config.InternalUsers

    def __GetConnectorToDB__(self, db):
        return sqlite3.connect(db)

    def AddUser(self, user):
        dbcursor = self.dbConnector.cursor()
        dbcursor.execute("select login from "+self.authTable+" where login='"+user['user_login']+"'");
        rows = dbcursor.fetchone()
        if rows:
            return
        t_sha = hashlib.sha512()
        t_sha.update(user['user_password']+self.secret)
        self.dbConnector.execute("INSERT INTO "+self.authTable+" ('login', 'username', 'email', 'role', 'password') VALUES ('"+user['user_login']+"','"+user['user_name']+"','"+user['email']+"','"+user['user_role']+"','"+base64.urlsafe_b64encode(t_sha.digest())+"')")
        res = self.dbConnector.commit()
        if not res:
            self.UsersCache[user['user_login']] = { "username": user['user_name'], "email": user['email'], "role": user['user_role'], "password": base64.urlsafe_b64encode(t_sha.digest()) }
        return res

    def DeleteUser(self, user):
        self.dbConnector.execute("delete from "+self.authTable+" where login='"+user['user_login']+"'");
        res = self.dbConnector.commit()
        if not res:
            del self.UsersCache[user['user_login']]
        return res

    def __delete__(self):
        return sqlite3.close(self.dbConnector)
