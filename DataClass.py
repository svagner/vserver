import sqlite3
from Crypto.Cipher import AES

class Database(object):
    def __CreateTables(self):
        self.connector.execute("CREATE TABLE IF NOT EXISTS "+self.settingTable+" (service text, parametrs text, user text, password)")
        self.connector.execute("CREATE TABLE IF NOT EXISTS "+self.intauthTable+" (login text, password text, name text, email text, role text, password text)")
        self.connector.commit()

    def __init__(self, dbtype, database):
        if not dbtype or dbtype != 'sqlite':
            return
        self.connector = sqlite3.connect(database)
        self.settingTable = "settings"
        self.authTable = "intauth"
        self.__CreateTables()

    def SaveServiceSettings(self, parametrs, user, password):
        if not service or not parametrs or not auth:
            return False
        self.connector.execute("INSERT INTO "+self.settingTable+" VALUES ("+service+","+parametrs+","+user+","+password+")")
        self.connect.commit()
        return True

    def __del__(self):
        self.connector.close()

class Secret(object):
    def __init__(self, secret):
        if not secret:
            return
        self.secret = secret

    def GetCryptedSecret(self, string):
        cipher = AES.new(self.secret)
        return EncodeAES(cipher, string)

    def GetEnCryptedSecret(self, string):
        cipher = AES.new(self.secret)
        return DecodeAES(cipher, string)
