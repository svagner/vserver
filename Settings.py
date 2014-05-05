import sqlite3
import hashlib
import base64
from Config import Config
from Crypto.Cipher import AES

class Settings(object):
    def __RestoreSettings(self, connector):
# Google
        dbcursor = connector.cursor()
        dbcursor.execute("select user,password from "+self.settingTable+" where service='google'") 
        rows = dbcursor.fetchone()
        crypto = Secret(self.secret)
        if rows:
            self.SaveGoogleSettings(rows[0], rows[1])
        dbcursor.execute("select login from "+self.IntAuthTable) 
        rows = dbcursor.fetchone()
        if not rows:
            t_sha = hashlib.sha512()
            t_sha.update("password"+self.secret)
            connector.execute("INSERT INTO "+self.IntAuthTable+" ('login', 'username', 'email', 'role', 'password') VALUES ('admin','Default user','None','admin','"+base64.urlsafe_b64encode(t_sha.digest())+"')")
            connector.commit()
            

    def __CreateSettingsTable(self, connector):
        connector.execute("CREATE TABLE IF NOT EXISTS "+self.settingTable+" (service text, parametrs text, user text, password)")
        connector.commit()

    def __CreateIntAuthTable(self, connector):
        connector.execute("CREATE TABLE IF NOT EXISTS "+self.IntAuthTable+" (login text, username text, email text, role text, password text)")
        connector.commit()

    def __RestoreIntAuthList(self, connector):
        dbcursor = connector.cursor()
        for row in dbcursor.execute('SELECT * FROM intauth ORDER BY login'):
            self.InternalUsers[row[0]] = { "username":row[1], "email": row[2], "role": row[3], "password": row[4] }

    def __init__(self, secret):
        self.google_user = ''
        self.google_password = ''
        self.secret = secret
        config = Config()
        dbconfig = config.GetOptionsFor("database")
        self.dbname = dbconfig["file"]
        self.settingTable = "settings"
        self.IntAuthTable = "intauth"
        self.InternalUsers = {} 
        connector = sqlite3.connect(self.dbname)
        self.__CreateSettingsTable(connector)
        self.__CreateIntAuthTable(connector)
        self.__RestoreSettings(connector)
        self.__RestoreIntAuthList(connector)
        connector.commit()
        connector.close()
    
    def SaveGoogleSettings(self, user, password):
        self.google_user = user
        self.google_password = password
        connector = sqlite3.connect(self.dbname)
        connector.execute("INSERT OR REPLACE INTO "+self.settingTable+" ('service', 'parametrs', 'user', 'password') VALUES ('google','none','"+self.google_user+"','"+self.google_password+"')")
        connector.commit()
        connector.close()

    def CheckInternalAuth(self, user, password):    
        connector = sqlite3.connect(self.dbname)
        dbcursor = connector.cursor()
        dbcursor.execute("select password,role from "+self.IntAuthTable+" where login='"+user+"'") 
        rows = dbcursor.fetchone()
        if rows:
            t_sha = hashlib.sha512()
            t_sha.update(password+self.secret)
            if base64.urlsafe_b64encode(t_sha.digest()) == rows[0]:
                return rows[1]
        return    

class Secret(object):
    def __init__(self, secret):
        if not secret:
            return
        PADDING = '{'
        BLOCK_SIZE = 32
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        self.secret = secret
        self.EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        self.DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

    def GetCryptedSecret(self, string):
        cipher = AES.new(self.secret)
        return self.EncodeAES(cipher, string)

    def GetEnCryptedSecret(self, string):
        cipher = AES.new(self.secret)
        return self.DecodeAES(cipher, string)
